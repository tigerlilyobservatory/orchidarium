import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    id: root

    property string intervalSeconds: "60"
    property string maxPointBacklog: "1000"
    property string intervalInputValue: intervalSeconds
    property string maxPointBacklogInputValue: maxPointBacklog

    signal intervalCommitted(string value)
    signal maxPointBacklogCommitted(string value)

    onIntervalSecondsChanged: intervalInputValue = intervalSeconds
    onMaxPointBacklogChanged: maxPointBacklogInputValue = maxPointBacklog

    function maxPointBacklogDisplayValue() {
        if (maxPointBacklogInputValue === "0")
            return "0 (infinite)"

        return maxPointBacklogInputValue
    }

    function normalizeIntegerText(value, minimum, fallback) {
        let textValue = String(value).trim()

        if (!/^[0-9]+$/.test(textValue))
            return fallback

        return String(Math.max(minimum, Number(textValue)))
    }

    function openIntervalEditor() {
        editPopup.settingName = "interval"
        editPopup.title = "Sensor collection interval"
        editPopup.minimumValue = 5
        editPopup.fallbackValue = intervalSeconds
        editPopup.draftValue = intervalInputValue
        editPopup.open()
    }

    function openMaxPointBacklogEditor() {
        editPopup.settingName = "backlog"
        editPopup.title = "Max point backlog"
        editPopup.minimumValue = 0
        editPopup.fallbackValue = maxPointBacklog
        editPopup.draftValue = maxPointBacklogInputValue
        editPopup.open()
    }

    function commitEditPopup() {
        let normalizedValue = normalizeIntegerText(editInput.text, editPopup.minimumValue, editPopup.fallbackValue)

        if (editPopup.settingName === "interval") {
            intervalInputValue = normalizedValue
            intervalCommitted(intervalInputValue)
        } else if (editPopup.settingName === "backlog") {
            maxPointBacklogInputValue = normalizedValue
            maxPointBacklogCommitted(maxPointBacklogInputValue)
        }

        editPopup.close()
    }

    Rectangle {
        anchors.fill: parent
        color: "#ffffff"

        ColumnLayout {
            anchors.fill: parent
            anchors.leftMargin: 28
            anchors.rightMargin: 28
            anchors.topMargin: 76
            anchors.bottomMargin: 28
            spacing: 18

            Text {
                Layout.fillWidth: true
                text: "Settings"
                color: "#222222"
                font.pixelSize: 28
                font.bold: true
            }

            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: 76
                color: "#ffffff"
                radius: 4
                border.color: "#d5d5d5"
                border.width: 1

                RowLayout {
                    anchors.fill: parent
                    anchors.leftMargin: 16
                    anchors.rightMargin: 12
                    spacing: 12

                    Text {
                        Layout.fillWidth: true
                        text: "Sensor collection interval: " + root.intervalInputValue + "s."
                        color: "#222222"
                        font.pixelSize: 16
                        verticalAlignment: Text.AlignVCenter
                        wrapMode: Text.WordWrap
                    }

                    Button {
                        Layout.preferredWidth: 88
                        Layout.preferredHeight: 42
                        text: "Edit"

                        onClicked: root.openIntervalEditor()
                    }
                }
            }

            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: 76
                color: "#ffffff"
                radius: 4
                border.color: "#d5d5d5"
                border.width: 1

                RowLayout {
                    anchors.fill: parent
                    anchors.leftMargin: 16
                    anchors.rightMargin: 12
                    spacing: 12

                    Text {
                        Layout.fillWidth: true
                        text: "Max point backlog: " + root.maxPointBacklogDisplayValue() + "."
                        color: "#222222"
                        font.pixelSize: 16
                        verticalAlignment: Text.AlignVCenter
                        wrapMode: Text.WordWrap
                    }

                    Button {
                        Layout.preferredWidth: 88
                        Layout.preferredHeight: 42
                        text: "Edit"

                        onClicked: root.openMaxPointBacklogEditor()
                    }
                }
            }

            Item {
                Layout.fillHeight: true
            }
        }
    }

    Popup {
        id: editPopup

        property string settingName: ""
        property string title: ""
        property int minimumValue: 0
        property string fallbackValue: ""
        property string draftValue: ""

        modal: true
        focus: true
        anchors.centerIn: parent
        width: Math.min(root.width - 56, 420)
        height: 230
        closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutside

        contentItem: Rectangle {
            anchors.fill: parent
            color: "#ffffff"
            radius: 4
            border.color: "#d5d5d5"
            border.width: 1

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 18
                spacing: 14

                Text {
                    Layout.fillWidth: true
                    text: editPopup.title
                    color: "#222222"
                    font.pixelSize: 20
                    font.bold: true
                }

                TextField {
                    id: editInput

                    Layout.fillWidth: true
                    text: editPopup.draftValue
                    inputMethodHints: Qt.ImhDigitsOnly
                    validator: IntValidator { bottom: editPopup.minimumValue }
                    selectByMouse: true

                    Keys.onReturnPressed: root.commitEditPopup()
                }

                RowLayout {
                    Layout.fillWidth: true
                    spacing: 10

                    Item {
                        Layout.fillWidth: true
                    }

                    Button {
                        Layout.preferredWidth: 92
                        text: "Cancel"

                        onClicked: editPopup.close()
                    }

                    Button {
                        Layout.preferredWidth: 92
                        text: "Save"

                        onClicked: root.commitEditPopup()
                    }
                }
            }
        }

        onOpened: {
            editInput.text = draftValue
            editInput.selectAll()
            editInput.forceActiveFocus()
        }
    }
}
