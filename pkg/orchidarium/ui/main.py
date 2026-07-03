# This Python file uses the following encoding: utf-8
from __future__ import annotations

import sys

from os import getenv
from pathlib import Path

from PySide6.QtGui import QFont, QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtWebEngineQuick import QtWebEngineQuick

from orchidarium.ui.config import Config


UI_FONT_FAMILY = 'Roboto'


def _initialize_webengine() -> None:
    """
    Initialize Qt WebEngine when a real display backend is available.
    """
    if getenv('QT_QPA_PLATFORM', '') == 'offscreen':
        return

    QtWebEngineQuick.initialize()


def run() -> None:
    """
    Run the Qt/QML UI.
    """
    _initialize_webengine()

    app = QGuiApplication(sys.argv)
    app.setFont(QFont(UI_FONT_FAMILY))

    engine = QQmlApplicationEngine()
    engine.addImportPath(str(Path(__file__).parent))

    config = Config(
        fullscreen=__name__ != '__main__',
        relay_count=8,
        relay_names={
            2: 'rain'
        }
    )
    engine.rootContext().setContextProperty("config", config)
    engine.loadFromModule("qml", "Main")

    if not engine.rootObjects():
        sys.exit(1)

    sys.exit(app.exec())


if __name__ == "__main__":
    run()
