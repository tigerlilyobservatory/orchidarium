import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    id: root

    property int currentIndex: 0

    signal controlsRequested()
    signal settingsRequested()

    z: 20

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

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 16
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
                text: "Controls"
                highlighted: root.currentIndex === 0

                onClicked: {
                    root.controlsRequested()
                    navigationDrawer.close()
                }
            }

            ItemDelegate {
                Layout.fillWidth: true
                text: "Settings"
                highlighted: root.currentIndex === 1

                onClicked: {
                    root.settingsRequested()
                    navigationDrawer.close()
                }
            }

            Item {
                Layout.fillHeight: true
            }
        }
    }
}
