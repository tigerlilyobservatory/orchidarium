import QtQuick
import QtQuick.Window
import QtQuick.Controls

Window {
    id: root

    width: 720
    height: 1280
    visible: true
    title: qsTr("Hello World")

    property var defaultConfig: ({
        fullscreen: false,
        relayCount: 4,
        intervalSeconds: "60",
        maxPointBacklog: "1000",
        monitoringUrl: "https://grafana:3000",
        readinessUrl: "http://127.0.0.1:8085/ready"
    })

    readonly property bool hasConfig: typeof config !== "undefined" && config !== null
    readonly property bool fullscreenEnabled: hasConfig ? config.fullscreen : defaultConfig.fullscreen
    readonly property int relayCount: hasConfig ? config.relayCount : defaultConfig.relayCount
    readonly property string intervalSeconds: hasConfig ? config.intervalSeconds : defaultConfig.intervalSeconds
    readonly property string maxPointBacklog: hasConfig ? config.maxPointBacklog : defaultConfig.maxPointBacklog
    readonly property string monitoringUrl: hasConfig ? config.monitoringUrl : defaultConfig.monitoringUrl
    readonly property string readinessUrl: hasConfig ? config.readinessUrl : defaultConfig.readinessUrl

    property var relayStates: []

    visibility: fullscreenEnabled ? Window.FullScreen : Window.Windowed

    Component.onCompleted: {
        relayStates = Array(relayCount).fill("auto")
    }

    onRelayCountChanged: {
        relayStates = Array(relayCount).fill("auto")
    }

    function relayNameForIndex(i) {
        let name = ""

        if (hasConfig && config.relayName)
            name = String(config.relayName(i)).trim()

        if (name === "Relay " + (i + 1))
            return ""

        return name.slice(0, 10)
    }

    function renameRelay(i, name) {
        let relayName = String(name).trim().slice(0, 10)

        if (hasConfig && config.setRelayName) {
            config.setRelayName(i, relayName)
        }
    }

    function commitRelayRename() {
        if (renamePopup.relayIndex >= 0)
            renameRelay(renamePopup.relayIndex, nameInput.text)

        nameInput.focus = false
        renamePopup.close()
    }

    function setRelayState(i, state) {
        let updated = relayStates.slice()
        updated[i] = state
        relayStates = updated
    }

    function setIntervalSeconds(value) {
        if (hasConfig && config.setIntervalSeconds) {
            config.setIntervalSeconds(value)
            settingsPage.intervalInputValue = config.intervalSeconds
        }
    }

    function setMaxPointBacklog(value) {
        if (hasConfig && config.setMaxPointBacklog) {
            config.setMaxPointBacklog(value)
            settingsPage.maxPointBacklogInputValue = config.maxPointBacklog
        }
    }

    function showPage(index) {
        swipeView.currentIndex = index
    }

    Connections {
        target: hasConfig ? config : null

        function onRelayNamesChanged() {
            controlsPage.refreshRelayModel()
        }

        function onRelayCountChanged() {
            controlsPage.refreshRelayModel()
            relayStates = Array(relayCount).fill("auto")
        }

        function onIntervalSecondsChanged() {
            settingsPage.intervalInputValue = config.intervalSeconds
        }

        function onMaxPointBacklogChanged() {
            settingsPage.maxPointBacklogInputValue = config.maxPointBacklog
        }
    }

    SwipeView {
        id: swipeView

        anchors.fill: parent
        interactive: currentIndex !== 1

        ControlsPage {
            id: controlsPage

            relayCount: root.relayCount
            relayStates: root.relayStates
            relayNameProvider: root.relayNameForIndex

            onRelayStateChanged: function(index, state) {
                root.setRelayState(index, state)
            }

            onRenameRelayRequested: function(index) {
                renamePopup.relayIndex = index
                renamePopup.open()
            }
        }

        Item {
            id: monitoringPageSlot

            Loader {
                id: monitoringPageLoader

                anchors.fill: parent
                active: swipeView.currentIndex === 1
                source: active ? "MonitoringPage.qml" : ""

                Binding {
                    target: monitoringPageLoader.item
                    property: "monitoringUrl"
                    value: root.monitoringUrl
                    when: monitoringPageLoader.status === Loader.Ready
                }

                Binding {
                    target: monitoringPageLoader.item
                    property: "refreshIntervalSeconds"
                    value: root.intervalSeconds
                    when: monitoringPageLoader.status === Loader.Ready
                }
            }
        }

        SettingsPage {
            id: settingsPage

            intervalSeconds: root.intervalSeconds
            maxPointBacklog: root.maxPointBacklog

            onIntervalCommitted: function(value) {
                root.setIntervalSeconds(value)
            }

            onMaxPointBacklogCommitted: function(value) {
                root.setMaxPointBacklog(value)
            }
        }
    }

    Item {
        id: monitoringSwipeRails

        z: 9
        anchors.fill: parent
        visible: swipeView.currentIndex === 1

        Rectangle {
            anchors.left: parent.left
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            width: 56
            color: "transparent"

            MouseArea {
                id: previousPageRail

                anchors.fill: parent
                preventStealing: true

                property real pressX: 0

                onPressed: pressX = mouse.x

                onReleased: {
                    if (mouse.x - pressX > 36)
                        root.showPage(0)
                }
            }
        }

        Rectangle {
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            width: 56
            color: "transparent"

            MouseArea {
                id: nextPageRail

                anchors.fill: parent
                preventStealing: true

                property real pressX: 0

                onPressed: pressX = mouse.x

                onReleased: {
                    if (pressX - mouse.x > 36)
                        root.showPage(2)
                }
            }
        }
    }

    Row {
        id: pageSelector

        z: 10
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.rightMargin: 20
        anchors.topMargin: 36
        spacing: 8

        Repeater {
            model: swipeView.count

            delegate: Rectangle {
                required property int index

                width: 10
                height: 10
                radius: 5
                color: swipeView.currentIndex === index ? "#222222" : "#d6d6d6"
                border.color: "#222222"
                border.width: swipeView.currentIndex === index ? 0 : 1

                MouseArea {
                    anchors.fill: parent

                    onClicked: root.showPage(index)
                }
            }
        }
    }

    NavigationDrawer {
        id: navigationDrawer

        anchors.fill: parent
        currentIndex: swipeView.currentIndex
        readinessRefreshIntervalSeconds: root.intervalSeconds
        readinessUrl: root.readinessUrl

        onControlsRequested: root.showPage(0)
        onMonitoringRequested: root.showPage(1)
        onSettingsRequested: root.showPage(2)
    }

    Popup {
        id: renamePopup

        modal: true
        focus: true
        anchors.centerIn: parent
        width: 300
        height: 180

        property int relayIndex: -1

        background: Rectangle {
            color: "#80000000"

            MouseArea {
                anchors.fill: parent

                onClicked: {
                    root.commitRelayRename()
                }
            }
        }

        contentItem: Rectangle {
            anchors.centerIn: parent
            width: 300
            height: 180
            color: "white"
            radius: 10

            Column {
                anchors.fill: parent
                anchors.margins: 16
                spacing: 12

                Text {
                    text: "Edit relay name"
                    font.pixelSize: 18
                    font.bold: true
                }

                TextField {
                    id: nameInput

                    placeholderText: "Enter name"
                    maximumLength: 10

                    Keys.onReturnPressed: root.commitRelayRename()
                    Keys.onEnterPressed: root.commitRelayRename()
                }

                Row {
                    spacing: 10
                    anchors.horizontalCenter: parent.horizontalCenter

                    Button {
                        text: "Cancel"

                        onClicked: {
                            nameInput.focus = false
                            renamePopup.close()
                        }
                    }

                    Button {
                        text: "OK"

                        onClicked: {
                            root.commitRelayRename()
                        }
                    }
                }
            }
        }

        onOpened: {
            nameInput.text = relayNameForIndex(relayIndex)
            nameInput.selectAll()
            nameInput.forceActiveFocus()
        }
    }
}
