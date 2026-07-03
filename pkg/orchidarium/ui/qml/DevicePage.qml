import QtQuick

Item {
    Rectangle {
        anchors.fill: parent
        color: "#ffffff"

        Text {
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.leftMargin: 76
            anchors.rightMargin: 76
            anchors.top: parent.top
            anchors.topMargin: 20
            height: 44
            text: "Device"
            color: "#222222"
            font.pixelSize: 28
            font.bold: true
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            elide: Text.ElideRight
        }
    }
}
