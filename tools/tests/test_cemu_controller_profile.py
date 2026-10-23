import os
import subprocess
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "linuxfs/overlay/usr/local/bin/droiddeck-pad-defaults"


class CemuControllerProfileTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.config = self.root / ".config"
        self.profile = self.config / "Cemu/controllerProfiles/controller0.xml"

    def run_defaults(self, mode):
        env = dict(os.environ, HOME=str(self.root), XDG_CONFIG_HOME=str(self.config))
        if mode is None:
            env.pop("DROIDDECK_CEMU_PRO_CONTROLLER", None)
        else:
            env["DROIDDECK_CEMU_PRO_CONTROLLER"] = mode
        subprocess.run([str(SCRIPT)], env=env, check=True, capture_output=True, text=True)
        return ET.parse(self.profile).getroot()

    def mapping(self, root):
        return {int(entry.findtext("mapping")): int(entry.findtext("button"))
                for entry in root.findall("./controller/mappings/entry")}

    def test_mode_switch_reseeds_profile_with_expected_mappings(self):
        pro = self.run_defaults("1")
        self.assertEqual(pro.findtext("type"), "Wii U Pro Controller")
        self.assertEqual(pro.findtext("./controller/uuid"), "0_03005e615e0400008e02000010010000")
        self.assertEqual(pro.findtext("./controller/display_name"), "Xbox 360 Controller (0)")
        self.assertEqual(self.mapping(pro), {
            1: 1, 2: 0, 3: 3, 4: 2, 5: 9, 6: 10, 7: 42, 8: 43, 9: 6, 10: 4,
            11: 5, 12: 11, 13: 12, 14: 13, 15: 14, 16: 7, 17: 8, 18: 44, 19: 39,
            20: 38, 21: 45, 22: 47, 23: 41, 24: 40, 25: 46,
        })

        gamepad = self.run_defaults("0")
        self.assertEqual(gamepad.findtext("type"), "Wii U GamePad")
        self.assertEqual(gamepad.findtext("./controller/uuid"), "0_03005e615e0400008e02000010010000")
        self.assertEqual(gamepad.findtext("./controller/display_name"), "Xbox 360 Controller (0)")
        self.assertEqual(self.mapping(gamepad), {
            1: 1, 2: 0, 3: 3, 4: 2, 5: 9, 6: 10, 7: 42, 8: 43, 9: 6, 10: 4,
            11: 11, 12: 12, 13: 13, 14: 14, 15: 7, 16: 8, 17: 45, 18: 39,
            19: 44, 20: 38, 21: 47, 22: 41, 23: 46, 24: 40, 27: 5,
        })

    def test_environment_override_precedes_saved_preference(self):
        preference = self.config / "Cemu/.droiddeck-controller-pref"
        preference.parent.mkdir(parents=True)
        preference.write_text("gamepad\n")
        self.assertEqual(self.run_defaults("1").findtext("type"), "Wii U Pro Controller")

    def test_saved_preference_is_used_without_environment_override(self):
        preference = self.config / "Cemu/.droiddeck-controller-pref"
        preference.parent.mkdir(parents=True)
        preference.write_text("pro\n")
        self.assertEqual(self.run_defaults(None).findtext("type"), "Wii U Pro Controller")

    def test_default_profile_is_wii_u_gamepad(self):
        self.assertEqual(self.run_defaults(None).findtext("type"), "Wii U GamePad")


if __name__ == "__main__":
    unittest.main()