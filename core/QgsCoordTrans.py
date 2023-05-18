# -*- coding: utf-8 -*-

from qgis.core import QgsGeometry, QgsPoint, QgsMultiPoint, QgsLineString, QgsMultiLineString, QgsPolygon, QgsMultiPolygon
from .CoordTrans import CoordTrans

class QgsCoordTrans:

    class COORD:
        COORD_WGS84 = 'wgs84'
        COORD_GCJ02 = 'gcj02'
        COORD_WEBMERCATOR = 'webmercator'

    @staticmethod
    def wgs84_to_gcj02(p : QgsPoint) -> QgsPoint:
        x, y = CoordTrans.wgs84_to_gcj02(p.x(), p.y)
        return QgsPoint(x ,y)

    @staticmethod
    def wgs84_to_webmercator(p : QgsPoint) -> QgsPoint:
        x, y = CoordTrans.wgs84_to_webmercator(p.x(), p.y)
        return QgsPoint(x ,y)
    
    @staticmethod
    def gcj02_to_wgs84(p : QgsPoint) -> QgsPoint:
        x, y = CoordTrans.gcj02_to_wgs84(p.x(), p.y)
        return QgsPoint(x ,y)

    @staticmethod
    def gcj02_to_webmercator(p : QgsPoint) -> QgsPoint:
        x, y = CoordTrans.gcj02_to_webmercator(p.x(), p.y)
        return QgsPoint(x ,y)
    
    @staticmethod
    def webmercator_to_wgs84(p : QgsPoint) -> QgsPoint:
        x, y = CoordTrans.webmercator_to_wgs84(p.x(), p.y)
        return QgsPoint(x ,y)

    @staticmethod
    def webmercator_to_gcj02(p : QgsPoint) -> QgsPoint:
        x, y = CoordTrans.webmercator_to_gcj02(p.x(), p.y)
        return QgsPoint(x ,y)
    
    @staticmethod
    def point_trans(p: QgsPoint, from_coord: COORD, to_coord: COORD) -> QgsPoint:
        if from_coord == QgsCoordTrans.COORD.COORD_WGS84:
            if to_coord == QgsCoordTrans.COORD.COORD_WGS84:
                return p
            elif to_coord == QgsCoordTrans.COORD.COORD_GCJ02:
                return QgsCoordTrans.wgs84_to_gcj02(p)
            elif to_coord == QgsCoordTrans.COORD.COORD_WEBMERCATOR:
                return QgsCoordTrans.wgs84_to_webmercator(p)
        elif from_coord == QgsCoordTrans.COORD.COORD_GCJ02:
            if to_coord == QgsCoordTrans.COORD.COORD_WGS84:
                return QgsCoordTrans.gcj02_to_wgs84(p)
            elif to_coord == QgsCoordTrans.COORD.COORD_GCJ02:
                return p
            elif to_coord == QgsCoordTrans.COORD.COORD_WEBMERCATOR:
                return QgsCoordTrans.gcj02_to_webmercator(p)
        elif from_coord == QgsCoordTrans.COORD.COORD_WEBMERCATOR:
            if to_coord == QgsCoordTrans.COORD.COORD_WGS84:
                return QgsCoordTrans.webmercator_to_wgs84(p)
            elif to_coord == QgsCoordTrans.COORD.COORD_GCJ02:
                return QgsCoordTrans.webmercator_to_gcj02(p)
            elif to_coord == QgsCoordTrans.COORD.COORD_WEBMERCATOR:
                return p

    @staticmethod  
    def multipoint_trans(l: QgsMultiPoint, from_coord: COORD, to_coord: COORD) -> QgsMultiPoint:
        points = []
        for index in range(l.numGeometries()):
            points.append(QgsCoordTrans.point_trans(l.pointN(index), from_coord, to_coord))

        return QgsGeometry.fromMultiPointXY(points)
    
    @staticmethod
    def linestring_trans(l: QgsLineString, from_coord: COORD, to_coord: COORD) -> QgsLineString:
        points = list(map(lambda l : QgsCoordTrans.point_trans(l, from_coord, to_coord), l.points()))
        return QgsGeometry.fromPolylineXY(points)

    @staticmethod
    def multilinestring_trans(l: QgsMultiLineString, from_coord: COORD, to_coord: COORD) -> QgsMultiLineString:
        multilinestring = QgsMultiLineString()

        for index in range(l.numGeometries()):
            l = QgsCoordTrans.linestring_trans(l.lineStringN(index), from_coord, to_coord)
            multilinestring.addGeometry(l)
        
        return multilinestring

    
    @staticmethod
    def polygon_trans(l: QgsPolygon, from_coord: COORD, to_coord: COORD) -> QgsPolygon:
        polygon = QgsPolygon()

        exter_ring = QgsCoordTrans.linestring_trans(l.exteriorRing(), from_coord, to_coord)
        polygon.setExteriorRing(exter_ring)

        for index in range(l.numInteriorRings()):
            inter_ring = QgsCoordTrans.linestring_trans(l.interiorRing(index), from_coord, to_coord)
            polygon.addInteriorRing(inter_ring)
        
        return polygon


    @staticmethod
    def multipolygon_trans(l: QgsMultiPolygon, from_coord: COORD, to_coord: COORD) -> QgsMultiPolygon:
        multipolygon = QgsMultiPolygon()
        for index in range(l.numGeometries()):
            l = QgsCoordTrans.polygon_trans(l.geometryN(index), from_coord, to_coord)
            multipolygon.addGeometry(multipolygon)

        return multipolygon
    
    @staticmethod
    def geometry_trans(g: QgsGeometry, from_coord: COORD, to_coord: COORD) -> QgsGeometry:
        if isinstance(g, QgsPoint):
            return QgsCoordTrans.point_trans(g, from_coord, to_coord)
        elif isinstance(g, QgsMultiPoint):
            return QgsCoordTrans.multipoint_trans(g, from_coord, to_coord)
        elif isinstance(g, QgsLineString):
            return QgsCoordTrans.linestring_trans(g, from_coord, to_coord)
        elif isinstance(g, QgsMultiLineString):
            return QgsCoordTrans.multilinestring_trans(g, from_coord, to_coord)
        elif isinstance(g, QgsPolygon):
            return QgsCoordTrans.polygon_trans(g, from_coord, to_coord)
        elif isinstance(g, QgsMultiPolygon):
            return QgsCoordTrans.multipolygon_trans(g, from_coord, to_coord)
        else:
            raise Exception(f'unsupport geometry type {g}')


