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

    function normalizeIntegerText(value, minimum, fallback) {
        let textValue = String(value).trim()

        if (!/^[0-9]+$/.test(textValue))
            return fallback

        return String(Math.max(minimum, Number(textValue)))
    }

    function commitIntervalInput() {
        intervalInputValue = normalizeIntegerText(intervalInputValue, 5, intervalSeconds)
        intervalCommitted(intervalInputValue)
    }

    function commitMaxPointBacklogInput() {
        maxPointBacklogInputValue = normalizeIntegerText(maxPointBacklogInputValue, 0, maxPointBacklog)
        maxPointBacklogCommitted(maxPointBacklogInputValue)
    }

    Rectangle {
        anchors.fill: parent
        color: "#eeeeee"

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

            ColumnLayout {
                Layout.fillWidth: true
                spacing: 8

                Text {
                    Layout.fillWidth: true
                    text: "Collection interval (s)"
                    color: "#333333"
                    font.pixelSize: 16
                    font.bold: true
                }

                TextField {
                    id: intervalInput

                    Layout.fillWidth: true
                    text: root.intervalInputValue
                    placeholderText: "Seconds"
                    inputMethodHints: Qt.ImhDigitsOnly
                    validator: IntValidator { bottom: 5 }
                    selectByMouse: true

                    onTextEdited: root.intervalInputValue = text
                    onEditingFinished: root.commitIntervalInput()
                    Keys.onReturnPressed: root.commitIntervalInput()
                }
            }

            ColumnLayout {
                Layout.fillWidth: true
                spacing: 8

                Text {
                    Layout.fillWidth: true
                    text: "Max point backlog"
                    color: "#333333"
                    font.pixelSize: 16
                    font.bold: true
                }

                TextField {
                    id: maxPointBacklogInput

                    Layout.fillWidth: true
                    text: root.maxPointBacklogInputValue
                    placeholderText: "0 means infinite"
                    inputMethodHints: Qt.ImhDigitsOnly
                    validator: IntValidator { bottom: 0 }
                    selectByMouse: true

                    onTextEdited: root.maxPointBacklogInputValue = text
                    onEditingFinished: root.commitMaxPointBacklogInput()
                    Keys.onReturnPressed: root.commitMaxPointBacklogInput()
                }
            }

            Item {
                Layout.fillHeight: true
            }
        }
    }
}
