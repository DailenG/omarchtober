pragma ComponentBehavior: Bound
import QtQuick
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
  property string statusLine: "NIGHTSCAPE SYNCHRONIZED"
  property real previewPhase: 0
  property var defaults: ({
    schemaVersion: 1,
    experience: { mode: "fun", scene: "haunted_estate" },
    elements: { stars: 60, clouds: 4, bats: 12, gravestones: 14, apparitions: 4, wanderers: 3, pumpkins: 8, lightning: 25, animationSpeed: 1.0 },
    art: { palette: "moonlit", showStatus: false },
    sound: { enabled: false, volume: 22, source: "procedural", mediaPath: "", wind: true, thunder: true, creatures: true },
    integration: { idleEnabled: true, exitOnPointerMotion: true }
  })
  property var config: root.clone(defaults)
  property var scenes: [
    { key: "haunted_estate", name: "Haunted Estate", description: "Victorian manor, graveyard, bats, pumpkins, and wandering visitors." }
  ]
  readonly property var elementDefinitions: [
    { key: "stars", name: "TWINKLING STARS", description: "quiet points of shifting moonlight", step: 5, max: 160, accent: "#e6ddaf" },
    { key: "clouds", name: "MOVING CLOUDS", description: "slow layers crossing the full moon", step: 1, max: 12, accent: "#a69bb8" },
    { key: "bats", name: "FLYING BATS", description: "flapping silhouettes above the estate", step: 1, max: 40, accent: "#bd8ac7" },
    { key: "gravestones", name: "GRAVESTONES", description: "weathered markers across the foreground", step: 1, max: 36, accent: "#8ba39a" },
    { key: "apparitions", name: "EMERGING FIGURES", description: root.config.experience.mode === "fun" ? "friendly ghosts popping up to wave" : "skeletons rising between the stones", step: 1, max: 12, accent: "#90d9bd" },
    { key: "wanderers", name: "WANDERERS", description: root.config.experience.mode === "fun" ? "costumed trick-or-treaters on patrol" : "restless undead crossing the grounds", step: 1, max: 10, accent: "#e3af62" },
    { key: "pumpkins", name: "JACK-O'-LANTERNS", description: "flickering faces along the path", step: 1, max: 24, accent: "#f1873d" }
  ]
  readonly property var paletteDefinitions: [
    { key: "moonlit", label: "MOONLIT", accent: "#c4a3d2", deep: "#090818" },
    { key: "harvest", label: "HARVEST", accent: "#ef813c", deep: "#16080d" },
    { key: "spectral", label: "SPECTRAL", accent: "#68dbaa", deep: "#031011" },
    { key: "monochrome", label: "MONO", accent: "#bebec2", deep: "#080809" }
  ]
  readonly property string pluginId: "dailen.omarchtober"
  readonly property string pluginDir: root.fromFileUrl(Qt.resolvedUrl("."))
  readonly property string configDir: Quickshell.env("HOME") + "/.config/omarchtober"
  readonly property string configPath: configDir + "/config.json"
  readonly property string launcherPath: pluginDir + "/scripts/launch-omarchtober"
  readonly property string selectorPath: pluginDir + "/scripts/select-media"
  readonly property color accent: root.paletteValue("accent")
  readonly property color deep: root.paletteValue("deep")
  readonly property string fontFamily: "monospace"

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
  function paletteValue(key) {
    for (var i = 0; i < paletteDefinitions.length; i++)
      if (paletteDefinitions[i].key === config.art.palette) return paletteDefinitions[i][key]
    return paletteDefinitions[0][key]
  }
  function knownScene(key) {
    for (var i = 0; i < scenes.length; i++) if (scenes[i].key === key) return true
    return false
  }
  function normalise(raw) {
    var incoming = raw && typeof raw === "object" ? raw : ({})
    var next = clone(defaults)
    var experience = incoming.experience && typeof incoming.experience === "object" ? incoming.experience : ({})
    next.experience.mode = experience.mode === "scary" ? "scary" : "fun"
    var scene = String(experience.scene || defaults.experience.scene)
    next.experience.scene = knownScene(scene) ? scene : defaults.experience.scene
    var elements = incoming.elements && typeof incoming.elements === "object" ? incoming.elements : ({})
    for (var i = 0; i < elementDefinitions.length; i++) {
      var definition = elementDefinitions[i]
      next.elements[definition.key] = Math.round(clamp(elements[definition.key], 0, definition.max, defaults.elements[definition.key]))
    }
    next.elements.lightning = Math.round(clamp(elements.lightning, 0, 100, defaults.elements.lightning))
    next.elements.animationSpeed = Math.round(clamp(elements.animationSpeed, 0.25, 2.0, defaults.elements.animationSpeed) * 100) / 100
    var art = incoming.art && typeof incoming.art === "object" ? incoming.art : ({})
    var palette = String(art.palette || defaults.art.palette)
    var knownPalette = false
    for (var p = 0; p < paletteDefinitions.length; p++) if (paletteDefinitions[p].key === palette) knownPalette = true
    next.art.palette = knownPalette ? palette : defaults.art.palette
    next.art.showStatus = typeof art.showStatus === "boolean" ? art.showStatus : defaults.art.showStatus
    var sound = incoming.sound && typeof incoming.sound === "object" ? incoming.sound : ({})
    next.sound.enabled = typeof sound.enabled === "boolean" ? sound.enabled : defaults.sound.enabled
    next.sound.volume = Math.round(clamp(sound.volume, 0, 100, defaults.sound.volume))
    next.sound.source = sound.source === "media" ? "media" : "procedural"
    next.sound.mediaPath = typeof sound.mediaPath === "string" && sound.mediaPath.length <= 4096 ? sound.mediaPath : ""
    next.sound.wind = typeof sound.wind === "boolean" ? sound.wind : defaults.sound.wind
    next.sound.thunder = typeof sound.thunder === "boolean" ? sound.thunder : defaults.sound.thunder
    next.sound.creatures = typeof sound.creatures === "boolean" ? sound.creatures : defaults.sound.creatures
    var integration = incoming.integration && typeof incoming.integration === "object" ? incoming.integration : ({})
    next.integration.idleEnabled = typeof integration.idleEnabled === "boolean" ? integration.idleEnabled : defaults.integration.idleEnabled
    next.integration.exitOnPointerMotion = typeof integration.exitOnPointerMotion === "boolean" ? integration.exitOnPointerMotion : defaults.integration.exitOnPointerMotion
    return next
  }
  function finishDirectorySetup(exitCode) {
    directoryReady = exitCode === 0
    if (directoryReady && pendingSaveText) {
      configFile.setText(pendingSaveText)
      pendingSaveText = ""
      statusLine = "NIGHTSCAPE SYNCHRONIZED"
    }
  }
  function persist() {
    pendingSaveText = JSON.stringify(normalise(config), null, 2) + "\n"
    statusLine = "WRITING NIGHTSCAPE PARAMETERS..."
    if (!directoryReady) {
      if (!ensureDir.running) ensureDir.running = true
      return
    }
    configFile.setText(pendingSaveText)
    pendingSaveText = ""
    statusLine = "NIGHTSCAPE SYNCHRONIZED"
  }
  function mutate(section, key, value) {
    var next = clone(config)
    next[section][key] = value
    config = normalise(next)
    persist()
  }
  function changeElement(key, delta, maximum) {
    mutate("elements", key, Math.round(clamp(Number(config.elements[key] || 0) + delta, 0, maximum, 0)))
  }
  function restoreDefaults() {
    config = clone(defaults)
    statusLine = "FRIENDLY DEFAULT NIGHT RESTORED"
    persist()
  }
  function open(payloadJson) {
    opened = true
    statusLine = "READING NIGHTSCAPE PARAMETERS..."
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
    if (pluginDir) Quickshell.execDetached(["bash", launcherPath, "force"])
  }
  function stop() {
    Quickshell.execDetached(["pkill", "-f", "[o]rg.omarchy.screensaver"])
    statusLine = "RETURN TO DESKTOP REQUESTED"
  }
  function chooseMedia() {
    if (!pluginDir || mediaPicker.running) return
    statusLine = "OPENING MEDIA PICKER..."
    mediaPicker.command = [selectorPath, config.sound.mediaPath]
    mediaPicker.running = true
  }
  function testAudio() {
    if (!pluginDir || audioTest.running) return
    persist()
    statusLine = config.sound.source === "procedural" ? "AUDIO TEST · THREE TONES THEN AMBIENCE" : "TESTING SELECTED MEDIA"
    audioTest.command = ["python3", pluginDir + "/scripts/omarchtober.py", "--audio-test", "8"]
    audioTest.running = true
  }

  Process {
    id: ensureDir
    command: ["mkdir", "-p", root.configDir]
    onExited: function(exitCode) {
      if (exitCode === 0) secureDir.running = true
      else root.finishDirectorySetup(exitCode)
    }
  }
  Process {
    id: secureDir
    command: ["chmod", "700", root.configDir]
    onExited: function(exitCode) { root.finishDirectorySetup(exitCode) }
  }
  Process {
    id: audioTest
    onExited: function(exitCode) {
      root.statusLine = exitCode === 0 ? "AUDIO TEST COMPLETE" : "AUDIO TEST FAILED · RUN --audio-test FOR DETAILS"
    }
  }
  Process {
    id: mediaPicker
    stdout: StdioCollector {
      waitForEnd: true
      onStreamFinished: {
        var selected = String(text || "").replace(/\n+$/, "")
        if (selected) {
          var next = root.clone(root.config)
          next.sound.mediaPath = selected
          next.sound.source = "media"
          root.config = root.normalise(next)
          root.persist()
        }
      }
    }
    onExited: function(exitCode) {
      root.statusLine = exitCode === 0 ? "CUSTOM MEDIA SYNCHRONIZED" : "MEDIA PICKER CLOSED"
    }
  }
  FileView {
    id: defaultsFile
    path: root.pluginDir ? root.pluginDir + "/defaults.json" : ""
    printErrors: false
    onLoaded: {
      try { root.defaults = root.normalise(JSON.parse(text())) }
      catch (error) { console.warn("Omarchtober defaults parse failed:", error) }
    }
  }
  FileView {
    id: configFile
    path: root.configPath
    watchChanges: false
    atomicWrites: true
    printErrors: false
    onLoaded: {
      try {
        root.config = root.normalise(JSON.parse(text()))
        root.statusLine = "NIGHTSCAPE SYNCHRONIZED"
      } catch (error) {
        root.config = root.clone(root.defaults)
        root.statusLine = "INVALID CONFIGURATION · SAFE DEFAULTS ACTIVE"
      }
    }
    onLoadFailed: {
      root.config = root.clone(root.defaults)
      root.statusLine = "NEW NIGHTSCAPE · FRIENDLY DEFAULTS ACTIVE"
    }
  }
  Timer {
    interval: 50
    running: root.opened
    repeat: true
    onTriggered: {
      root.previewPhase += 0.035 * root.config.elements.animationSpeed
      preview.requestPaint()
    }
  }
  Component.onCompleted: if (!ensureDir.running) ensureDir.running = true

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
      color: "#ed05040c"
      Canvas {
        anchors.fill: parent
        opacity: 0.5
        onPaint: {
          var context = getContext("2d")
          context.reset()
          var gradient = context.createLinearGradient(0, 0, 0, height)
          gradient.addColorStop(0, root.deep)
          gradient.addColorStop(1, "#020204")
          context.fillStyle = gradient
          context.fillRect(0, 0, width, height)
          context.fillStyle = root.accent
          context.globalAlpha = 0.12
          for (var i = 0; i < 80; i++) {
            var x = (i * 149) % width
            var y = (i * 71) % Math.max(1, height * 0.65)
            context.fillRect(x, y, i % 5 === 0 ? 2 : 1, i % 5 === 0 ? 2 : 1)
          }
        }
      }
    }
    MouseArea { anchors.fill: parent; onClicked: root.dismiss() }

    Rectangle {
      id: card
      anchors.centerIn: parent
      width: Math.min(940, panel.width - 40)
      height: Math.min(940, panel.height - 30)
      radius: 18
      color: "#f20a0811"
      border.width: 1
      border.color: root.accent
      clip: true
      MouseArea { anchors.fill: parent; onClicked: function(mouse) { mouse.accepted = true } }

      Rectangle {
        id: header
        anchors { top: parent.top; left: parent.left; right: parent.right }
        height: 112
        color: "#321c1028"
        Text {
          x: 28; y: 17
          text: "OMARCHTOBER"
          color: root.accent
          font.family: root.fontFamily
          font.pixelSize: 32
          font.bold: true
          font.letterSpacing: 5
        }
        Text {
          x: 31; y: 61
          text: "ORIGINAL HALLOWEEN NIGHTSCAPE // CONTROL ROOM"
          color: "#d4c7dc"
          font.family: root.fontFamily
          font.pixelSize: 11
          font.letterSpacing: 1.5
        }
        Text {
          anchors { right: closeButton.left; rightMargin: 22; verticalCenter: parent.verticalCenter }
          text: root.config.experience.mode === "fun" ? "FUN MODE · FAMILY FRIENDLY" : "SCARY MODE · CREEPY CONTENT"
          color: root.config.experience.mode === "fun" ? "#85d7ad" : "#e07879"
          font.family: root.fontFamily
          font.pixelSize: 11
          font.bold: true
        }
        Rectangle {
          id: closeButton
          anchors { right: parent.right; rightMargin: 20; verticalCenter: parent.verticalCenter }
          width: 38; height: 38; radius: 19
          color: closeHover.containsMouse ? "#33ffffff" : "#14ffffff"
          border.width: 1; border.color: "#667f7188"
          Text { anchors.centerIn: parent; text: "×"; color: "#eee7f0"; font.family: root.fontFamily; font.pixelSize: 23 }
          MouseArea { id: closeHover; anchors.fill: parent; hoverEnabled: true; onClicked: root.dismiss() }
        }
      }

      Flickable {
        id: scroll
        anchors { top: header.bottom; bottom: footer.top; left: parent.left; right: parent.right }
        contentWidth: width
        contentHeight: content.implicitHeight + 44
        clip: true
        boundsBehavior: Flickable.StopAtBounds

        Column {
          id: content
          x: 26; y: 22
          width: scroll.width - 52
          spacing: 18

          Rectangle {
            width: parent.width; height: 162; radius: 12
            color: "#5808050d"
            border.width: 1; border.color: "#4a73577d"
            clip: true
            Canvas {
              id: preview
              anchors.fill: parent
              onPaint: {
                var context = getContext("2d")
                context.reset()
                var gradient = context.createLinearGradient(0, 0, 0, height)
                gradient.addColorStop(0, root.deep)
                gradient.addColorStop(1, "#121017")
                context.fillStyle = gradient
                context.fillRect(0, 0, width, height)
                context.globalAlpha = 0.9
                context.fillStyle = root.config.art.palette === "harvest" ? "#ffb354" : root.config.art.palette === "spectral" ? "#acf2d3" : "#eadcae"
                context.beginPath(); context.arc(width * 0.76, 43, 29, 0, Math.PI * 2); context.fill()
                context.globalAlpha = 0.35
                context.fillStyle = "#6f687d"
                for (var c = 0; c < Math.min(root.config.elements.clouds, 7); c++) {
                  var cx = ((c * 171 + root.previewPhase * (14 + c * 2)) % (width + 110)) - 55
                  var cy = 24 + (c * 29) % 62
                  context.beginPath(); context.ellipse(cx, cy, 39, 10, 0, 0, Math.PI * 2); context.fill()
                }
                context.globalAlpha = 1
                context.fillStyle = "#2e2733"
                context.beginPath()
                context.moveTo(width * 0.33, 129); context.lineTo(width * 0.33, 79); context.lineTo(width * 0.4, 51); context.lineTo(width * 0.47, 79)
                context.lineTo(width * 0.47, 61); context.lineTo(width * 0.53, 37); context.lineTo(width * 0.59, 61); context.lineTo(width * 0.59, 129); context.fill()
                context.fillStyle = "#e9a746"
                for (var w = 0; w < 8; w++) context.fillRect(width * 0.36 + (w % 4) * 42, 79 + Math.floor(w / 4) * 27, 9, 13)
                context.strokeStyle = root.accent
                context.lineWidth = 2
                for (var b = 0; b < Math.min(root.config.elements.bats, 14); b++) {
                  var bx = ((b * 83 + root.previewPhase * (18 + b)) % (width + 30)) - 15
                  var by = 19 + (b * 23) % 80 + Math.sin(root.previewPhase * 2 + b) * 4
                  context.beginPath(); context.moveTo(bx - 6, by); context.quadraticCurveTo(bx - 3, by - 5, bx, by); context.quadraticCurveTo(bx + 3, by - 5, bx + 6, by); context.stroke()
                }
                context.fillStyle = "#17211d"; context.fillRect(0, 129, width, 33)
              }
            }
            Text {
              anchors { right: parent.right; rightMargin: 16; bottom: parent.bottom; bottomMargin: 12 }
              text: "LIVE COMPOSITION PREVIEW\nADAPTIVE DETAIL · TERMINAL TRUECOLOR · 24 FPS"
              horizontalAlignment: Text.AlignRight
              color: "#7e7187"
              font.family: root.fontFamily
              font.pixelSize: 9
              lineHeight: 1.3
            }
          }

          Text { text: "CONTENT MODE"; color: "#a596ad"; font.family: root.fontFamily; font.pixelSize: 11; font.bold: true; font.letterSpacing: 2 }
          Row {
            width: parent.width; spacing: 10
            Repeater {
              model: [
                { key: "fun", label: "FUN", detail: "Friendly ghosts and costumed walkers. No blood, skeletons, zombies, or menace.", colour: "#71d4a1", fill: "#2871d4a1" },
                { key: "scary", label: "SCARY", detail: "Undead silhouettes, grave risers, blood accents, and darker creature sounds.", colour: "#dc676d", fill: "#28dc676d" }
              ]
              Rectangle {
                id: modeCard
                required property var modelData
                width: Math.floor((content.width - 10) / 2); height: 92; radius: 11
                color: root.config.experience.mode === modelData.key ? modelData.fill : "#14ffffff"
                border.width: root.config.experience.mode === modelData.key ? 2 : 1
                border.color: root.config.experience.mode === modelData.key ? modelData.colour : "#3b493f4e"
                Text { x: 15; y: 13; text: modeCard.modelData.label; color: modeCard.modelData.colour; font.family: root.fontFamily; font.pixelSize: 15; font.bold: true; font.letterSpacing: 1.5 }
                Text { x: 15; y: 40; width: parent.width - 30; text: modeCard.modelData.detail; color: "#a99eae"; font.family: root.fontFamily; font.pixelSize: 10; wrapMode: Text.Wrap; lineHeight: 1.25 }
                MouseArea { anchors.fill: parent; onClicked: root.mutate("experience", "mode", modeCard.modelData.key) }
              }
            }
          }

          Text { text: "SCENE"; color: "#a596ad"; font.family: root.fontFamily; font.pixelSize: 11; font.bold: true; font.letterSpacing: 2 }
          Rectangle {
            width: parent.width; height: 72; radius: 10
            color: "#17110d1b"; border.width: 1; border.color: root.accent
            Text { x: 16; y: 13; text: "HAUNTED ESTATE"; color: "#e9e0eb"; font.family: root.fontFamily; font.pixelSize: 13; font.bold: true }
            Text { x: 16; y: 38; text: "Moonlit Victorian exterior and surrounding graveyard · more scenes on the roadmap"; color: "#817687"; font.family: root.fontFamily; font.pixelSize: 10 }
            Text {
              anchors { right: parent.right; rightMargin: 16; verticalCenter: parent.verticalCenter }
              text: "AVAILABLE"; color: root.accent; font.family: root.fontFamily; font.pixelSize: 10; font.bold: true
            }
          }

          Text { text: "POPULATION & ATMOSPHERE"; color: "#a596ad"; font.family: root.fontFamily; font.pixelSize: 11; font.bold: true; font.letterSpacing: 2 }
          Column {
            width: parent.width; spacing: 7
            Repeater {
              model: root.elementDefinitions
              Rectangle {
                id: elementRow
                required property var modelData
                width: content.width; height: 57; radius: 9
                color: rowHover.containsMouse ? "#281e172c" : "#160e0b18"
                border.width: 1; border.color: rowHover.containsMouse ? modelData.accent : "#34423a46"
                Rectangle { x: 12; anchors.verticalCenter: parent.verticalCenter; width: 4; height: 31; radius: 2; color: elementRow.modelData.accent }
                Text { x: 29; y: 9; text: elementRow.modelData.name; color: "#e4dce7"; font.family: root.fontFamily; font.pixelSize: 12; font.bold: true }
                Text { x: 29; y: 31; text: elementRow.modelData.description; color: "#7e7483"; font.family: root.fontFamily; font.pixelSize: 10 }
                Row {
                  anchors { right: parent.right; rightMargin: 10; verticalCenter: parent.verticalCenter }
                  spacing: 8
                  Rectangle {
                    width: 32; height: 32; radius: 7; color: "#1effffff"
                    Text { anchors.centerIn: parent; text: "−"; color: "#d9cedd"; font.family: root.fontFamily; font.pixelSize: 18 }
                    MouseArea { anchors.fill: parent; onClicked: root.changeElement(elementRow.modelData.key, -elementRow.modelData.step, elementRow.modelData.max) }
                  }
                  Text { width: 38; height: 32; text: String(root.config.elements[elementRow.modelData.key]).padStart(2, "0"); color: elementRow.modelData.accent; font.family: root.fontFamily; font.pixelSize: 17; font.bold: true; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
                  Rectangle {
                    width: 32; height: 32; radius: 7; color: "#1effffff"
                    Text { anchors.centerIn: parent; text: "+"; color: "#d9cedd"; font.family: root.fontFamily; font.pixelSize: 17 }
                    MouseArea { anchors.fill: parent; onClicked: root.changeElement(elementRow.modelData.key, elementRow.modelData.step, elementRow.modelData.max) }
                  }
                }
                MouseArea {
                  id: rowHover
                  anchors { left: parent.left; right: parent.right; top: parent.top; bottom: parent.bottom; rightMargin: 128 }
                  hoverEnabled: true; acceptedButtons: Qt.NoButton
                }
              }
            }
          }

          Text { text: "NIGHT TREATMENT"; color: "#a596ad"; font.family: root.fontFamily; font.pixelSize: 11; font.bold: true; font.letterSpacing: 2 }
          Rectangle {
            width: parent.width; height: 178; radius: 11; color: "#160e0b18"; border.width: 1; border.color: "#34423a46"
            Text { x: 16; y: 14; text: "COLOR PALETTE"; color: "#e4dce7"; font.family: root.fontFamily; font.pixelSize: 11; font.bold: true }
            Row {
              x: 16; y: 40; spacing: 8
              Repeater {
                model: root.paletteDefinitions
                Rectangle {
                  id: paletteChip
                  required property var modelData
                  width: Math.floor((content.width - 32 - 24) / 4); height: 34; radius: 7
                  color: root.config.art.palette === modelData.key ? modelData.accent : "#16ffffff"
                  border.width: 1; border.color: modelData.accent
                  Text { anchors.centerIn: parent; text: paletteChip.modelData.label; color: root.config.art.palette === paletteChip.modelData.key ? "#100a13" : paletteChip.modelData.accent; font.family: root.fontFamily; font.pixelSize: 9; font.bold: true }
                  MouseArea { anchors.fill: parent; onClicked: root.mutate("art", "palette", paletteChip.modelData.key) }
                }
              }
            }
            Text { x: 16; y: 96; text: "LIGHTNING FREQUENCY"; color: "#a99eae"; font.family: root.fontFamily; font.pixelSize: 10 }
            Row {
              anchors { right: parent.right; rightMargin: 16; top: parent.top; topMargin: 87 }
              spacing: 8
              Rectangle {
                width: 32; height: 30; radius: 6; color: "#1effffff"
                Text { anchors.centerIn: parent; text: "−"; color: "#d9cedd"; font.family: root.fontFamily; font.pixelSize: 17 }
                MouseArea { anchors.fill: parent; onClicked: root.mutate("elements", "lightning", root.config.elements.lightning - 5) }
              }
              Text { width: 54; height: 30; text: root.config.elements.lightning + "%"; color: root.accent; font.family: root.fontFamily; font.pixelSize: 13; font.bold: true; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
              Rectangle {
                width: 32; height: 30; radius: 6; color: "#1effffff"
                Text { anchors.centerIn: parent; text: "+"; color: "#d9cedd"; font.family: root.fontFamily; font.pixelSize: 16 }
                MouseArea { anchors.fill: parent; onClicked: root.mutate("elements", "lightning", root.config.elements.lightning + 5) }
              }
            }
            Text { x: 16; y: 139; text: "ANIMATION SPEED"; color: "#a99eae"; font.family: root.fontFamily; font.pixelSize: 10 }
            Row {
              anchors { right: parent.right; rightMargin: 16; top: parent.top; topMargin: 130 }
              spacing: 8
              Rectangle {
                width: 32; height: 30; radius: 6; color: "#1effffff"
                Text { anchors.centerIn: parent; text: "−"; color: "#d9cedd"; font.family: root.fontFamily; font.pixelSize: 17 }
                MouseArea { anchors.fill: parent; onClicked: root.mutate("elements", "animationSpeed", root.config.elements.animationSpeed - 0.1) }
              }
              Text { width: 54; height: 30; text: Number(root.config.elements.animationSpeed).toFixed(1) + "×"; color: root.accent; font.family: root.fontFamily; font.pixelSize: 13; font.bold: true; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
              Rectangle {
                width: 32; height: 30; radius: 6; color: "#1effffff"
                Text { anchors.centerIn: parent; text: "+"; color: "#d9cedd"; font.family: root.fontFamily; font.pixelSize: 16 }
                MouseArea { anchors.fill: parent; onClicked: root.mutate("elements", "animationSpeed", root.config.elements.animationSpeed + 0.1) }
              }
            }
          }

          Text { text: "AMBIENCE"; color: "#a596ad"; font.family: root.fontFamily; font.pixelSize: 11; font.bold: true; font.letterSpacing: 2 }
          Rectangle {
            width: parent.width; height: 272; radius: 11
            color: root.config.sound.enabled ? "#281d142e" : "#160e0b18"
            border.width: 1; border.color: root.config.sound.enabled ? root.accent : "#34423a46"
            Text { x: 16; y: 14; text: "AUDIO"; color: "#e4dce7"; font.family: root.fontFamily; font.pixelSize: 12; font.bold: true }
            Text { x: 16; y: 37; text: "off by default · one audio leader across every monitor"; color: "#7e7483"; font.family: root.fontFamily; font.pixelSize: 10 }
            Rectangle {
              x: 16; y: 67; width: 48; height: 26; radius: 13; color: root.config.sound.enabled ? root.accent : "#3b3340"
              Rectangle { x: root.config.sound.enabled ? parent.width - width - 3 : 3; anchors.verticalCenter: parent.verticalCenter; width: 20; height: 20; radius: 10; color: root.config.sound.enabled ? "#100a13" : "#b7aebc"; Behavior on x { NumberAnimation { duration: 150 } } }
              MouseArea { anchors.fill: parent; onClicked: root.mutate("sound", "enabled", !root.config.sound.enabled) }
            }
            Text { x: 78; y: 72; text: root.config.sound.enabled ? "ENABLED" : "DISABLED"; color: root.config.sound.enabled ? root.accent : "#8a808e"; font.family: root.fontFamily; font.pixelSize: 10; font.bold: true }
            Rectangle {
              anchors { right: volumeRow.left; rightMargin: 14; top: parent.top; topMargin: 65 }
              width: 78; height: 30; radius: 6; color: audioTest.running ? "#3322b684" : "#1effffff"; border.width: 1; border.color: "#52605765"
              Text { anchors.centerIn: parent; text: audioTest.running ? "PLAYING" : "TEST 8S"; color: audioTest.running ? "#78d9ad" : "#cfc5d3"; font.family: root.fontFamily; font.pixelSize: 9; font.bold: true }
              MouseArea { anchors.fill: parent; enabled: !audioTest.running; onClicked: root.testAudio() }
            }
            Row {
              id: volumeRow
              anchors { right: parent.right; rightMargin: 16; top: parent.top; topMargin: 66 }
              spacing: 7
              Rectangle {
                width: 30; height: 28; radius: 6; color: "#1effffff"
                Text { anchors.centerIn: parent; text: "−"; color: "#d9cedd"; font.family: root.fontFamily; font.pixelSize: 16 }
                MouseArea { anchors.fill: parent; onClicked: root.mutate("sound", "volume", root.config.sound.volume - 5) }
              }
              Text { width: 46; height: 28; text: root.config.sound.volume + "%"; color: root.accent; font.family: root.fontFamily; font.pixelSize: 12; font.bold: true; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
              Rectangle {
                width: 30; height: 28; radius: 6; color: "#1effffff"
                Text { anchors.centerIn: parent; text: "+"; color: "#d9cedd"; font.family: root.fontFamily; font.pixelSize: 15 }
                MouseArea { anchors.fill: parent; onClicked: root.mutate("sound", "volume", root.config.sound.volume + 5) }
              }
            }
            Text { x: 16; y: 113; text: "SOURCE"; color: "#a99eae"; font.family: root.fontFamily; font.pixelSize: 10 }
            Row {
              x: 83; y: 104; spacing: 8
              Repeater {
                model: [{ key: "procedural", label: "PROCEDURAL" }, { key: "media", label: "MY MEDIA" }]
                Rectangle {
                  id: sourceChip
                  required property var modelData
                  width: 100; height: 30; radius: 6
                  color: root.config.sound.source === modelData.key ? root.accent : "#1effffff"
                  border.width: 1; border.color: root.accent
                  Text { anchors.centerIn: parent; text: sourceChip.modelData.label; color: root.config.sound.source === sourceChip.modelData.key ? "#100a13" : root.accent; font.family: root.fontFamily; font.pixelSize: 9; font.bold: true }
                  MouseArea { anchors.fill: parent; onClicked: root.mutate("sound", "source", sourceChip.modelData.key) }
                }
              }
            }
            Rectangle {
              x: 310; y: 104; width: 116; height: 30; radius: 6; color: "#1effffff"; border.width: 1; border.color: "#52605765"
              Text { anchors.centerIn: parent; text: "CHOOSE FILE"; color: "#cfc5d3"; font.family: root.fontFamily; font.pixelSize: 9; font.bold: true }
              MouseArea { anchors.fill: parent; onClicked: root.chooseMedia() }
            }
            Text { x: 440; y: 112; width: parent.width - 456; text: root.config.sound.mediaPath || "MP3, MP4, M4A, OGG, OPUS, FLAC, WAV, or WEBM"; color: "#786e7d"; font.family: root.fontFamily; font.pixelSize: 9; elide: Text.ElideMiddle }
            Rectangle { x: 16; y: 151; width: parent.width - 32; height: 1; color: "#34423a46" }
            Row {
              x: 16; y: 169; width: parent.width - 32; spacing: 14
              Repeater {
                model: [
                  { key: "wind", label: "WIND", detail: "filtered night air" },
                  { key: "thunder", label: "THUNDER", detail: root.config.experience.mode === "fun" ? "gentle distant rumbles" : "deep distant rumbles" },
                  { key: "creatures", label: "CREATURES", detail: root.config.experience.mode === "fun" ? "soft owl calls" : "low nocturnal calls" }
                ]
                Rectangle {
                  id: audioLayer
                  required property var modelData
                  width: Math.floor((parent.width - 28) / 3); height: 78; radius: 8
                  color: root.config.sound[audioLayer.modelData.key] ? "#24231b2a" : "#12ffffff"
                  border.width: 1; border.color: root.config.sound[audioLayer.modelData.key] ? root.accent : "#34423a46"
                  Text { x: 12; y: 13; text: audioLayer.modelData.label; color: root.config.sound[audioLayer.modelData.key] ? "#e4dce7" : "#7e7483"; font.family: root.fontFamily; font.pixelSize: 10; font.bold: true }
                  Text { x: 12; y: 37; text: audioLayer.modelData.detail; color: "#786e7d"; font.family: root.fontFamily; font.pixelSize: 9 }
                  Text {
                    anchors { right: parent.right; rightMargin: 12; top: parent.top; topMargin: 13 }
                    text: root.config.sound[audioLayer.modelData.key] ? "ON" : "OFF"; color: root.config.sound[audioLayer.modelData.key] ? root.accent : "#665d6b"; font.family: root.fontFamily; font.pixelSize: 10; font.bold: true
                  }
                  MouseArea { anchors.fill: parent; onClicked: root.mutate("sound", audioLayer.modelData.key, !root.config.sound[audioLayer.modelData.key]) }
                }
              }
            }
          }

          Text { text: "OMARCHY INTEGRATION"; color: "#a596ad"; font.family: root.fontFamily; font.pixelSize: 11; font.bold: true; font.letterSpacing: 2 }
          Row {
            width: parent.width; spacing: 10
            Repeater {
              model: [
                { key: "idleEnabled", label: "AUTOMATIC IDLE NIGHT", detail: "Uses shell.json idle timing and preserves Omarchy lock behavior." },
                { key: "exitOnPointerMotion", label: "EXIT ON POINTER MOVE", detail: "Clicks and keyboard input always return to the desktop." }
              ]
              Rectangle {
                id: integrationCard
                required property var modelData
                width: Math.floor((content.width - 10) / 2); height: 82; radius: 10
                color: root.config.integration[modelData.key] ? "#241b1929" : "#160e0b18"
                border.width: 1; border.color: root.config.integration[modelData.key] ? root.accent : "#34423a46"
                Text { x: 14; y: 13; text: integrationCard.modelData.label; color: "#e4dce7"; font.family: root.fontFamily; font.pixelSize: 10; font.bold: true }
                Text { x: 14; y: 37; width: parent.width - 82; text: integrationCard.modelData.detail; color: "#786e7d"; font.family: root.fontFamily; font.pixelSize: 9; wrapMode: Text.Wrap }
                Rectangle {
                  anchors { right: parent.right; rightMargin: 14; verticalCenter: parent.verticalCenter }
                  width: 46; height: 24; radius: 12
                  color: root.config.integration[integrationCard.modelData.key] ? root.accent : "#3b3340"
                  Rectangle { x: root.config.integration[integrationCard.modelData.key] ? parent.width - width - 3 : 3; anchors.verticalCenter: parent.verticalCenter; width: 18; height: 18; radius: 9; color: root.config.integration[integrationCard.modelData.key] ? "#100a13" : "#b7aebc"; Behavior on x { NumberAnimation { duration: 150 } } }
                  MouseArea { anchors.fill: parent; onClicked: root.mutate("integration", integrationCard.modelData.key, !root.config.integration[integrationCard.modelData.key]) }
                }
              }
            }
          }
        }
      }

      Rectangle {
        id: footer
        anchors { left: parent.left; right: parent.right; bottom: parent.bottom }
        height: 80; color: "#f20a0811"
        Text { x: 24; anchors.verticalCenter: parent.verticalCenter; text: root.statusLine; color: "#746a79"; font.family: root.fontFamily; font.pixelSize: 9; font.letterSpacing: 1 }
        Rectangle {
          anchors { right: stopButton.left; rightMargin: 10; verticalCenter: parent.verticalCenter }
          width: 96; height: 40; radius: 8; color: resetHover.containsMouse ? "#2affffff" : "#14ffffff"; border.width: 1; border.color: "#4b5d5262"
          Text { anchors.centerIn: parent; text: "RESET"; color: "#c5b9c9"; font.family: root.fontFamily; font.pixelSize: 10; font.bold: true }
          MouseArea { id: resetHover; anchors.fill: parent; hoverEnabled: true; onClicked: root.restoreDefaults() }
        }
        Rectangle {
          id: stopButton
          anchors { right: launchButton.left; rightMargin: 10; verticalCenter: parent.verticalCenter }
          width: 118; height: 40; radius: 8; color: stopHover.containsMouse ? "#30d86673" : "#14ffffff"; border.width: 1; border.color: "#61584452"
          Text { anchors.centerIn: parent; text: "RETURN"; color: "#d69aa2"; font.family: root.fontFamily; font.pixelSize: 10; font.bold: true }
          MouseArea { id: stopHover; anchors.fill: parent; hoverEnabled: true; onClicked: root.stop() }
        }
        Rectangle {
          id: launchButton
          anchors { right: parent.right; rightMargin: 20; verticalCenter: parent.verticalCenter }
          width: 182; height: 44; radius: 9; color: launchHover.containsMouse ? Qt.lighter(root.accent, 1.12) : root.accent; border.width: 1; border.color: "#b9ffffff"
          Text { anchors.centerIn: parent; text: "BEGIN NIGHT  ›"; color: "#100a13"; font.family: root.fontFamily; font.pixelSize: 11; font.bold: true; font.letterSpacing: 0.7 }
          MouseArea { id: launchHover; anchors.fill: parent; hoverEnabled: true; onClicked: root.launch() }
        }
      }

      Item {
        id: keyCatcher
        anchors.fill: parent
        focus: root.opened
        Keys.onEscapePressed: root.dismiss()
        Keys.onReturnPressed: root.launch()
        Keys.onEnterPressed: root.launch()
        Keys.onDownPressed: scroll.contentY = Math.min(scroll.contentHeight - scroll.height, scroll.contentY + 64)
        Keys.onUpPressed: scroll.contentY = Math.max(0, scroll.contentY - 64)
        Keys.onPressed: function(event) {
          if (event.key === Qt.Key_PageDown) {
            scroll.contentY = Math.min(scroll.contentHeight - scroll.height, scroll.contentY + scroll.height * 0.82)
            event.accepted = true
          } else if (event.key === Qt.Key_PageUp) {
            scroll.contentY = Math.max(0, scroll.contentY - scroll.height * 0.82)
            event.accepted = true
          } else if (event.key === Qt.Key_Home) {
            scroll.contentY = 0; event.accepted = true
          } else if (event.key === Qt.Key_End) {
            scroll.contentY = Math.max(0, scroll.contentHeight - scroll.height); event.accepted = true
          }
        }
      }
    }
  }
}
