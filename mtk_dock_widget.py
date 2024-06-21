from PyQt5 import QtCore
from qgis.gui import QgsDockWidget

from .mtk_widget import MapToolKitWidget

class MapToolKitDockWidget(QgsDockWidget):
    def __init__(self):
        super().__init__()
        self.setAllowedAreas(QtCore.Qt.AllDockWidgetAreas)
        self.setFeatures(QgsDockWidget.DockWidgetMovable | QgsDockWidget.DockWidgetFloatable | QgsDockWidget.DockWidgetClosable)

        self.widget = MapToolKitWidget()
        self.setWidget(self.widget)
        