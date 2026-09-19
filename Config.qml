pragma ComponentBehavior: Bound
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import Quickshell
import Quickshell.Io
import Quickshell.Wayland

Item {
  id: root

  property var shell: null
  property var manifest: null
  property bool opened: false
  property bool directoryReady: false
  property string pendingSaveText: ""
  property string statusLine: "VISUAL COLLECTION READY"
  property var defaults: ({
    schemaVersion: 4,
    experience: {
      mode: "fun",
      scene: "rotation",
      enabledScenes: ["haunted_estate", "witching_woods", "pumpkin_hollow", "midnight_mausoleum"],
      rotationSeconds: 90
    },
    art: {
      theme: "moonlit",
      motion: 0.7,
      parallax: 0.55,
      effects: { mist: 0.7, flight: 0.6, lanterns: 0.65, lightning: 0.35 }
    },
    sound: { enabled: false, volume: 22, source: "procedural", mediaPath: "", wind: true, thunder: true, creatures: true },
    integration: { idleEnabled: true, exitOnPointerMotion: true }
  })
  property var config: clone(defaults)
  readonly property var scenes: [
    { key: "rotation", name: "THE COLLECTION", description: "Move through every enabled scene", file: "haunted-estate.webp" },
    { key: "haunted_estate", name: "HAUNTED ESTATE", description: "Victorian manor and moonlit graveyard", file: "haunted-estate.webp" },
    { key: "witching_woods", name: "WITCHING WOODS", description: "Lantern path through ancient trees", file: "witching-woods.webp" },
    { key: "pumpkin_hollow", name: "PUMPKIN HOLLOW", description: "Amber harvest village after dark", file: "pumpkin-hollow.webp" },
    { key: "midnight_mausoleum", name: "MIDNIGHT MAUSOLEUM", description: "Cypress avenue and reflecting pools", file: "midnight-mausoleum.webp" }
  ]
  readonly property var themes: [
    { key: "moonlit", name: "MOONLIT", color: "#b9acd3" },
    { key: "harvest", name: "HARVEST", color: "#d57b35" },
    { key: "spectral", name: "SPECTRAL", color: "#65c8b0" },
    { key: "midnight", name: "MIDNIGHT", color: "#718cd6" }
  ]

  readonly property string pluginId: "dailen.omarchtober"
  readonly property string pluginDir: fromFileUrl(Qt.resolvedUrl("."))
  readonly property string configDir: Quickshell.env("HOME") + "/.config/omarchtober"
  readonly property string configPath: configDir + "/config.json"
  readonly property string launcherPath: pluginDir + "/scripts/launch-omarchtober"
  readonly property string selectorPath: pluginDir + "/scripts/select-media"
  readonly property color accent: themeColor(config.art.theme)

  function fromFileUrl(url) {
    var path = String(url || "").replace(/^file:\/\//, "").replace(/\/$/, "")
    try { return decodeURIComponent(path) } catch (error) { return path }
  }
  function clone(value) { return JSON.parse(JSON.stringify(value)) }
  function clamp(value, minimum, maximum, fallback) {
    var number = Number(value)
    if (!isFinite(number)) number = fallback
    return Math.max(minimum, Math.min(maximum, number))
  }
  function knownScene(key) {
    for (var i = 0; i < scenes.length; i++) if (scenes[i].key === key) return true
    return false
  }
  function knownTheme(key) {
    for (var i = 0; i < themes.length; i++) if (themes[i].key === key) return true
    return false
  }
  function themeColor(key) {
    for (var i = 0; i < themes.length; i++) if (themes[i].key === key) return themes[i].color
    return themes[0].color
  }
  function sceneFile(key) {
    for (var i = 0; i < scenes.length; i++) if (scenes[i].key === key) return scenes[i].file
    return scenes[0].file
  }
  function alphaColor(value, opacity) { return Qt.rgba(value.r, value.g, value.b, opacity) }
  function normalise(raw) {
    var incoming = raw && typeof raw === "object" ? raw : ({})
    if (incoming.schemaVersion !== 2 && incoming.schemaVersion !== 3 && incoming.schemaVersion !== 4) incoming = ({})
    var next = clone(defaults)
    var experience = incoming.experience && typeof incoming.experience === "object" ? incoming.experience : ({})
    next.experience.mode = experience.mode === "scary" ? "scary" : "fun"
    var scene = String(experience.scene || defaults.experience.scene)
    next.experience.scene = knownScene(scene) ? scene : defaults.experience.scene
    if (Array.isArray(experience.enabledScenes)) {
      var enabled = []
      for (var i = 0; i < experience.enabledScenes.length; i++) {
        var key = String(experience.enabledScenes[i])
        if (knownScene(key) && key !== "rotation" && enabled.indexOf(key) < 0) enabled.push(key)
      }
      if (enabled.length) next.experience.enabledScenes = enabled
    }
    next.experience.rotationSeconds = Math.round(clamp(experience.rotationSeconds, 15, 900, defaults.experience.rotationSeconds))
    var art = incoming.art && typeof incoming.art === "object" ? incoming.art : ({})
    var theme = String(art.theme || defaults.art.theme)
    next.art.theme = knownTheme(theme) ? theme : defaults.art.theme
    next.art.motion = Math.round(clamp(art.motion, 0, 2, defaults.art.motion) * 100) / 100
    next.art.parallax = Math.round(clamp(art.parallax, 0, 2, defaults.art.parallax) * 100) / 100
    var effects = art.effects && typeof art.effects === "object" ? art.effects : ({})
    next.art.effects.mist = Math.round(clamp(effects.mist, 0, 2, defaults.art.effects.mist) * 100) / 100
    next.art.effects.flight = Math.round(clamp(effects.flight, 0, 2, defaults.art.effects.flight) * 100) / 100
    next.art.effects.lanterns = Math.round(clamp(effects.lanterns, 0, 2, defaults.art.effects.lanterns) * 100) / 100
    next.art.effects.lightning = Math.round(clamp(effects.lightning, 0, 2, defaults.art.effects.lightning) * 100) / 100
    var sound = incoming.sound && typeof incoming.sound === "object" ? incoming.sound : ({})
    next.sound.enabled = typeof sound.enabled === "boolean" ? sound.enabled : defaults.sound.enabled
    next.sound.volume = Math.round(clamp(sound.volume, 0, 100, defaults.sound.volume))
    next.sound.source = sound.source === "media" ? "media" : "procedural"
    next.sound.mediaPath = typeof sound.mediaPath === "string" && sound.mediaPath.length <= 4096 ? sound.mediaPath : ""
    for (var s = 0; s < 3; s++) {
      var layer = ["wind", "thunder", "creatures"][s]
      next.sound[layer] = typeof sound[layer] === "boolean" ? sound[layer] : defaults.sound[layer]
    }
    var integration = incoming.integration && typeof incoming.integration === "object" ? incoming.integration : ({})
    next.integration.idleEnabled = typeof integration.idleEnabled === "boolean" ? integration.idleEnabled : defaults.integration.idleEnabled
    next.integration.exitOnPointerMotion = typeof integration.exitOnPointerMotion === "boolean" ? integration.exitOnPointerMotion : defaults.integration.exitOnPointerMotion
    return next
  }
  function persist() {
    pendingSaveText = JSON.stringify(normalise(config), null, 2) + "\n"
    statusLine = "SAVING VISUAL COLLECTION..."
    if (!directoryReady) {
      if (!ensureDir.running) ensureDir.running = true
      return
    }
    configFile.setText(pendingSaveText)
    pendingSaveText = ""
    statusLine = "VISUAL COLLECTION READY"
  }
  function updateConfig(callback) {
    var next = clone(config)
    callback(next)
    config = normalise(next)
    persist()
  }
  function open(payloadJson) {
    opened = true
    statusLine = "LOADING VISUAL COLLECTION..."
    if (!ensureDir.running) ensureDir.running = true
    configFile.reload()
    Qt.callLater(function() { keyCatcher.forceActiveFocus() })
  }
  function close() { opened = false }
  function dismiss() {
    opened = false
    if (shell && typeof shell.hide === "function") shell.hide(pluginId)
  }
  function launch() {
    persist()
    dismiss()
    Quickshell.execDetached(["bash", launcherPath, "force"])
  }
  function stop() {
    Quickshell.execDetached(["pkill", "-f", "[o]rg.omarchy.screensaver"])
    statusLine = "RETURN TO DESKTOP REQUESTED"
  }
  function chooseMedia() {
    if (!mediaPicker.running) {
      mediaPicker.command = [selectorPath, config.sound.mediaPath]
      mediaPicker.running = true
    }
  }
  function restoreDefaults() {
    config = clone(defaults)
    persist()
  }

  Process {
    id: ensureDir
    command: ["mkdir", "-p", root.configDir]
    onExited: function(exitCode) {
      root.directoryReady = exitCode === 0
      if (root.directoryReady && root.pendingSaveText) root.persist()
    }
  }
  Process {
    id: mediaPicker
    stdout: StdioCollector {
      waitForEnd: true
      onStreamFinished: {
        var selected = String(text || "").replace(/\n+$/, "")
        if (selected) root.updateConfig(function(next) { next.sound.mediaPath = selected; next.sound.source = "media" })
      }
    }
  }
  FileView {
    id: configFile
    path: root.configPath
    atomicWrites: true
    printErrors: false
    onLoaded: {
      try { root.config = root.normalise(JSON.parse(text())); root.statusLine = "VISUAL COLLECTION READY" }
      catch (error) { root.config = root.clone(root.defaults); root.statusLine = "SAFE DEFAULTS ACTIVE" }
    }
    onLoadFailed: { root.config = root.clone(root.defaults); root.statusLine = "NEW VISUAL COLLECTION" }
  }
  Component.onCompleted: if (!ensureDir.running) ensureDir.running = true

  component PillButton: Button {
    id: pill
    property bool primary: false
    implicitHeight: 30
    padding: 12
    font.pixelSize: 11
    font.bold: true
    font.letterSpacing: 1.4
    contentItem: Label {
      text: pill.text
      font: pill.font
      color: pill.primary ? "#0a0b16" : "#d8d3e4"
      horizontalAlignment: Text.AlignHCenter
      verticalAlignment: Text.AlignVCenter
    }
    background: Rectangle {
      radius: 15
      color: pill.primary
        ? (pill.down ? Qt.darker(root.accent, 1.2) : root.accent)
        : (pill.down ? root.alphaColor(root.accent, 0.26) : "#141527")
      border.width: 1
      border.color: pill.primary ? root.accent : (pill.hovered ? root.alphaColor(root.accent, 0.55) : "#2c2d42")
    }
  }

  component ChoiceButton: Button {
    id: choice
    property bool active: false
    implicitHeight: 30
    font.pixelSize: 11
    font.bold: true
    font.letterSpacing: 1.6
    contentItem: Label {
      text: choice.text
      font: choice.font
      color: choice.active ? "#fffaf0" : "#8f8ba1"
      horizontalAlignment: Text.AlignHCenter
      verticalAlignment: Text.AlignVCenter
    }
    background: Rectangle {
      radius: 9
      color: choice.active ? root.alphaColor(root.accent, 0.24) : (choice.down ? "#1a1b2f" : "#111222")
      border.width: 1
      border.color: choice.active ? root.accent : (choice.hovered ? "#3b3c56" : "#292a3d")
    }
  }

  component DarkCheckBox: CheckBox {
    id: box
    font.pixelSize: 11
    indicator: Rectangle {
      implicitWidth: 16
      implicitHeight: 16
      x: box.leftPadding
      y: (box.height - height) / 2
      radius: 4
      color: box.checked ? root.accent : "#111222"
      border.width: 1
      border.color: box.checked ? root.accent : "#3b3c56"
      Label {
        anchors.centerIn: parent
        visible: box.checked
        text: "✓"
        color: "#0a0b16"
        font.pixelSize: 11
        font.bold: true
      }
    }
    contentItem: Label {
      text: box.text
      font: box.font
      color: "#c9c4d8"
      leftPadding: box.indicator.width + 8
      verticalAlignment: Text.AlignVCenter
    }
  }

  component DarkSlider: Slider {
    id: bar
    implicitHeight: 22
    background: Rectangle {
      x: bar.leftPadding
      y: bar.topPadding + (bar.availableHeight - height) / 2
      width: bar.availableWidth
      height: 4
      radius: 2
      color: "#26273a"
      Rectangle {
        width: bar.visualPosition * parent.width
        height: parent.height
        radius: 2
        color: root.accent
      }
    }
    handle: Rectangle {
      x: bar.leftPadding + bar.visualPosition * (bar.availableWidth - width)
      y: bar.topPadding + (bar.availableHeight - height) / 2
      width: 14
      height: 14
      radius: 7
      color: bar.pressed ? Qt.lighter(root.accent, 1.15) : "#f0edf7"
      border.width: 1
      border.color: root.accent
    }
  }

  PanelWindow {
    id: panel
    visible: root.opened
    anchors { top: true; bottom: true; left: true; right: true }
    color: "transparent"
    WlrLayershell.namespace: "omarchtober-control-room"
    WlrLayershell.layer: WlrLayer.Overlay
    WlrLayershell.keyboardFocus: WlrKeyboardFocus.Exclusive
    exclusionMode: ExclusionMode.Ignore

    Rectangle {
      anchors.fill: parent
      color: "#b8040610"
      MouseArea { anchors.fill: parent; onClicked: root.dismiss() }
    }

    Rectangle {
      anchors.centerIn: parent
      width: Math.min(parent.width - 48, 1120)
      height: Math.min(parent.height - 48, 800)
      radius: 18
      color: "#f20a0b18"
      border.color: root.alphaColor(root.accent, 0.45)
      border.width: 1
      clip: true

      ColumnLayout {
        anchors.fill: parent
        anchors.margins: 22
        spacing: 14

        RowLayout {
          Layout.fillWidth: true
          ColumnLayout {
            Layout.fillWidth: true
            spacing: 2
            Label { text: "OMARCHTOBER"; color: root.accent; font.pixelSize: 13; font.bold: true; font.letterSpacing: 3 }
            Label { text: "Living illustrated nights"; color: "#f0edf7"; font.pixelSize: 29; font.bold: true }
            Label { text: root.statusLine; color: "#817d94"; font.pixelSize: 11; font.family: "monospace" }
          }
          PillButton { text: "RESTORE DEFAULTS"; onClicked: root.restoreDefaults() }
          PillButton { text: "CLOSE"; onClicked: root.dismiss() }
        }

        Rectangle {
          Layout.fillWidth: true
          Layout.preferredHeight: 175
          radius: 12
          color: "#060715"
          clip: true
          Image {
            anchors.fill: parent
            source: "file://" + root.pluginDir + "/assets/scenes/" + root.sceneFile(root.config.experience.scene)
            fillMode: Image.PreserveAspectCrop
            smooth: true
            mipmap: true
          }
          Rectangle { anchors.fill: parent; color: "#30000000" }
          Column {
            anchors.left: parent.left; anchors.bottom: parent.bottom; anchors.margins: 18; spacing: 3
            Label { text: root.config.experience.scene === "rotation" ? "THE COMPLETE COLLECTION" : root.config.experience.scene.replace(/_/g, " ").toUpperCase(); color: "#fffaf0"; font.pixelSize: 21; font.bold: true }
            Label { text: "GPU-rendered illustrated scenes · subtle motion · multi-monitor"; color: "#d0c9db"; font.pixelSize: 12 }
          }
        }

        Label { text: "SCENE"; color: root.accent; font.pixelSize: 12; font.bold: true; font.letterSpacing: 2 }
        Flow {
          Layout.fillWidth: true
          spacing: 8
          Repeater {
            model: root.scenes
            delegate: Rectangle {
              id: sceneCard
              required property var modelData
              width: 202; height: 66; radius: 9
              color: root.config.experience.scene === sceneCard.modelData.key ? root.alphaColor(root.accent, 0.20) : "#111222"
              border.color: root.config.experience.scene === sceneCard.modelData.key ? root.accent : "#292a3d"
              Column { anchors.fill: parent; anchors.margins: 10; spacing: 3
                Label { text: sceneCard.modelData.name; color: "#f0edf7"; font.pixelSize: 12; font.bold: true }
                Label { text: sceneCard.modelData.description; color: "#8f8ba1"; font.pixelSize: 10; width: 180; wrapMode: Text.WordWrap }
              }
              MouseArea { anchors.fill: parent; onClicked: root.updateConfig(function(next) { next.experience.scene = sceneCard.modelData.key }) }
            }
          }
        }

        Label { text: "THEME"; color: root.accent; font.pixelSize: 12; font.bold: true; font.letterSpacing: 2 }
        RowLayout {
          Layout.fillWidth: true
          Repeater {
            model: root.themes
            delegate: ChoiceButton {
              required property var modelData
              Layout.fillWidth: true
              text: modelData.name
              active: root.config.art.theme === modelData.key
              onClicked: root.updateConfig(function(next) { next.art.theme = modelData.key })
            }
          }
        }

        GridLayout {
          Layout.fillWidth: true
          columns: 2
          columnSpacing: 24
          rowSpacing: 8

          ColumnLayout {
            Layout.fillWidth: true
            Label { text: "MASTER MOTION · " + Number(root.config.art.motion).toFixed(2); color: "#d8d3e4"; font.pixelSize: 11; font.bold: true }
            DarkSlider { id: masterMotionSlider; Layout.fillWidth: true; from: 0; to: 2; value: root.config.art.motion; onMoved: root.updateConfig(function(next) { next.art.motion = masterMotionSlider.value }) }
          }
          ColumnLayout {
            Layout.fillWidth: true
            Label { text: "SCENE DURATION · " + root.config.experience.rotationSeconds + "s"; color: "#d8d3e4"; font.pixelSize: 11; font.bold: true }
            DarkSlider { id: durationSlider; Layout.fillWidth: true; from: 15; to: 300; stepSize: 15; value: root.config.experience.rotationSeconds; onMoved: root.updateConfig(function(next) { next.experience.rotationSeconds = durationSlider.value }) }
          }
          ColumnLayout {
            Layout.fillWidth: true
            Label { text: "PARALLAX DEPTH · " + Number(root.config.art.parallax).toFixed(2); color: "#d8d3e4"; font.pixelSize: 11; font.bold: true }
            DarkSlider { id: parallaxSlider; Layout.fillWidth: true; from: 0; to: 2; value: root.config.art.parallax; onMoved: root.updateConfig(function(next) { next.art.parallax = parallaxSlider.value }) }
          }
          ColumnLayout {
            Layout.fillWidth: true
            Label { text: "MIST LAYER · " + Number(root.config.art.effects.mist).toFixed(2); color: "#d8d3e4"; font.pixelSize: 11; font.bold: true }
            DarkSlider { id: mistSlider; Layout.fillWidth: true; from: 0; to: 2; value: root.config.art.effects.mist; onMoved: root.updateConfig(function(next) { next.art.effects.mist = mistSlider.value }) }
          }
          ColumnLayout {
            Layout.fillWidth: true
            Label { text: "SKY LIFE · " + Number(root.config.art.effects.flight).toFixed(2); color: "#d8d3e4"; font.pixelSize: 11; font.bold: true }
            DarkSlider { id: flightSlider; Layout.fillWidth: true; from: 0; to: 2; value: root.config.art.effects.flight; onMoved: root.updateConfig(function(next) { next.art.effects.flight = flightSlider.value }) }
          }
          ColumnLayout {
            Layout.fillWidth: true
            Label { text: "LANTERN MOTES · " + Number(root.config.art.effects.lanterns).toFixed(2); color: "#d8d3e4"; font.pixelSize: 11; font.bold: true }
            DarkSlider { id: lanternSlider; Layout.fillWidth: true; from: 0; to: 2; value: root.config.art.effects.lanterns; onMoved: root.updateConfig(function(next) { next.art.effects.lanterns = lanternSlider.value }) }
          }
          ColumnLayout {
            Layout.fillWidth: true
            Label { text: "STORM LIGHT · " + Number(root.config.art.effects.lightning).toFixed(2); color: "#d8d3e4"; font.pixelSize: 11; font.bold: true }
            DarkSlider { id: lightningSlider; Layout.fillWidth: true; from: 0; to: 2; value: root.config.art.effects.lightning; onMoved: root.updateConfig(function(next) { next.art.effects.lightning = lightningSlider.value }) }
          }
          RowLayout {
            Layout.fillWidth: true
            DarkCheckBox { text: "Automatic idle launch"; checked: root.config.integration.idleEnabled; onToggled: root.updateConfig(function(next) { next.integration.idleEnabled = checked }) }
            DarkCheckBox { text: "Exit on pointer motion"; checked: root.config.integration.exitOnPointerMotion; onToggled: root.updateConfig(function(next) { next.integration.exitOnPointerMotion = checked }) }
          }
          RowLayout {
            Layout.fillWidth: true
            DarkCheckBox { text: "Ambient sound"; checked: root.config.sound.enabled; onToggled: root.updateConfig(function(next) { next.sound.enabled = checked }) }
            PillButton { text: "SELECT LOCAL AUDIO"; onClicked: root.chooseMedia() }
          }
        }

        Item { Layout.fillHeight: true }
        RowLayout {
          Layout.fillWidth: true
          PillButton { text: "RETURN TO DESKTOP"; onClicked: root.stop() }
          Item { Layout.fillWidth: true }
          PillButton { text: "START VISUAL COLLECTION"; primary: true; onClicked: root.launch() }
        }
      }
    }

    Item { id: keyCatcher; anchors.fill: parent; focus: root.opened; Keys.onEscapePressed: root.dismiss() }
  }
}
