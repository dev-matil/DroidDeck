package com.droiddeck.launcher.frontend

import android.content.Context
import java.io.File
import java.security.MessageDigest

object CemuControllerPrefs {
    const val LAUNCHER_KEY = "cemu_pro_ctrl_launcher"
    private const val PREFS = "cemu_controller"

    fun gameKey(path: File): String {
        val stablePath = runCatching { path.canonicalPath }.getOrDefault(path.absolutePath)
        val digest = MessageDigest.getInstance("SHA-256").digest(stablePath.toByteArray())
        return "cemu_pro_ctrl_" + digest.joinToString("") { "%02x".format(it) }
    }

    fun get(context: Context, key: String): Boolean =
        context.getSharedPreferences(PREFS, Context.MODE_PRIVATE).getBoolean(key, false)

    fun set(context: Context, key: String, enabled: Boolean) {
        context.getSharedPreferences(PREFS, Context.MODE_PRIVATE).edit().putBoolean(key, enabled).apply()
    }
}