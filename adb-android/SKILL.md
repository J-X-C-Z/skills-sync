---
name: adb-android
description: Operate and debug Android devices using this Windows computer's ADB and adb MCP. Use for device discovery, screenshots, UI interaction, APK installation, logcat, shell diagnostics, and USB or wireless debugging.
---

# Android device tools

Use the `adb` MCP server for device discovery, screenshots, UI hierarchy, interaction, app lifecycle, file transfer, and logs. Read its `android://guide/driving` resource for extended UI work when available. Use direct ADB for commands the MCP does not expose.

## This computer

- ADB: `C:/Users/Jxcz2/Agent/aurora-android/tools/android-sdk/platform-tools/adb.exe`
- SDK: `C:/Users/Jxcz2/Agent/aurora-android/tools/android-sdk`
- MCP executable: `C:/Users/Jxcz2/.local/share/adb-mcp/adb-mcp.exe`
- MCP is registered globally in Codex as `adb`, using an explicit SDK path.

Discover devices at the start of the task with MCP `list_devices` or `adb devices -l`. Device serials and authorization change; never reuse a remembered serial without checking it. Pass `serial` to device-facing MCP tools or `-s <serial>` to direct ADB. With multiple plausible devices, identify the intended device before acting.

For `unauthorized`, ask the user to unlock the phone and accept its USB debugging prompt. For `offline`, check the cable/connection first. Avoid restarting the shared ADB server unless needed, since other Android sessions use it. Wireless debugging needs a user-supplied current pairing address/code; do not expose ADB to public interfaces.

## UI and diagnostics

Observe with `screenshot` and `describe_ui`, act on the actual UI, then observe again. UI hierarchy coordinates are device pixels; screenshots can be scaled. Prefer named elements over guessed coordinates. Do not install an accessibility bridge or change lock-screen credentials merely to enable routine automation.

Direct PowerShell examples (substitute the freshly discovered serial):

```powershell
$adb = 'C:/Users/Jxcz2/Agent/aurora-android/tools/android-sdk/platform-tools/adb.exe'
& $adb devices -l
& $adb -s <serial> shell getprop ro.product.model
& $adb -s <serial> logcat -d -t 200
& $adb -s <serial> install -r 'C:/absolute/path/app.apk'
```

APK installation must be requested or necessary for the authorized app task. Preserve app data: `install -r` retains data; do not use uninstall/clear-data as an install workaround without authorization. Likewise, confirm intended package and scope before destructive operations, flashing, reset, or credential changes. Read-only inspection and reversible actions within the user's request can proceed directly.

For raw screenshots, capture binary stdout via Python `subprocess.run([...,'exec-out','screencap','-p'], check=True, stdout=file)`; Windows PowerShell text redirection can corrupt PNG bytes. Use absolute host paths for push/pull and screenshot files. Keep screenshots and logs local unless sharing is requested; avoid including unrelated notifications, tokens, or private messages in reports.

Report actual evidence: server handshake/tool listing, device enumeration, and any real-device operation tested. A configured server alone does not establish that Codex has loaded its tools; a new chat or app restart may be needed after registration.
