#!/usr/bin/env bash
set -euo pipefail

if ! command -v unzip >/dev/null 2>&1 || ! command -v zstd >/dev/null 2>&1 \
    || ! command -v gawk >/dev/null 2>&1; then
    sudo apt-get update
    sudo apt-get install -y --no-install-recommends unzip zstd gawk
fi

sdk_root="${ANDROID_HOME:-${HOME}/Android/Sdk}"
cmdline_tools_version=13114758
cmdline_tools="${sdk_root}/cmdline-tools/latest/bin/sdkmanager"

if [[ ! -x "${cmdline_tools}" ]]; then
    archive=$(mktemp "${TMPDIR:-/tmp}/android-cmdline-tools.XXXXXX.zip")
    trap 'rm -f "${archive}"' EXIT
    mkdir -p "${sdk_root}/cmdline-tools"
    curl -fsSL --retry 3 \
        "https://dl.google.com/android/repository/commandlinetools-linux-${cmdline_tools_version}_latest.zip" \
        -o "${archive}"
    unzip -q "${archive}" -d "${sdk_root}/cmdline-tools"
    rm -rf "${sdk_root}/cmdline-tools/latest"
    mv "${sdk_root}/cmdline-tools/cmdline-tools" "${sdk_root}/cmdline-tools/latest"
fi

export ANDROID_HOME="${sdk_root}"
export ANDROID_SDK_ROOT="${sdk_root}"
export PATH="${sdk_root}/cmdline-tools/latest/bin:${sdk_root}/platform-tools:${HOME}/.cargo/bin:${PATH}"

env_file="${HOME}/.config/droiddeck/android-env.sh"
mkdir -p "$(dirname "${env_file}")"
cat > "${env_file}" <<EOF
export ANDROID_HOME="${sdk_root}"
export ANDROID_SDK_ROOT="${sdk_root}"
export PATH="${sdk_root}/cmdline-tools/latest/bin:${sdk_root}/platform-tools:\${HOME}/.cargo/bin:\${PATH}"
EOF
for profile in "${HOME}/.bashrc" "${HOME}/.profile"; do
    if ! grep -Fq "${env_file}" "${profile}" 2>/dev/null; then
        printf '\n[ -f "%s" ] && . "%s"\n' "${env_file}" "${env_file}" >> "${profile}"
    fi
done

(set +o pipefail; yes | sdkmanager --sdk_root="${sdk_root}" --licenses >/dev/null)
sdkmanager --sdk_root="${sdk_root}" \
    'platform-tools' \
    'platforms;android-34' \
    'build-tools;35.0.0' \
    'ndk;27.3.13750724'

rustup target add --toolchain stable aarch64-linux-android
if ! cargo ndk --version >/dev/null 2>&1; then
    cargo install cargo-ndk --locked
fi
