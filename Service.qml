import QtQuick
import Qt.labs.platform 1.1 as Platform
import Quickshell
import Quickshell.Io
import Quickshell.Wayland

Item {
  id: root

  property var shell: null
  property var manifest: null
  property bool configLoaded: false
  property bool idleIntegrationEnabled: true
  property bool stayAwake: false
  property bool stayAwakeStateLoaded: false

  readonly property string pluginId: "dailen.omarchtober"
  readonly property string pluginDir: root.fromFileUrl(Qt.resolvedUrl("."))
  readonly property string launcherPath: pluginDir + "/scripts/launch-omarchtober"
  readonly property string integrationPath: pluginDir + "/scripts/idle-integration"
  readonly property string stayAwakeStateDir: Quickshell.env("HOME") + "/.local/state/omarchy/indicators"
  readonly property var idleConfig: shell && shell.shellConfig && shell.shellConfig.idle ? shell.shellConfig.idle : ({})
  readonly property int screensaverTimeout: {
    var value = Number(idleConfig.screensaver)
    return isFinite(value) && value >= 1 ? Math.round(value) : 150
  }
  readonly property bool automaticNightEnabled: configLoaded && idleIntegrationEnabled && stayAwakeStateLoaded && !stayAwake

  function fromFileUrl(url) {
    var path = String(url || "").replace(/^file:\/\//, "").replace(/\/$/, "")
    try { return decodeURIComponent(path) } catch (error) { return path }
  }

  function openControlRoom() {
    if (shell && typeof shell.summon === "function") {
      shell.summon(pluginId, "{}")
      return
    }
    Quickshell.execDetached(["omarchy-shell", "shell", "summon", pluginId, "{}"])
  }

  function launch(mode) {
    if (!pluginDir) return
    Quickshell.execDetached(["bash", launcherPath, mode])
  }

  function stop() {
    Quickshell.execDetached(["pkill", "-f", "[o]rg.omarchy.screensaver"])
  }

  function applyIdleIntegration(enabled) {
    if (pluginDir) Quickshell.execDetached(["bash", integrationPath, enabled ? "enable" : "disable"])
  }

  function loadConfig(raw) {
    var enabled = true
    try {
      var parsed = JSON.parse(raw)
      if (parsed.integration && parsed.integration.idleEnabled !== undefined)
        enabled = !!parsed.integration.idleEnabled
    } catch (error) {
      enabled = true
    }
    idleIntegrationEnabled = enabled
    configLoaded = true
    applyIdleIntegration(enabled)
  }

  function refreshStayAwakeState() {
    if (!stayAwakeProbe.running) stayAwakeProbe.running = true
  }

  FileView {
    id: configFile
    path: Quickshell.env("HOME") + "/.config/omarchtober/config.json"
    watchChanges: true
    printErrors: false
    onLoaded: root.loadConfig(text())
    onFileChanged: reload()
    onLoadFailed: root.loadConfig("{}")
  }

  IdleMonitor {
    enabled: root.automaticNightEnabled
    timeout: root.screensaverTimeout
    respectInhibitors: true
    onIsIdleChanged: {
      if (isIdle && root.automaticNightEnabled) root.launch("automatic")
    }
  }

  Process {
    id: stayAwakeProbe
    command: ["bash", "-c", "mkdir -p \"$HOME/.local/state/omarchy/indicators\"; [[ -f $HOME/.local/state/omarchy/indicators/stay-awake ]] && echo yes || echo no"]
    stdout: SplitParser {
      onRead: function(line) {
        root.stayAwake = String(line).trim() === "yes"
        root.stayAwakeStateLoaded = true
      }
    }
    onExited: function() { stayAwakeWatcher.reload() }
  }

  FileView {
    id: stayAwakeWatcher
    path: root.stayAwakeStateDir
    watchChanges: true
    printErrors: false
    onFileChanged: root.refreshStayAwakeState()
  }

  Platform.SystemTrayIcon {
    visible: true
    tooltip: "Omarchtober · click to configure · middle-click to haunt"
    icon.source: Qt.resolvedUrl("assets/tray.svg")
    menu: Platform.Menu {
      Platform.MenuItem { text: "Open Nightscape Control"; onTriggered: root.openControlRoom() }
      Platform.MenuItem { text: "Haunt Now"; onTriggered: root.launch("force") }
      Platform.MenuItem { text: "Return to Desktop"; onTriggered: root.stop() }
      Platform.MenuSeparator { }
      Platform.MenuItem { text: "Report Bug"; onTriggered: Qt.openUrlExternally("https://github.com/DailenG/omarchtober/issues") }
    }
    onActivated: function(reason) {
      if (reason === Platform.SystemTrayIcon.MiddleClick) root.launch("force")
      else if (reason === Platform.SystemTrayIcon.Trigger || reason === Platform.SystemTrayIcon.DoubleClick) root.openControlRoom()
    }
  }

  IpcHandler {
    target: "omarchtober"
    function configure(): void { root.openControlRoom() }
    function start(): void { root.launch("force") }
    function stop(): void { root.stop() }
    function pluginDirectory(): string { return root.pluginDir }
  }

  Component.onDestruction: {
    if (root.pluginDir) Quickshell.execDetached(["bash", root.integrationPath, "disable"])
  }
  Component.onCompleted: {
    configFile.reload()
    refreshStayAwakeState()
  }
}
