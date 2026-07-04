import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    id: root

    property int currentIndex: 0
    property bool deviceReady: false
    property bool deviceReadinessKnown: false
    property string readinessRefreshIntervalSeconds: "60"
    property string readinessUrl: "http://127.0.0.1:8085/ready"
    readonly property int readinessRefreshIntervalMs: Math.max(5000, (Number(readinessRefreshIntervalSeconds) || 60) * 1000)
    readonly property string deviceReadinessText: deviceReadinessKnown ? (deviceReady ? "Ready" : "Not ready") : "Checking"

    signal controlsRequested()
    signal monitoringRequested()
    signal settingsRequested()

    z: 20

    onReadinessUrlChanged: refreshReadiness()

    onReadinessRefreshIntervalSecondsChanged: {
        readinessTimer.restart()
        refreshReadiness()
    }

    function refreshReadiness() {
        if (readinessUrl.length === 0) {
            deviceReady = false
            deviceReadinessKnown = true
            return
        }

        let request = new XMLHttpRequest()

        request.onreadystatechange = function() {
            if (request.readyState !== 4)
                return

            deviceReadinessKnown = true
            deviceReady = request.status >= 200 && request.status < 300
        }

        request.onerror = function() {
            deviceReadinessKnown = true
            deviceReady = false
        }

        request.open("GET", readinessUrl)
        request.send()
    }

    ToolButton {
        id: menuButton

        z: 10
        width: 52
        height: 52
        anchors.left: parent.left
        anchors.top: parent.top
        anchors.margins: 12
        display: AbstractButton.IconOnly
        ToolTip.visible: hovered
        ToolTip.text: "Menu"

        background: Rectangle {
            color: menuButton.down ? "#d8d8d8"
                 : menuButton.hovered ? "#eeeeee"
                 : "#ffffff"
            radius: 4
            border.color: "#c7c7c7"
            border.width: 1
        }

        contentItem: Item {
            implicitWidth: 24
            implicitHeight: 24

            Column {
                anchors.centerIn: parent
                spacing: 5

                Repeater {
                    model: 3

                    Rectangle {
                        width: 24
                        height: 3
                        radius: 1.5
                        color: "#222222"
                    }
                }
            }
        }

        onClicked: navigationDrawer.open()
    }

    Drawer {
        id: navigationDrawer

        z: 20
        width: Math.min(root.width * 0.72, 280)
        height: root.height
        edge: Qt.LeftEdge
        modal: true
        interactive: true

        background: Rectangle {
            color: "#ffffff"
        }

        Item {
            id: drawerContents

            anchors.fill: parent
            anchors.margins: 16

            ColumnLayout {
                id: navigationLinks

                anchors.left: parent.left
                anchors.right: parent.right
                anchors.top: parent.top
                spacing: 8

                Item {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 18
                }

                Text {
                    Layout.fillWidth: true
                    text: "Orchidarium"
                    color: "#222222"
                    font.pixelSize: 22
                    font.bold: true
                }

                ItemDelegate {
                    Layout.fillWidth: true
                    text: "Hardware"
                    highlighted: root.currentIndex === 0

                    onClicked: {
                        root.controlsRequested()
                        navigationDrawer.close()
                    }
                }

                ItemDelegate {
                    Layout.fillWidth: true
                    text: "Monitoring"
                    highlighted: root.currentIndex === 1

                    onClicked: {
                        root.monitoringRequested()
                        navigationDrawer.close()
                    }
                }

                ItemDelegate {
                    Layout.fillWidth: true
                    text: "Settings"
                    highlighted: root.currentIndex === 2

                    onClicked: {
                        root.settingsRequested()
                        navigationDrawer.close()
                    }
                }
            }

            Rectangle {
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.bottom: deviceDelegate.top
                anchors.bottomMargin: 8
                height: 1
                color: "#eeeeee"
            }

            ItemDelegate {
                id: deviceDelegate

                anchors.left: parent.left
                anchors.right: parent.right
                anchors.bottom: parent.bottom
                height: 56
                highlighted: false
                implicitHeight: 56
                ToolTip.visible: hovered
                ToolTip.text: "Readiness: " + root.deviceReadinessText

                contentItem: RowLayout {
                    spacing: 10

                    Text {
                        text: "Device"
                        color: "#222222"
                        font.pixelSize: 16
                        verticalAlignment: Text.AlignVCenter
                    }

                    Rectangle {
                        Layout.preferredWidth: readinessLabel.implicitWidth + 18
                        Layout.preferredHeight: 24
                        radius: 12
                        color: root.deviceReady ? "#2e7d32" : "#c62828"

                        Text {
                            id: readinessLabel

                            anchors.centerIn: parent
                            text: root.deviceReadinessText
                            color: "#ffffff"
                            font.pixelSize: 11
                            font.bold: true
                        }
                    }

                    Item {
                        Layout.fillWidth: true
                    }
                }

                onClicked: {
                    root.refreshReadiness()
                }
            }
        }
    }

    Timer {
        id: readinessTimer

        interval: root.readinessRefreshIntervalMs
        repeat: true
        running: true
        triggeredOnStart: true

        onTriggered: root.refreshReadiness()
    }
}
