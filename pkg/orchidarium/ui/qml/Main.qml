import QtQuick
import QtQuick.Window
import QtQuick.Controls
import QtQuick.Layouts

Window {
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

    visibility: fullscreenEnabled ? Window.FullScreen : Window.Windowed

    property var relayStates: []

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

    Connections {
        target: hasConfig ? config : null

        function onRelayNamesChanged() {
            relayRepeater.model = 0
            relayRepeater.model = relayCount
        }

        function onRelayCountChanged() {
            relayRepeater.model = 0
            relayRepeater.model = relayCount
            relayStates = Array(relayCount).fill("auto")
        }

        function onIntervalSecondsChanged() {
            intervalInput.text = config.intervalSeconds
        }

        function onMaxPointBacklogChanged() {
            maxPointBacklogInput.text = config.maxPointBacklog
        }
    }

    SwipeView {
        id: swipeView
        anchors.fill: parent

        Item {
            Row {
                anchors.fill: parent
                anchors.margins: 20
                spacing: 10

                Repeater {
                    id: relayRepeater
                    model: relayCount

                    delegate: Column {
                        required property int index

                        width: (parent.width - ((relayCount - 1) * 10)) / relayCount
                        spacing: 12

                        Rectangle {
                            width: parent.width
                            height: 120
                            radius: 12

                            color: relayStates[index] === "on" ? "#4CAF50"
                                 : relayStates[index] === "off" ? "#F44336"
                                 : "#9E9E9E"

                            border.color: "#333333"
                            border.width: 2

                            MouseArea {
                                anchors.fill: parent
                                onPressAndHold: {
                                    renamePopup.relayIndex = index
                                    renamePopup.open()
                                }
                            }

                            Column {
                                anchors.fill: parent
                                anchors.margins: 8
                                spacing: 6

                                Text {
                                    width: parent.width
                                    height: (parent.height - 6) / 2
                                    text: relayNameForIndex(index)
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
                                    text: relayStates[index].toUpperCase()
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

                            property string currentRelayState: relayStates[index]

                            width: parent.width
                            from: 0
                            to: 2
                            stepSize: 1
                            snapMode: Slider.SnapAlways

                            Component.onCompleted: value = sliderValueForState(currentRelayState)

                            onCurrentRelayStateChanged: {
                                let nextValue = sliderValueForState(currentRelayState)
                                if (value !== nextValue)
                                    value = nextValue
                            }

                            onMoved: setRelayState(index, stateForSliderValue(value))
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

        Item {
            Rectangle {
                anchors.fill: parent
                color: "#eeeeee"

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 28
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
                            text: "Collection interval"
                            color: "#333333"
                            font.pixelSize: 16
                            font.bold: true
                        }

                        TextField {
                            id: intervalInput
                            Layout.fillWidth: true
                            text: intervalSeconds
                            placeholderText: "Seconds"
                            inputMethodHints: Qt.ImhDigitsOnly
                            validator: IntValidator { bottom: 5 }
                            selectByMouse: true

                            onEditingFinished: {
                                if (hasConfig) {
                                    config.setIntervalSeconds(text)
                                    text = config.intervalSeconds
                                }
                            }
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
                            text: maxPointBacklog
                            placeholderText: "0 means infinite"
                            inputMethodHints: Qt.ImhDigitsOnly
                            validator: IntValidator { bottom: 0 }
                            selectByMouse: true

                            onEditingFinished: {
                                if (hasConfig) {
                                    config.setMaxPointBacklog(text)
                                    text = config.maxPointBacklog
                                }
                            }
                        }
                    }

                    Item {
                        Layout.fillHeight: true
                    }
                }
            }
        }
    }

    Popup {
        id: renamePopup
        modal: true
        focus: true
        anchors.centerIn: parent
        width: 300
        height: 180

        property int relayIndex: -1

        // 👇 catches clicks outside content
        background: Rectangle {
            color: "#80000000" // semi-transparent dark overlay

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

        // 👇 actual popup content
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
