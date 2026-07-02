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
        maxPointBacklog: "1000"
    })

    readonly property bool hasConfig: typeof config !== "undefined" && config !== null
    readonly property bool fullscreenEnabled: hasConfig ? config.fullscreen : defaultConfig.fullscreen
    readonly property int relayCount: hasConfig ? config.relayCount : defaultConfig.relayCount
    readonly property string intervalSeconds: hasConfig ? config.intervalSeconds : defaultConfig.intervalSeconds
    readonly property string maxPointBacklog: hasConfig ? config.maxPointBacklog : defaultConfig.maxPointBacklog

    property var relayStates: []

    visibility: fullscreenEnabled ? Window.FullScreen : Window.Windowed

    Component.onCompleted: {
        relayStates = Array(relayCount).fill("auto")
    }

    onRelayCountChanged: {
        relayStates = Array(relayCount).fill("auto")
    }

    function relayNameForIndex(i) {
        if (hasConfig && config.relayName)
            return config.relayName(i)

        return "Relay " + (i + 1)
    }

    function renameRelay(i, name) {
        if (hasConfig && config.setRelayName) {
            config.setRelayName(i, name)
        }
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

    NavigationDrawer {
        id: navigationDrawer

        anchors.fill: parent
        currentIndex: swipeView.currentIndex

        onControlsRequested: root.showPage(0)
        onSettingsRequested: root.showPage(1)
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
                    if (renamePopup.relayIndex >= 0) {
                        renameRelay(renamePopup.relayIndex, nameInput.text)
                    }

                    nameInput.focus = false
                    renamePopup.close()
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
                    text: "Rename Relay"
                    font.pixelSize: 18
                    font.bold: true
                }

                TextField {
                    id: nameInput

                    placeholderText: "Enter name"
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
                        text: "Save"

                        onClicked: {
                            if (renamePopup.relayIndex >= 0) {
                                renameRelay(renamePopup.relayIndex, nameInput.text)
                            }

                            nameInput.focus = false
                            renamePopup.close()
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
