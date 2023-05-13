from .core.NdsUtil import NdsUtil

from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtWidgets import *
from PyQt5.QtWidgets import *
from qgis.core import *
from qgis.gui import *

if __name__ == '__main__':
    print('hello world')

    tiles = '557005127,557005138,557005139,557005133,557005144,557005145,557005135,557005146,557005147'
    tiles = list(map(lambda x : int(x.strip()), tiles.strip().split(',')))

    for tileid in tiles:
        p = NdsUtil.get_tile_polygon_of_deg(tileid)
        points = list(map(lambda l : QgsPointXY(l[0], l[1]), NdsUtil.get_tile_polygon_of_deg(tileid)))
        polygon = QgsPolygon([points])