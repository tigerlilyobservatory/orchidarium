import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    id: root

    property int relayCount: 4
    property var relayStates: []
    property var relayNameProvider: null

    signal relayStateChanged(int index, string state)
    signal renameRelayRequested(int index)

    function refreshRelayModel() {
        relayRepeater.model = 0
        relayRepeater.model = root.relayCount
    }

    function relayNameForIndex(i) {
        if (root.relayNameProvider)
            return root.relayNameProvider(i)

        return "Relay " + (i + 1)
    }

    function relayStateForIndex(i) {
        let state = root.relayStates[i]

        if (state === "on" || state === "auto" || state === "off")
            return state

        return "auto"
    }

    function sliderValueForState(state) {
        if (state === "on")
            return 0

        if (state === "auto")
            return 1

        return 2
    }

    function stateForSliderValue(value) {
        if (value < 0.5)
            return "on"

        if (value < 1.5)
            return "auto"

        return "off"
    }

    Rectangle {
        anchors.fill: parent
        color: "#ffffff"

        ColumnLayout {
            anchors.fill: parent
            anchors.leftMargin: 20
            anchors.rightMargin: 20
            anchors.topMargin: 76
            anchors.bottomMargin: 20
            spacing: 18

            Text {
                Layout.fillWidth: true
                text: "Relay states"
                color: "#222222"
                font.pixelSize: 28
                font.bold: true
            }

            Row {
                Layout.fillWidth: true
                Layout.fillHeight: true
                spacing: 10

                Repeater {
                    id: relayRepeater

                    model: root.relayCount

                    delegate: Column {
                        required property int index

                        width: (parent.width - ((root.relayCount - 1) * 10)) / root.relayCount
                        spacing: 12

                        Rectangle {
                            width: parent.width
                            height: 120
                            radius: 12

                            color: root.relayStateForIndex(index) === "on" ? "#4CAF50"
                                 : root.relayStateForIndex(index) === "off" ? "#F44336"
                                 : "#9E9E9E"

                            border.color: "#333333"
                            border.width: 2

                            MouseArea {
                                anchors.fill: parent

                                onPressAndHold: root.renameRelayRequested(index)
                            }

                            Column {
                                anchors.fill: parent
                                anchors.margins: 8
                                spacing: 6

                                Text {
                                    width: parent.width
                                    height: (parent.height - 6) / 2
                                    text: root.relayNameForIndex(index)
                                    color: "white"
                                    font.bold: true
                                    font.pixelSize: 22
                                    minimumPixelSize: 6
                                    fontSizeMode: Text.Fit
                                    horizontalAlignment: Text.AlignHCenter
                                    verticalAlignment: Text.AlignVCenter
                                    wrapMode: Text.NoWrap
                                    elide: Text.ElideRight
                                }

                                Text {
                                    width: parent.width
                                    height: (parent.height - 6) / 2
                                    text: root.relayStateForIndex(index).toUpperCase()
                                    color: "white"
                                    font.bold: true
                                    font.pixelSize: 28
                                    minimumPixelSize: 6
                                    fontSizeMode: Text.Fit
                                    horizontalAlignment: Text.AlignHCenter
                                    verticalAlignment: Text.AlignVCenter
                                    wrapMode: Text.NoWrap
                                    elide: Text.ElideRight
                                }
                            }
                        }

                        Slider {
                            id: relaySlider

                            property string currentRelayState: root.relayStateForIndex(index)

                            width: parent.width
                            from: 0
                            to: 2
                            stepSize: 1
                            snapMode: Slider.SnapAlways

                            Component.onCompleted: value = root.sliderValueForState(currentRelayState)

                            onCurrentRelayStateChanged: {
                                let nextValue = root.sliderValueForState(currentRelayState)

                                if (value !== nextValue)
                                    value = nextValue
                            }

                            onMoved: root.relayStateChanged(index, root.stateForSliderValue(value))
                        }

                        Row {
                            width: parent.width

                            Text {
                                text: "ON"
                                width: parent.width / 3
                                horizontalAlignment: Text.AlignLeft
                                color: "#333333"
                                font.pixelSize: 9
                                font.bold: true
                            }

                            Text {
                                text: "AUTO"
                                width: parent.width / 3
                                horizontalAlignment: Text.AlignHCenter
                                color: "#333333"
                                font.pixelSize: 9
                                font.bold: true
                            }

                            Text {
                                text: "OFF"
                                width: parent.width / 3
                                horizontalAlignment: Text.AlignRight
                                color: "#333333"
                                font.pixelSize: 9
                                font.bold: true
                            }
                        }
                    }
                }
            }
        }
    }
}
