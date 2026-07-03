import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtWebEngine

Item {
    id: root

    property string monitoringUrl: "https://grafana:3000"
    property string currentUrl: monitoringUrl
    property string refreshIntervalSeconds: "60"
    property int secondsUntilRefresh: refreshInterval()

    function normalizedUrl(value) {
        let nextUrl = String(value).trim()

        if (nextUrl.length === 0)
            return root.currentUrl

        if (!/^[A-Za-z][A-Za-z0-9+.-]*:\/\//.test(nextUrl))
            nextUrl = "https://" + nextUrl

        return nextUrl
    }

    function refreshInterval() {
        return Math.max(5, Math.round(Number(refreshIntervalSeconds) || 60))
    }

    function resetRefreshCountdown() {
        secondsUntilRefresh = refreshInterval()
    }

    function refreshPage() {
        grafanaView.reload()
        resetRefreshCountdown()
    }

    function loadUrl(value) {
        currentUrl = normalizedUrl(value)
        grafanaView.url = currentUrl
        resetRefreshCountdown()
    }

    onMonitoringUrlChanged: loadUrl(monitoringUrl)
    onRefreshIntervalSecondsChanged: resetRefreshCountdown()

    Timer {
        id: refreshTimer

        interval: 1000
        repeat: true
        running: true

        onTriggered: {
            if (root.secondsUntilRefresh <= 1) {
                root.refreshPage()
                return
            }

            root.secondsUntilRefresh -= 1
        }
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
            text: "Monitoring"
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
            spacing: 12

            RowLayout {
                Layout.fillWidth: true
                Layout.preferredHeight: 44

                Item {
                    Layout.fillWidth: true
                }

                Button {
                    Layout.preferredWidth: 132
                    Layout.preferredHeight: 42
                    text: "Reload in " + root.secondsUntilRefresh + "s"

                    onClicked: root.refreshPage()
                }
            }

            Rectangle {
                Layout.fillWidth: true
                Layout.fillHeight: true
                color: "#ffffff"
                border.color: "#d5d5d5"
                border.width: 1
                radius: 4
                clip: true

                WebEngineView {
                    id: grafanaView

                    anchors.fill: parent
                    anchors.margins: 1
                    url: root.currentUrl

                    onCertificateError: function(error) {
                        error.acceptCertificate()
                    }

                    onLoadingChanged: function(loadRequest) {
                        if (loadRequest.status === WebEngineView.LoadSucceededStatus)
                            root.currentUrl = String(url)
                    }
                }
            }
        }
    }
}
