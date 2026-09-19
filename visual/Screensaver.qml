pragma ComponentBehavior: Bound
import QtCore
import QtQuick
import QtQuick.Window
Window {
  id: root
  visible: true
  visibility: Window.FullScreen
  color: "#060715"
  title: "Omarchtober Visual"
  flags: Qt.FramelessWindowHint

  property var options: ({})
  property var scenePaths: []
  property int sceneIndex: 0
  property bool frontIsA: true
  property bool armed: false
  property real motion: Number(options.motion || 1.0)
  property real parallaxDepth: 0.55
  property var sceneLayers: []
  property var foreground: ({})
  property real foregroundDriftX: 0
  property real foregroundDriftY: 0
  property real mist: 0.7
  property real flight: 0.6
  property real lanterns: 0.65
  property real lightningLevel: 0.35
  property int transitionMs: 2800

  function sessionCandidates() {
    var dirs = [
      StandardPaths.writableLocation(StandardPaths.RuntimeLocation),
      StandardPaths.writableLocation(StandardPaths.GenericCacheLocation)
    ]
    var urls = []
    for (var i = 0; i < dirs.length; i++) {
      var dir = String(dirs[i] || "")
      if (dir.length) urls.push(dir.replace(/\/$/, "") + "/omarchtober/session.json")
    }
    return urls
  }

  function readSession() {
    var urls = sessionCandidates()
    for (var i = 0; i < urls.length; i++) {
      var request = new XMLHttpRequest()
      try {
        request.open("GET", urls[i], false)
        request.send(null)
        if (request.responseText) return JSON.parse(request.responseText)
      } catch (error) {
        continue
      }
    }
    return ({})
  }

  function activateLayers(index) {
    var layers = Array.isArray(sceneLayers[index]) ? sceneLayers[index] : []
    foreground = layers.length && layers[0] && typeof layers[0] === "object" ? layers[0] : ({})
  }

  function parseOptions() {
    var parsed = readSession()
    options = parsed && typeof parsed === "object" ? parsed : ({})
    var incoming = Array.isArray(options.scenes) ? options.scenes : []
    var files = []
    for (var i = 0; i < incoming.length; i++) {
      var file = String(incoming[i])
      if (file.length) files.push(file)
    }
    scenePaths = files
    sceneLayers = Array.isArray(options.layers) ? options.layers : []
    var requested = Number(options.motion)
    motion = isFinite(requested) ? Math.max(0, Math.min(2, requested)) : 0.7
    var requestedParallax = Number(options.parallaxDepth)
    parallaxDepth = isFinite(requestedParallax) ? Math.max(0, Math.min(2, requestedParallax)) : 0.55
    var effects = options.effects && typeof options.effects === "object" ? options.effects : ({})
    var effectNames = ["mist", "flight", "lanterns", "lightning"]
    var effectDefaults = [0.7, 0.6, 0.65, 0.35]
    var effectValues = []
    for (var j = 0; j < effectNames.length; j++) {
      var level = Number(effects[effectNames[j]])
      effectValues.push(isFinite(level) ? Math.max(0, Math.min(2, level)) : effectDefaults[j])
    }
    mist = effectValues[0]
    flight = effectValues[1]
    lanterns = effectValues[2]
    lightningLevel = effectValues[3]
    if (scenePaths.length > 0) {
      imageA.item.source = "file://" + scenePaths[0]
      imageA.opacity = 1
      imageB.opacity = 0
      activateLayers(0)
    }
    armTimer.start()
    var seconds = Number(options.duration)
    rotationTimer.interval = Math.max(15, Math.min(900, isFinite(seconds) ? seconds : 90)) * 1000
    rotationTimer.running = scenePaths.length > 1
  }

  function nextScene() {
    if (scenePaths.length < 2) return
    sceneIndex = (sceneIndex + 1) % scenePaths.length
    if (frontIsA) {
      imageB.item.source = "file://" + scenePaths[sceneIndex]
      imageB.opacity = 1
      imageA.opacity = 0
    } else {
      imageA.item.source = "file://" + scenePaths[sceneIndex]
      imageA.opacity = 1
      imageB.opacity = 0
    }
    frontIsA = !frontIsA
    activateLayers(sceneIndex)
  }

  function dismiss() {
    if (armed) Qt.quit()
  }

  function themeColor() {
    var theme = String(options.theme || "moonlit")
    if (theme === "harvest") return "#481500"
    if (theme === "spectral") return "#003f38"
    if (theme === "midnight") return "#000b32"
    return "#000000"
  }

  function themeOpacity() {
    return String(options.theme || "moonlit") === "moonlit" ? 0 : 0.13
  }

  Rectangle {
    anchors.fill: parent
    color: "#060715"
  }

  Component {
    id: sceneImage
    Image {
      anchors.fill: parent
      fillMode: Image.PreserveAspectFit
      asynchronous: true
      cache: true
      smooth: true
      mipmap: true
      sourceSize.width: Math.min(3840, parent.width)
      sourceSize.height: Math.min(2160, parent.height)
      Behavior on opacity { NumberAnimation { duration: root.transitionMs; easing.type: Easing.InOutCubic } }
    }
  }

  Item {
    id: artFrame
    anchors.centerIn: parent
    width: Math.min(root.width, root.height * 16 / 9)
    height: width * 9 / 16
    clip: false
  }

  Loader { id: imageA; anchors.fill: artFrame; sourceComponent: sceneImage }
  Loader { id: imageB; anchors.fill: artFrame; sourceComponent: sceneImage }

  Image {
    id: foregroundPlane
    anchors.fill: artFrame
    source: root.foreground.source ? "file://" + root.foreground.source : ""
    fillMode: Image.PreserveAspectFit
    asynchronous: true
    cache: true
    smooth: true
    mipmap: true
    sourceSize.width: Math.min(3840, artFrame.width)
    sourceSize.height: Math.min(2160, artFrame.height)
    opacity: Math.min(0.72, Number(root.foreground.opacity || 0) * root.parallaxDepth)
    transform: Translate { x: root.foregroundDriftX; y: root.foregroundDriftY }
  }

  SequentialAnimation on foregroundDriftX {
    loops: Animation.Infinite
    running: root.parallaxDepth > 0 && root.motion > 0 && foregroundPlane.source !== ""
    NumberAnimation {
      from: -Number(root.foreground.xAmplitude || 0) * root.parallaxDepth
      to: Number(root.foreground.xAmplitude || 0) * root.parallaxDepth
      duration: 38000 / Math.max(0.25, root.motion)
      easing.type: Easing.InOutSine
    }
    NumberAnimation {
      from: Number(root.foreground.xAmplitude || 0) * root.parallaxDepth
      to: -Number(root.foreground.xAmplitude || 0) * root.parallaxDepth
      duration: 38000 / Math.max(0.25, root.motion)
      easing.type: Easing.InOutSine
    }
  }

  SequentialAnimation on foregroundDriftY {
    loops: Animation.Infinite
    running: root.parallaxDepth > 0 && root.motion > 0 && foregroundPlane.source !== ""
    NumberAnimation {
      from: -Number(root.foreground.yAmplitude || 0) * root.parallaxDepth
      to: Number(root.foreground.yAmplitude || 0) * root.parallaxDepth
      duration: 51000 / Math.max(0.25, root.motion)
      easing.type: Easing.InOutSine
    }
    NumberAnimation {
      from: Number(root.foreground.yAmplitude || 0) * root.parallaxDepth
      to: -Number(root.foreground.yAmplitude || 0) * root.parallaxDepth
      duration: 51000 / Math.max(0.25, root.motion)
      easing.type: Easing.InOutSine
    }
  }
  Rectangle {
    anchors.fill: parent
    color: root.themeColor()
    opacity: root.themeOpacity()
  }

  Item {
    id: flightLayer
    anchors.fill: parent
    clip: true
    opacity: Math.min(1, root.flight * root.motion * 0.82)

    Repeater {
      model: 7
      Item {
        id: flockMember
        required property int index
        width: 28 + (flockMember.index % 3) * 7
        height: 13
        y: root.height * (0.12 + (flockMember.index % 4) * 0.075)
        x: -width
        opacity: 0.55 + (flockMember.index % 3) * 0.12
        Rectangle {
          width: parent.width * 0.55; height: 3; radius: 2
          anchors.right: parent.horizontalCenter; anchors.verticalCenter: parent.verticalCenter
          rotation: -16; color: "#5b5575"
        }
        Rectangle {
          width: parent.width * 0.55; height: 3; radius: 2
          anchors.left: parent.horizontalCenter; anchors.verticalCenter: parent.verticalCenter
          rotation: 16; color: "#5b5575"
        }
        Rectangle {
          width: 4; height: 5; radius: 2
          anchors.centerIn: parent; color: "#5b5575"
        }
        SequentialAnimation on x {
          loops: Animation.Infinite
          running: root.flight > 0 && root.motion > 0
          PauseAnimation { duration: flockMember.index * 5800 }
          NumberAnimation {
            from: -flockMember.width
            to: root.width + flockMember.width
            duration: (33000 + flockMember.index * 4200) / Math.max(0.25, root.motion * root.flight)
            easing.type: Easing.InOutSine
          }
        }
      }
    }
  }

  Item {
    id: fogLayer
    anchors.fill: parent
    opacity: Math.min(0.13, 0.055 * root.motion * root.mist)
    clip: true

    Repeater {
      model: 3
      Rectangle {
        id: fogBand
        required property int index
        width: root.width * 0.8
        height: root.height * (0.08 + fogBand.index * 0.018)
        y: root.height * (0.48 + fogBand.index * 0.13)
        radius: height / 2
        gradient: Gradient {
          GradientStop { position: 0.0; color: "#00dad5e8" }
          GradientStop { position: 0.36; color: fogBand.index % 2 ? "#80a79fca" : "#80dad5e8" }
          GradientStop { position: 0.64; color: fogBand.index % 2 ? "#80a79fca" : "#80dad5e8" }
          GradientStop { position: 1.0; color: "#00dad5e8" }
        }
        x: -width
        SequentialAnimation on x {
          loops: Animation.Infinite
          running: root.mist > 0 && root.motion > 0
          PauseAnimation { duration: fogBand.index * 4200 }
          NumberAnimation {
            from: -root.width
            to: root.width * 1.2
            duration: (62000 + fogBand.index * 17000) / Math.max(0.25, root.motion * root.mist)
            easing.type: Easing.InOutSine
          }
        }
      }
    }
  }

  Item {
    id: lanternLayer
    anchors.fill: parent
    opacity: Math.min(1, root.lanterns * root.motion)
    Repeater {
      model: 14
      Item {
        id: lanternMote
        required property int index
        width: 34; height: 34
        x: root.width * (0.06 + (lanternMote.index * 0.137) % 0.88)
        y: root.height * (0.46 + (lanternMote.index % 5) * 0.085)
        opacity: 0.14 + (lanternMote.index % 4) * 0.035
        Rectangle {
          anchors.centerIn: parent
          width: 32; height: 32; radius: 16
          color: "#d99338"; opacity: 0.23
        }
        Rectangle {
          anchors.centerIn: parent
          width: 6; height: 6; radius: 3
          color: "#ffe7a6"
        }
        SequentialAnimation on opacity {
          loops: Animation.Infinite
          running: root.lanterns > 0 && root.motion > 0
          NumberAnimation { to: 0.35; duration: 1400 + lanternMote.index * 120 }
          NumberAnimation { to: 0.10; duration: 1900 + lanternMote.index * 160 }
        }
      }
    }
  }
  Rectangle {
    id: lightning
    anchors.fill: parent
    color: "#d8ddff"
    opacity: 0
    SequentialAnimation {
      id: lightningAnimation
      NumberAnimation { target: lightning; property: "opacity"; to: 0.10; duration: 45 }
      NumberAnimation { target: lightning; property: "opacity"; to: 0; duration: 180 }
    }
  }

  Timer {
    interval: Math.max(9000, 60000 / Math.max(0.25, root.motion * root.lightningLevel))
    running: root.motion > 0 && root.lightningLevel > 0
    repeat: true
    onTriggered: if (String(root.options.theme || "moonlit") !== "harvest") lightningAnimation.restart()
  }
  Timer { id: rotationTimer; repeat: true; onTriggered: root.nextScene() }
  Timer { id: armTimer; interval: 900; onTriggered: root.armed = true }

  MouseArea {
    anchors.fill: parent
    hoverEnabled: true
    acceptedButtons: Qt.AllButtons
    onClicked: root.dismiss()
    onWheel: root.dismiss()
    onPositionChanged: if (root.options.exitOnMotion !== false) root.dismiss()
  }
  Item {
    anchors.fill: parent
    focus: true
    Keys.onPressed: root.dismiss()
    Component.onCompleted: forceActiveFocus()
  }

  Component.onCompleted: parseOptions()
}
