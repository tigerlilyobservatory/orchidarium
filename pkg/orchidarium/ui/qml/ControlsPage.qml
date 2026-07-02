import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    id: root

    property int relayCount: 4
    property var relayStates: []
    property var relayNameProvider: null
    property bool relaysFrozen: false
    property var frozenRelayStates: []
    property var relayOverrideActive: []
    property var relayRestoreStates: []
    readonly property real relayContentOpacity: relaysFrozen ? 0.38 : 1.0

    signal relayStateChanged(int index, string state)
    signal renameRelayRequested(int index)

    onRelayCountChanged: resetRelayOverrides()

    function refreshRelayModel() {
        relayRepeater.model = 0
        relayRepeater.model = root.relayCount
    }

    function resetRelayOverrides() {
        root.relaysFrozen = false
        root.frozenRelayStates = []
        root.relayOverrideActive = Array(root.relayCount).fill(false)
        root.relayRestoreStates = Array(root.relayCount).fill("auto")
    }

    function ensureRelayOverrideState() {
        if (root.relayOverrideActive.length !== root.relayCount)
            root.relayOverrideActive = Array(root.relayCount).fill(false)

        if (root.relayRestoreStates.length !== root.relayCount)
            root.relayRestoreStates = Array(root.relayCount).fill("auto")
    }

    function relayNameForIndex(i) {
        if (root.relayNameProvider)
            return String(root.relayNameProvider(i)).slice(0, 10)

        return ""
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

    function clearRelayOverride(index) {
        ensureRelayOverrideState()

        let overrides = root.relayOverrideActive.slice()
        let restoreStates = root.relayRestoreStates.slice()

        overrides[index] = false
        restoreStates[index] = "auto"

        root.relayOverrideActive = overrides
        root.relayRestoreStates = restoreStates
    }

    function toggleRelayOverride(index) {
        if (root.relaysFrozen)
            return

        ensureRelayOverrideState()

        let overrides = root.relayOverrideActive.slice()
        let restoreStates = root.relayRestoreStates.slice()

        if (overrides[index]) {
            root.relayStateChanged(index, restoreStates[index])
            overrides[index] = false
            restoreStates[index] = "auto"
        } else {
            restoreStates[index] = root.relayStateForIndex(index)
            overrides[index] = true
            root.relayStateChanged(index, "off")
        }

        root.relayOverrideActive = overrides
        root.relayRestoreStates = restoreStates
    }

    function setRelayFromSlider(index, value) {
        clearRelayOverride(index)
        root.relayStateChanged(index, root.stateForSliderValue(value))
    }

    function toggleRelayFreeze() {
        if (root.relaysFrozen) {
            for (let restoreIndex = 0; restoreIndex < root.relayCount; restoreIndex += 1)
                root.relayStateChanged(restoreIndex, root.frozenRelayStates[restoreIndex] || "auto")

            root.relaysFrozen = false
            root.frozenRelayStates = []
            resetRelayOverrides()
            return
        }

        let frozenStates = []

        for (let freezeIndex = 0; freezeIndex < root.relayCount; freezeIndex += 1)
            frozenStates.push(root.relayStateForIndex(freezeIndex))

        resetRelayOverrides()
        root.frozenRelayStates = frozenStates
        root.relaysFrozen = true

        for (let offIndex = 0; offIndex < root.relayCount; offIndex += 1)
            root.relayStateChanged(offIndex, "off")
    }

    Rectangle {
        anchors.fill: parent
        color: "#ffffff"

        Text {
            id: pageTitle

            anchors.left: parent.left
            anchors.right: parent.right
            anchors.leftMargin: 76
            anchors.rightMargin: 20
            anchors.top: parent.top
            anchors.topMargin: 20
            height: 44
            text: "Hardware"
            color: "#222222"
            font.pixelSize: 28
            font.bold: true
            verticalAlignment: Text.AlignVCenter
            elide: Text.ElideRight
        }

        ColumnLayout {
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: pageTitle.bottom
            anchors.bottom: parent.bottom
            anchors.leftMargin: 20
            anchors.rightMargin: 20
            anchors.topMargin: 18
            anchors.bottomMargin: 20
            spacing: 18

            Text {
                id: relaySectionTitle

                Layout.fillWidth: true
                text: "Relays"
                color: root.relaysFrozen ? "#9a9a9a" : "#333333"
                font.pixelSize: 18
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
                            opacity: root.relayContentOpacity

                            border.color: "#333333"
                            border.width: 2

                            MouseArea {
                                id: relayButtonMouseArea

                                property bool renameRequested: false

                                anchors.fill: parent

                                onPressed: renameRequested = false

                                onClicked: {
                                    if (!renameRequested)
                                        root.toggleRelayOverride(index)
                                }

                                onPressAndHold: {
                                    renameRequested = true
                                    root.renameRelayRequested(index)
                                }
                            }

                            Column {
                                anchors.fill: parent
                                anchors.margins: 8
                                spacing: 4

                                Text {
                                    width: parent.width
                                    height: (parent.height - 8) / 3
                                    text: root.relayNameForIndex(index)
                                    color: "white"
                                    font.bold: true
                                    font.pixelSize: 18
                                    minimumPixelSize: 6
                                    fontSizeMode: Text.Fit
                                    horizontalAlignment: Text.AlignHCenter
                                    verticalAlignment: Text.AlignVCenter
                                    wrapMode: Text.NoWrap
                                    elide: Text.ElideRight
                                }

                                Text {
                                    width: parent.width
                                    height: (parent.height - 8) / 3
                                    text: String(index + 1)
                                    color: "white"
                                    font.bold: true
                                    font.pixelSize: 24
                                    minimumPixelSize: 6
                                    fontSizeMode: Text.Fit
                                    horizontalAlignment: Text.AlignHCenter
                                    verticalAlignment: Text.AlignVCenter
                                    wrapMode: Text.NoWrap
                                    elide: Text.ElideRight
                                }

                                Text {
                                    width: parent.width
                                    height: (parent.height - 8) / 3
                                    text: root.relayStateForIndex(index).toUpperCase()
                                    color: "white"
                                    font.bold: true
                                    font.pixelSize: 24
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
                            enabled: !root.relaysFrozen

                            Component.onCompleted: value = root.sliderValueForState(currentRelayState)

                            onCurrentRelayStateChanged: {
                                let nextValue = root.sliderValueForState(currentRelayState)

                                if (value !== nextValue)
                                    value = nextValue
                            }

                            onMoved: root.setRelayFromSlider(index, value)
                        }

                        Row {
                            width: parent.width
                            opacity: root.relayContentOpacity

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

                        Button {
                            width: parent.width
                            height: 36
                            text: "Edit"

                            onClicked: root.renameRelayRequested(index)
                        }
                    }
                }
            }

            Button {
                Layout.fillWidth: true
                Layout.preferredHeight: 54
                text: root.relaysFrozen ? "Resume Relays" : "Freeze Relays"

                onClicked: root.toggleRelayFreeze()
            }
        }
    }
}
