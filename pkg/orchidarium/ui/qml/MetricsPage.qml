import QtQuick

Item {
    Rectangle {
        anchors.fill: parent
        color: "#ffffff"

        Text {
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.leftMargin: 76
            anchors.rightMargin: 20
            anchors.top: parent.top
            anchors.topMargin: 20
            height: 44
            text: "Metrics"
            color: "#222222"
            font.pixelSize: 28
            font.bold: true
            verticalAlignment: Text.AlignVCenter
            elide: Text.ElideRight
        }
    }
}
