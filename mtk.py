# -*- coding: utf-8 -*-
"""
/***************************************************************************
 MapToolKit
                                 A QGIS plugin
 lesteryan map tool kit
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2023-04-26
        git sha              : $Format:%H$
        copyright            : (C) 2023 by lesteryan
        email                : cgmsyx@163.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtWidgets import *
from PyQt5.QtWidgets import *
from qgis.core import *
from qgis.gui import *
# from QtCore.Qt import DockWidgetArea
# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .mtk_dock_widget import MapToolKitDockWidget
import os.path
import urllib
import json

from .core.NdsUtil import NdsUtil
from .core.MerTileUtil import MerTileUtil
from .core.QgsCoordTrans import QgsCoordTrans


class MapToolKit:
    """QGIS Plugin Implementation."""

    epsg_id_wgs84 = 'EPSG:4326'
    epsg_id_webmercator = 'EPSG:3857'
    supported_coords = [QgsCoordTrans.COORD.COORD_WGS84, QgsCoordTrans.COORD.COORD_GCJ02, QgsCoordTrans.COORD.COORD_WEBMERCATOR]
    xyz_layers = {
        '': '',
        'amap vector':'http://webrd03.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=8&x={x}&y={y}&z={z}',
        'amap satelite':'https://webst03.is.autonavi.com/appmaptile?style=6&x={x}&y={y}&z={z}',
        'osm vector':'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
        }

    def __init__(self, iface : QgisInterface):
        self.iface = iface
        self.canvas = iface.mapCanvas()
      
        self.task_manager = QgsApplication.taskManager()
        self.plugin_dir = os.path.dirname(__file__)

        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'MapToolKit_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        self.actions = []
        self.menu = self.tr(u'&MapToolKit')

    def tr(self, message):
        return QCoreApplication.translate('MapToolKit', message)

    def initGui(self):
        self.dlg = MapToolKitDockWidget()
        self.iface.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.dlg)

        self.widget = self.dlg.widget
        self.map_tool = None

        self.widget.combo_simple_coordstype.addItems(self.supported_coords)
        self.widget.combo_wkt_coordstype.addItems(self.supported_coords)
        self.widget.combo_geojson_coordstype.addItems(self.supported_coords)
        self.widget.combo_coords_a.addItems(self.supported_coords)
        self.widget.combo_coords_b.addItems(self.supported_coords)
        self.widget.combo_coords_a.setCurrentIndex(0)
        self.widget.combo_coords_b.setCurrentIndex(1)

        self.widget.combo_xyzlayer_layertype.addItems(list(self.xyz_layers.keys()))
        self.widget.combo_xyzlayer_layertype.currentIndexChanged.connect(self.combo_xyz_index_changed)
        self.widget.button_xyzlayer_draw.clicked.connect(self.button_xyz_layer_add_clicked)

        self.widget.button_draw_nds_wgs84.clicked.connect(self.button_draw_nds_wgs84_clicked)
        self.widget.button_draw_nds_gcj02.clicked.connect(self.button_draw_nds_gcj02_clicked)
        self.widget.button_get_bound_tile.clicked.connect(self.button_get_bound_tile_clicked)

        self.widget.button_draw_mer_tile.clicked.connect(self.button_draw_mer_tile_clicked)
        self.widget.button_get_bound_mer_tile.clicked.connect(self.button_get_bound_mer_tile_clicked)

        self.widget.button_draw_coordpick_point.clicked.connect(self.button_coordpick_point_cliked)
        self.widget.button_draw_coordpick_line.clicked.connect(self.button_coordpick_line_cliked)
        self.widget.button_draw_coordpick_polygon.clicked.connect(self.button_coordpick_polygon_cliked)

        self.widget.button_draw_wkt.clicked.connect(self.button_draw_wkt_clicked)
        self.widget.button_draw_wkb.clicked.connect(self.button_draw_wkb_clicked)

        self.widget.button_draw_geojson.clicked.connect(self.button_draw_geojson_clicked)

        self.widget.button_coordstrans_a2b.clicked.connect(self.button_coordtransform_a2b_clicked)
        self.widget.button_coordstrans_b2a.clicked.connect(self.button_coordtransform_b2a_clicked)

        self.widget.button_draw_point.clicked.connect(self.button_draw_point_clicked)
        self.widget.button_draw_line.clicked.connect(self.button_draw_line_clicked)
        self.widget.button_draw_polygon.clicked.connect(self.button_draw_polygon_clicked)

        self.canvas.extentsChanged.connect(self.handleLayerExtentChanged)

    def unload(self):
        self.iface.removeDockWidget(self.dlg)
        if self.map_tool is not None:
            self.canvas.unsetMapTool(self.map_tool)

    def button_coordpick_point_cliked(self):
        if self.map_tool is not None:
            self.map_tool.draw_finish_event.disconnect(self.coordpick_finished)

        self.map_tool = DrawTool(self.canvas, QgsWkbTypes.PointGeometry)
        self.map_tool.draw_finish_event.connect(self.coordpick_finished)
        self.canvas.setMapTool(self.map_tool)

    def button_coordpick_line_cliked(self):
        if self.map_tool is not None:
            self.map_tool.draw_finish_event.disconnect(self.coordpick_finished)

        self.map_tool = DrawTool(self.canvas, QgsWkbTypes.LineGeometry)
        self.map_tool.draw_finish_event.connect(self.coordpick_finished)
        self.canvas.setMapTool(self.map_tool)

    def button_coordpick_polygon_cliked(self):
        if self.map_tool is not None:
            self.map_tool.draw_finish_event.disconnect(self.coordpick_finished)

        self.map_tool = DrawTool(self.canvas, QgsWkbTypes.PolygonGeometry)
        self.map_tool.draw_finish_event.connect(self.coordpick_finished)
        self.canvas.setMapTool(self.map_tool)

    def coordpick_finished(self, geometry: QgsGeometry):
        if not geometry.isEmpty():
            points = QgsCoordTrans.get_geometry_points(geometry)
            points_str = ','.join(list(map(lambda l : f'{l.x()},{l.y()}', points)))
            self.widget.text_simple_content.setPlainText(points_str)
            self.widget.tab_layer.setCurrentIndex(2)
            self.widget.text_wkt_content.setPlainText(geometry.asWkt())
            self.widget.text_geojson_content.setPlainText(json.dumps(json.loads(geometry.asJson()), indent=4))

    def handleLayerExtentChanged(self, layer = None):
        if self.canvas.scale() > 194089792:
            reply = QMessageBox.question(self.dlg, 'tips', 'canvas scale too large, go to default zoom ?', QMessageBox.Yes | QMessageBox.No | QMessageBox.NoToAll, QMessageBox.Yes)

            if reply == QMessageBox.Yes:
                self.canvas.setExtent(QgsRectangle(12962995,4853260,12963803,4853649))

        scale = self.canvas.scale()
        if self.widget.checkbox_tile_draw_with_zoom.isChecked():
            level = self.widget.spin_tile_level.value()
            nds_layers = QgsProject.instance().mapLayersByShortName('nds')
            num = int(scale / pow(2, level))
            if len(nds_layers) != 0 and num < 1000:
                nds_layer = nds_layers[0]
                request = QgsFeatureRequest().setFilterRect(self.canvas.extent())
                features = nds_layer.getFeatures(request)
                exist_tile_ids = set(map(lambda l : str(l.attributeMap()['tid']), features))

                extent = self.iface.mapCanvas().extent()
                crs = nds_layer.crs()
                if(crs.authid() != self.epsg_id_wgs84):
                    transform = QgsCoordinateTransform(crs, QgsCoordinateReferenceSystem(self.epsg_id_wgs84), QgsProject.instance())
                    extent = transform.transform(extent)
        
                x1, y1, x2, y2 = extent.xMinimum(), extent.yMinimum(), extent.xMaximum(), extent.yMaximum()
                
                tile_ids = NdsUtil.get_bound_tileids(x1, y1, x2, y2, level)
                tile_ids = list(map(lambda l : str(l), tile_ids))
                tile_ids = list(filter(lambda l : l not in exist_tile_ids, tile_ids))

                if len(tile_ids) != 0:
                    tile_ids_str = ','.join(tile_ids)
                    self.draw_nds_tile_by_layer(nds_layer, tile_ids_str, QgsCoordTrans.COORD.COORD_WGS84)
        elif self.widget.checkbox_mer_tile_draw_with_zoom.isChecked():
            mer_layers = QgsProject.instance().mapLayersByShortName('mer_tile')
            level = self.widget.spin_mer_tile_level.value()
            num = int(scale / pow(2, level))
            if len(mer_layers) != 0 and num < 1000:
                mer_layer = mer_layers[0]
                
                request = QgsFeatureRequest().setFilterRect(self.canvas.extent())
                features = mer_layer.getFeatures(request)
                exist_tile_ids = set(map(lambda l : str(l.attributeMap()['tid']), features))

                extent = self.iface.mapCanvas().extent()

                x1, y1, x2, y2 = extent.xMinimum(), extent.yMinimum(), extent.xMaximum(), extent.yMaximum()
                
                tile_ids = MerTileUtil.get_tiles(x1, y1, x2, y2, level)
                tile_ids = list(map(lambda l : str(l), tile_ids))

                tile_ids = list(filter(lambda l : l not in exist_tile_ids, tile_ids))

                if len(tile_ids) != 0:
                    tile_ids_str = ','.join(tile_ids)
                    self.draw_mer_tile_by_layer(mer_layer, tile_ids_str)

        
    def draw_nds_tile_by_layer(self, nds_layer: QgsVectorLayer, tileid_str: str, coords_sys: str): 
        if(len(tileid_str) == 0):
            self.iface.messageBar().pushMessage("Error", "invalid nds string", level=Qgis.Critical)
            return 

        fields = QgsFields()
        fields.append(QgsField("tid", QVariant.String))
        fields.append(QgsField("level", QVariant.Int))
        
        pr = nds_layer.dataProvider()

        for n in range(pr.fields().count()):
            QgsMessageLog.logMessage(f'pr fields {n} {pr.fields()[n].name()}')

        tiles = list(map(lambda x : int(x.strip()), tileid_str.strip().split(',')))
        for tileid in tiles:
            level = NdsUtil.get_tile_level(tileid)
            p = NdsUtil.get_tile_polygon_of_deg(tileid)

            points = list(map(lambda l : QgsPointXY(l[0], l[1]), p))
            polygon = QgsGeometry.fromPolygonXY([points])
            polygon = QgsCoordTrans.geometry_trans(polygon, coords_sys, QgsCoordTrans.COORD.COORD_WGS84)

            feature = QgsFeature(fields, tileid)
            feature.setGeometry(polygon)
            feature['tid'] = str(tileid)
            feature['level'] = level

            pr.addFeature(feature)
        
        nds_layer.updateExtents()

    def draw_mer_tile_by_layer(self, mer_layer: QgsVectorLayer, tileid_str: str): 
        if(len(tileid_str) == 0):
            self.iface.messageBar().pushMessage("Error", "invalid nds string", level=Qgis.Critical)
            return 

        fields = QgsFields()
        fields.append(QgsField("tid", QVariant.String))
        fields.append(QgsField("level", QVariant.Int))
        
        pr = mer_layer.dataProvider()

        tiles = list(map(lambda x : int(x.strip()), tileid_str.strip().split(',')))
        for tileid in tiles:
            level = tileid >> 56
            p = MerTileUtil.get_tile_polygon(tileid)
            
            points = list(map(lambda l : QgsPointXY(l[0], l[1]), p))

            polygon = QgsGeometry.fromPolygonXY([points])

            feature = QgsFeature(fields, tileid)
            feature.setGeometry(polygon)
            feature['tid'] = str(tileid)
            feature['level'] = level

            pr.addFeature(feature)
        
        mer_layer.updateExtents()

    def create_nds_layer(self, layer_name: str, repeate: bool = False):
        layers = QgsProject.instance().mapLayersByName(layer_name)
        if layers != None and len(layers) != 0 and not repeate:
            return layers[0]

        nds_layer = QgsVectorLayer(f'Polygon?crs={self.epsg_id_wgs84}', layer_name, 'memory')
        nds_layer.setShortName('nds')
        symbol = QgsFillSymbol.createSimple({'color': '#00000000', 'style': 'solid', 'outline_color': 'red', 'stroke_width': '1'})
        nds_layer.renderer().setSymbol(symbol)
        
        pr = nds_layer.dataProvider()
        ret = pr.addAttributes([QgsField("tid", QVariant.String), QgsField("level", QVariant.Int)])
        nds_layer.updateFields()

        layer_settings = QgsPalLayerSettings()
        text_format = QgsTextFormat()
        text_format.setColor(QColor("red"))
        layer_settings.setFormat(text_format)
        layer_settings.fieldName = "tid"
        layer_settings.placement = QgsPalLayerSettings.AroundPoint
        layer_settings.enabled = True
        labels = QgsVectorLayerSimpleLabeling(layer_settings)

        nds_layer.setLabeling(labels)
        nds_layer.setLabelsEnabled(True)

        QgsProject.instance().addMapLayer(nds_layer)

        return nds_layer
    
    def create_mer_tile_layer(self, layer_name: str, repeate: bool = False):
        layers = QgsProject.instance().mapLayersByName(layer_name)
        if layers != None and len(layers) != 0 and not repeate:
            return layers[0]

        mer_layer = QgsVectorLayer(f'Polygon?crs={self.epsg_id_webmercator}', layer_name, 'memory')
        mer_layer.setShortName('mer_tile')
        symbol = QgsFillSymbol.createSimple({'color': '#00000000', 'style': 'solid', 'outline_color': 'red', 'stroke_width': '1'})
        mer_layer.renderer().setSymbol(symbol)
        
        pr = mer_layer.dataProvider()
        ret = pr.addAttributes([QgsField("tid", QVariant.String), QgsField("level", QVariant.Int)])
        mer_layer.updateFields()

        layer_settings = QgsPalLayerSettings()
        text_format = QgsTextFormat()
        text_format.setColor(QColor("red"))
        layer_settings.setFormat(text_format)
        layer_settings.fieldName = "tid"
        layer_settings.placement = QgsPalLayerSettings.AroundPoint
        layer_settings.enabled = True
        labels = QgsVectorLayerSimpleLabeling(layer_settings)

        mer_layer.setLabeling(labels)
        mer_layer.setLabelsEnabled(True)

        QgsProject.instance().addMapLayer(mer_layer)

        return mer_layer

    def button_draw_mer_tile_clicked(self):
        layer_name = self.widget.edit_mer_tile_layer_name.text()
        tileid_str = self.widget.text_mer_tile_content.toPlainText()

        mer_layer = create_mer_tile_layer(layer_name)

        self.draw_mer_tile_by_layer(mer_layer, tileid_str)

    def button_draw_nds_wgs84_clicked(self):
        layer = self.create_nds_layer(self.widget.edit_tile_layer_name.text())
        self.draw_nds_tile_by_layer(layer, self.widget.text_tile_content.toPlainText(), QgsCoordTrans.COORD.COORD_WGS84)

    def button_draw_nds_gcj02_clicked(self):
        layer = self.create_nds_layer(self.widget.edit_tile_layer_name.text())
        self.draw_nds_tile_by_layer(layer, self.widget.text_tile_content.toPlainText(), QgsCoordTrans.COORD.COORD_GCJ02)

    def button_get_bound_tile_clicked(self):
        extent = self.iface.mapCanvas().extent()
        transform = QgsCoordinateTransform(QgsCoordinateReferenceSystem(self.epsg_id_webmercator), QgsCoordinateReferenceSystem(self.epsg_id_wgs84), QgsProject.instance())
        extent = transform.transform(extent)
        x1, y1, x2, y2 = extent.xMinimum(), extent.yMinimum(), extent.xMaximum(), extent.yMaximum()
        level = self.widget.spin_tile_level.value()
        tile_ids = NdsUtil.get_bound_tileids(x1, y1, x2, y2, level)
        tile_ids_str = ','.join(list(map(str, tile_ids)))
        self.widget.text_tile_content.setPlainText(tile_ids_str)

    def button_get_bound_mer_tile_clicked(self):
        extent = self.iface.mapCanvas().extent()
        x1, y1, x2, y2 = extent.xMinimum(), extent.yMinimum(), extent.xMaximum(), extent.yMaximum()
        level = self.widget.spin_mer_tile_level.value()
        tile_ids = MerTileUtil.get_tiles(x1, y1, x2, y2, level)
        tile_ids_str = ','.join(list(map(str, tile_ids)))
        self.widget.text_mer_tile_content.setPlainText(tile_ids_str)

    def combo_xyz_index_changed(self):
        xyz_name = self.widget.combo_xyzlayer_layertype.currentText()
        self.widget.label_xyz_server.setText(self.xyz_layers[xyz_name])

    def draw_geometry(self, layer_name: str, geometry: QgsGeometry):
        geom_type = self.wkbType2String(geometry)
        uri = f'{geom_type}?crs={self.epsg_id_wgs84}'

        layer = QgsVectorLayer(uri, layer_name, 'memory')
        layer.setShortName('simple')
        pr = layer.dataProvider()

        feature = QgsFeature()
        feature.setGeometry(geometry)
        pr.addFeature(feature)
        layer.updateExtents()
        QgsProject.instance().addMapLayer(layer)

    def wkbType2String(self, g: QgsGeometry) -> str:
        geometry = g.constGet()
        if isinstance(geometry, QgsPoint) or isinstance(geometry, QgsPointXY) or isinstance(geometry, QgsMultiPoint):
            return 'Point'
        elif isinstance(geometry, QgsLineString) or isinstance(geometry, QgsMultiLineString):
            return 'LineString'
        elif isinstance(geometry, QgsPolygon) or isinstance(geometry, QgsMultiPolygon):
            return 'Polygon'        

        raise Exception(f'invalid geometry type {g.asWkt()}')

    def button_draw_wkt_clicked(self):
        text_content = self.widget.text_wkt_content.toPlainText()
        geometries = list(map(lambda l : QgsGeometry.fromWkt(l.strip()), text_content.strip().split('\n')))
        geom = geometries[0]

        if geom is None or geom.isEmpty():
            self.iface.messageBar().pushMessage("Error", "invalid wkt string", level=Qgis.Critical)
            return 
        
        geom = QgsGeometry(geom)
    
        coord_type = self.widget.combo_wkt_coordstype.currentText()
        geom = QgsCoordTrans.geometry_trans(geom, coord_type, QgsCoordTrans.COORD.COORD_WGS84)
        layer_name = self.widget.edit_wkt_layer_name.text()
        self.draw_geometry(layer_name, geom)

    def button_draw_wkb_clicked(self):
        text_content = self.widget.text_wkt_content.toPlainText()
        geometries = list(map(lambda l : QgsGeometry.fromWkt(l.strip()), text_content.strip().split('\n')))
        geom = QgsGeometryCollection()
        for g in geometries:
            geom.addGeometry(g.get())

        if geom is None or geom.isEmpty():
            self.iface.messageBar().pushMessage("Error", "invalid wkt string", level=Qgis.Critical)
            return 
        
        geom = QgsGeometry(geom)
        
        coord_type = self.widget.combo_wkt_coordstype.currentText()
        geom = QgsCoordTrans.geometry_trans(geom, coord_type, QgsCoordTrans.COORD.COORD_WGS84)
        layer_name = self.widget.edit_wkt_layer_name.text()
        self.draw_geometry(layer_name, geom)

    def button_draw_geojson_clicked(self):
        features = QgsJsonUtils.stringToFeatureList(self.widget.text_geojson_content.toPlainText())
        coord_type = self.widget.combo_geojson_coordstype.currentText()
        features = QgsCoordTrans.features_trans(features, coord_type, QgsCoordTrans.COORD.COORD_WGS84)

        layer_name = self.widget.edit_geojson_layer_name.text()

        geom_type = self.wkbType2String(features[0].geometry())
        uri = f'{geom_type}?crs={self.epsg_id_wgs84}'
        layer = QgsVectorLayer(uri, layer_name, 'memory')
        layer.setShortName('geojson')
        pr = layer.dataProvider()
        pr.addFeatures(features)

        layer.updateExtents()
        QgsProject.instance().addMapLayer(layer)

    # mode 0 point 1 line 2 polygone
    def draw_simple_feature(self, layer_name: str, coords_str: str, mode: int, coords_sys: str):
        coords = list(map(lambda x : float(x.strip()), coords_str.strip().split(',')))
        points = []
        for i in range(0, len(coords), 2):
            x, y = coords[i + 0], coords[i + 1]
            points.append(QgsPointXY(x, y))

        if mode == 0:
            geometry = QgsGeometry.fromMultiPointXY(points)
        elif mode == 1:
            geometry = QgsGeometry.fromPolylineXY(points)
        elif mode == 2:
            geometry = QgsGeometry.fromPolygonXY([points])

        geometry = QgsCoordTrans.geometry_trans(geometry, coords_sys, QgsCoordTrans.COORD.COORD_WGS84)

        if geometry is not None and not geometry.isEmpty():
            self.draw_geometry(layer_name, geometry)  

    def button_draw_point_clicked(self):
        layer_name = self.widget.edit_simple_layer_name.text()
        coords = self.widget.text_simple_content.toPlainText()
        coords_type = self.widget.combo_simple_coordstype.currentText()
        self.draw_simple_feature(layer_name, coords, 0, coords_type)

    def button_draw_line_clicked(self):
        layer_name = self.widget.edit_simple_layer_name.text()
        coords = self.widget.text_simple_content.toPlainText()
        coords_type = self.widget.combo_simple_coordstype.currentText()
        self.draw_simple_feature(layer_name, coords, 1, coords_type)

    def button_draw_polygon_clicked(self):
        layer_name = self.widget.edit_simple_layer_name.text()
        coords = self.widget.text_simple_content.toPlainText()
        coords_type = self.widget.combo_simple_coordstype.currentText()
        self.draw_simple_feature(layer_name, coords, 2, coords_type)

    def button_coordtransform_a2b_clicked(self):
        src_coords_sys = self.widget.combo_coords_a.currentText()
        dest_coords_sys = self.widget.combo_coords_b.currentText()
        coords_str = self.widget.text_coords_a.toPlainText()
        result_str = QgsCoordTrans.coords_transform(coords_str, src_coords_sys, dest_coords_sys)
        self.widget.text_coords_b.setPlainText(result_str)

    def button_coordtransform_b2a_clicked(self):
        src_coords_sys = self.widget.combo_coords_b.currentText()
        dest_coords_sys = self.widget.combo_coords_a.currentText()
        coords_str = self.widget.text_coords_b.toPlainText()
        result_str = QgsCoordTrans.coords_transform(coords_str, src_coords_sys, dest_coords_sys)
        self.widget.text_coords_a.setPlainText(result_str)

    def button_xyz_layer_add_clicked(self):
        layer_name = self.widget.combo_xyzlayer_layertype.currentText()
        layer_uri = self.widget.label_xyz_server.text()

        if layer_name is None or layer_uri is None :
            return 
        
        layer_uri = urllib.parse.quote(layer_uri)
        layer_uri = f'url={layer_uri}&type=xyz&zmax=18&zmin=0'
        layer = QgsRasterLayer(layer_uri, layer_name, "wms")

        QgsProject.instance().addMapLayer(layer)

    def log(self, msg: str):
        QgsMessageLog.logMessage(msg)

class DrawTool(QgsMapTool):
    draw_finish_event = pyqtSignal(QgsGeometry)

    def __init__(self, canvas: QgsMapCanvas, geometry_type: QgsWkbTypes):
        super().__init__(canvas)
        self.canvas = canvas
        self.geometry_type = geometry_type
        self.geometry_index = 0
        self.point_count = 0
        self.rubber_band = QgsRubberBand(self.canvas, self.geometry_type)
        self.rubber_band.setColor(QColor(QRgba64.fromRgba(255, 0, 0, 100)))
        self.rubber_band.setFillColor(QColor(QRgba64.fromRgba(128, 128, 128, 75)))
        self.rubber_band.setLineStyle(Qt.PenStyle.DashLine)

    def canvasPressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.point_count = self.point_count + 1
            point = self.toMapCoordinates(event.pos())
            self.rubber_band.addPoint(point, geometryIndex=self.geometry_index)
        elif event.button() == QtCore.Qt.RightButton:
            if self.point_count == 0:
                self.deactivate()
            else:
                self.geometry_index = self.geometry_index + 1
                self.point_count = 0

    def deactivate(self):
        geom = self.rubber_band.asGeometry()
        self.draw_finish_event.emit(geom)

        self.rubber_band.reset(self.geometry_type)
        super().deactivate()
        