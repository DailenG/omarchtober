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
  property bool transitionPending: false
  property var pendingIncoming: null
  property var pendingOutgoing: null
  property int transitionMs: 2800
  property real cameraOffset: 0
  readonly property real cameraAmplitude: artFrame.width * 0.0175

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


  function layerSet(index) {
    return Array.isArray(sceneLayers[index]) ? sceneLayers[index] : []
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
    if (scenePaths.length > 0) {
      sceneA.layerSet = layerSet(0)
      sceneA.scenePath = scenePaths[0]
      sceneA.opacity = 1
      sceneB.opacity = 0
    }
    armTimer.start()
    var seconds = Number(options.duration)
    rotationTimer.interval = Math.max(15, Math.min(900, isFinite(seconds) ? seconds : 90)) * 1000
    rotationTimer.running = scenePaths.length > 1
  }

  function beginTransition(candidate) {
    if (!transitionPending || candidate !== pendingIncoming || !candidate.contentReady) return
    pendingIncoming.opacity = 1
    pendingOutgoing.opacity = 0
    frontIsA = !frontIsA
    transitionPending = false
    pendingIncoming = null
    pendingOutgoing = null
  }

  function nextScene() {
    if (scenePaths.length < 2 || transitionPending) return
    sceneIndex = (sceneIndex + 1) % scenePaths.length
    pendingOutgoing = frontIsA ? sceneA : sceneB
    pendingIncoming = frontIsA ? sceneB : sceneA
    pendingIncoming.opacity = 0
    pendingIncoming.layerSet = layerSet(sceneIndex)
    pendingIncoming.scenePath = scenePaths[sceneIndex]
    transitionPending = true
    beginTransition(pendingIncoming)
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

  Item {
    id: artFrame
    anchors.centerIn: parent
    width: Math.min(root.width, root.height * 16 / 9)
    height: width * 9 / 16
    clip: true
  }

  component SceneStack: Item {
    id: sceneStack
    property string scenePath: ""
    property var layerSet: []
    property bool contentReady: false
    property var layerReadiness: []
    transform: [
      Scale {
        origin.x: sceneStack.width / 2
        origin.y: sceneStack.height / 2
        xScale: root.motion > 0 ? 1.04 : 1
        yScale: root.motion > 0 ? 1.04 : 1
      },
      Translate { x: root.cameraOffset }
    ]

    function refreshContentReady() {
      var ready = scenePath.length > 0 && baseImage.status === Image.Ready && layerReadiness.length === layerSet.length
      for (var i = 0; ready && i < layerReadiness.length; i++) ready = layerReadiness[i] === true
      contentReady = ready
    }
    function recordLayerReady(index, ready) {
      var next = layerReadiness.slice()
      next[index] = ready
      layerReadiness = next
      refreshContentReady()
    }

    onScenePathChanged: {
      contentReady = false
      Qt.callLater(refreshContentReady)
    }
    onLayerSetChanged: {
      contentReady = false
      layerReadiness = []
      Qt.callLater(refreshContentReady)
    }
    Behavior on opacity { NumberAnimation { duration: root.transitionMs; easing.type: Easing.InOutCubic } }

    Image {
      id: baseImage
      anchors.fill: parent
      source: sceneStack.scenePath ? "file://" + sceneStack.scenePath : ""
      fillMode: Image.PreserveAspectFit
      asynchronous: true
      cache: true
      smooth: true
      mipmap: true
      sourceSize.width: Math.min(3840, sceneStack.width)
      sourceSize.height: Math.min(2160, sceneStack.height)
      onStatusChanged: sceneStack.refreshContentReady()
    }

    Repeater {
      id: layerRepeater
      model: sceneStack.layerSet

      delegate: Item {
        id: layerPlane
        required property int index
        required property var modelData

        anchors.fill: parent
        property real driftX: 0
        property real driftY: 0
        transform: Translate { x: layerPlane.driftX; y: layerPlane.driftY }

        Image {
          id: planeImage
          anchors.fill: parent
          source: layerPlane.modelData.source ? "file://" + layerPlane.modelData.source : ""
          fillMode: Image.PreserveAspectFit
          asynchronous: true
          cache: true
          smooth: true
          mipmap: true
          sourceSize.width: Math.min(3840, sceneStack.width)
          sourceSize.height: Math.min(2160, sceneStack.height)
          opacity: Math.min(0.72, Number(layerPlane.modelData.opacity) * root.parallaxDepth)
          onStatusChanged: sceneStack.recordLayerReady(layerPlane.index, planeImage.status === Image.Ready)
        }

        SequentialAnimation on driftX {
          loops: Animation.Infinite
          running: root.parallaxDepth > 0 && root.motion > 0 && String(layerPlane.modelData.source || "").length > 0
          NumberAnimation {
            from: -Number(layerPlane.modelData.xAmplitude) * Number(layerPlane.modelData.depth) * root.parallaxDepth
            to: Number(layerPlane.modelData.xAmplitude) * Number(layerPlane.modelData.depth) * root.parallaxDepth
            duration: (38000 + layerPlane.index * 3500) / Math.max(0.25, root.motion)
            easing.type: Easing.InOutSine
          }
          NumberAnimation {
            from: Number(layerPlane.modelData.xAmplitude) * Number(layerPlane.modelData.depth) * root.parallaxDepth
            to: -Number(layerPlane.modelData.xAmplitude) * Number(layerPlane.modelData.depth) * root.parallaxDepth
            duration: (38000 + layerPlane.index * 3500) / Math.max(0.25, root.motion)
            easing.type: Easing.InOutSine
          }
        }

        SequentialAnimation on driftY {
          loops: Animation.Infinite
          running: root.parallaxDepth > 0 && root.motion > 0 && String(layerPlane.modelData.source || "").length > 0
          NumberAnimation {
            from: -Number(layerPlane.modelData.yAmplitude) * Number(layerPlane.modelData.depth) * root.parallaxDepth
            to: Number(layerPlane.modelData.yAmplitude) * Number(layerPlane.modelData.depth) * root.parallaxDepth
            duration: (51000 + layerPlane.index * 4700) / Math.max(0.25, root.motion)
            easing.type: Easing.InOutSine
          }
          NumberAnimation {
            from: Number(layerPlane.modelData.yAmplitude) * Number(layerPlane.modelData.depth) * root.parallaxDepth
            to: -Number(layerPlane.modelData.yAmplitude) * Number(layerPlane.modelData.depth) * root.parallaxDepth
            duration: (51000 + layerPlane.index * 4700) / Math.max(0.25, root.motion)
            easing.type: Easing.InOutSine
          }
        }
      }
    }
  }

  SceneStack {
    id: sceneA
    anchors.fill: artFrame
    opacity: 0
    onContentReadyChanged: if (contentReady) root.beginTransition(this)
  }
  SceneStack {
    id: sceneB
    anchors.fill: artFrame
    opacity: 0
    onContentReadyChanged: if (contentReady) root.beginTransition(this)
  }
  Rectangle {
    anchors.fill: parent
    color: root.themeColor()
    opacity: root.themeOpacity()
  }

  SequentialAnimation on cameraOffset {
    loops: Animation.Infinite
    running: root.motion > 0 && root.scenePaths.length > 0
    NumberAnimation {
      from: -root.cameraAmplitude
      to: root.cameraAmplitude
      duration: 20000 / Math.max(0.25, root.motion)
      easing.type: Easing.InOutSine
    }
    NumberAnimation {
      from: root.cameraAmplitude
      to: -root.cameraAmplitude
      duration: 20000 / Math.max(0.25, root.motion)
      easing.type: Easing.InOutSine
    }
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
