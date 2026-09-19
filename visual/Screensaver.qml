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
    var requested = Number(options.motion)
    motion = isFinite(requested) ? Math.max(0, Math.min(2, requested)) : 0.7
    if (scenePaths.length > 0) {
      imageA.item.source = "file://" + scenePaths[0]
      imageA.opacity = 1
      imageB.opacity = 0
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

  Component {
    id: sceneImage
    Image {
      anchors.centerIn: parent
      width: parent.width * 1.035
      height: parent.height * 1.035
      fillMode: Image.PreserveAspectCrop
      asynchronous: true
      cache: true
      smooth: true
      mipmap: true
      sourceSize.width: Math.min(3840, root.width * 1.08)
      sourceSize.height: Math.min(2160, root.height * 1.08)
      Behavior on opacity { NumberAnimation { duration: root.transitionMs; easing.type: Easing.InOutCubic } }
      SequentialAnimation on scale {
        loops: Animation.Infinite
        running: root.motion > 0
        NumberAnimation { from: 1.0; to: 1.012; duration: 26000 / Math.max(0.25, root.motion); easing.type: Easing.InOutSine }
        NumberAnimation { from: 1.012; to: 1.0; duration: 26000 / Math.max(0.25, root.motion); easing.type: Easing.InOutSine }
      }
    }
  }

  Loader { id: imageA; anchors.fill: parent; sourceComponent: sceneImage }
  Loader { id: imageB; anchors.fill: parent; sourceComponent: sceneImage }

  Rectangle {
    anchors.fill: parent
    color: root.themeColor()
    opacity: root.themeOpacity()
  }

  Item {
    id: fogLayer
    anchors.fill: parent
    opacity: 0.055 * root.motion
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
        color: fogBand.index % 2 ? "#a79fca" : "#dad5e8"
        x: -width
        SequentialAnimation on x {
          loops: Animation.Infinite
          running: root.motion > 0
          PauseAnimation { duration: fogBand.index * 4200 }
          NumberAnimation {
            from: -root.width
            to: root.width * 1.2
            duration: (62000 + fogBand.index * 17000) / Math.max(0.25, root.motion)
            easing.type: Easing.InOutSine
          }
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
    interval: 37000
    running: root.motion > 0
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
