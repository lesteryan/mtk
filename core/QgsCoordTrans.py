# -*- coding: utf-8 -*-

from qgis.core import QgsGeometry, QgsPoint, QgsMultiPoint, QgsLineString, QgsMultiLineString, QgsPolygon, QgsMultiPolygon, QgsRectangle, QgsGeometryCollection
from qgis.core import QgsFeature
from .CoordTrans import CoordTrans

class QgsCoordTrans:

    class COORD:
        COORD_WGS84 = 'wgs84'
        COORD_GCJ02 = 'gcj02'
        COORD_WEBMERCATOR = 'webmercator'

    @staticmethod
    def wgs84_to_gcj02(p : QgsPoint) -> QgsPoint:
        x, y = CoordTrans.wgs84_to_gcj02(p.x(), p.y())
        return QgsPoint(x ,y)

    @staticmethod
    def wgs84_to_webmercator(p : QgsPoint) -> QgsPoint:
        x, y = CoordTrans.wgs84_to_webmercator(p.x(), p.y())
        return QgsPoint(x ,y)
    
    @staticmethod
    def gcj02_to_wgs84(p : QgsPoint) -> QgsPoint:
        x, y = CoordTrans.gcj02_to_wgs84(p.x(), p.y())
        return QgsPoint(x ,y)

    @staticmethod
    def gcj02_to_webmercator(p : QgsPoint) -> QgsPoint:
        x, y = CoordTrans.gcj02_to_webmercator(p.x(), p.y())
        return QgsPoint(x ,y)
    
    @staticmethod
    def webmercator_to_wgs84(p : QgsPoint) -> QgsPoint:
        x, y = CoordTrans.webmercator_to_wgs84(p.x(), p.y())
        return QgsPoint(x ,y)

    @staticmethod
    def webmercator_to_gcj02(p : QgsPoint) -> QgsPoint:
        x, y = CoordTrans.webmercator_to_gcj02(p.x(), p.y())
        return QgsPoint(x ,y)
    
    @staticmethod
    def point_trans(p: QgsPoint, from_coord: str, to_coord: str) -> QgsPoint:
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
    def multipoint_trans(multi_point: QgsMultiPoint, from_coord: str, to_coord: str) -> QgsMultiPoint:
        ret = QgsMultiPoint()
        for index in range(multi_point.numGeometries()):
            ret.addGeometry(QgsCoordTrans.point_trans(multi_point.pointN(index), from_coord, to_coord))

        return ret
    
    @staticmethod
    def linestring_trans(linestring: QgsLineString, from_coord: str, to_coord: str) -> QgsLineString:
        points = list(map(lambda l : QgsCoordTrans.point_trans(l, from_coord, to_coord), linestring.points()))
        return QgsLineString(points)

    @staticmethod
    def multilinestring_trans(multi_linestring: QgsMultiLineString, from_coord: str, to_coord: str) -> QgsMultiLineString:
        ret = QgsMultiLineString()

        for index in range(multi_linestring.numGeometries()):
            linestring = QgsCoordTrans.linestring_trans(multi_linestring.geometryN(index), from_coord, to_coord)
            ret.addGeometry(linestring)
        
        return ret

    
    @staticmethod
    def polygon_trans(polygon: QgsPolygon, from_coord: str, to_coord: str) -> QgsPolygon:
        ret = QgsPolygon()

        exter_ring = QgsCoordTrans.linestring_trans(polygon.exteriorRing(), from_coord, to_coord)
        ret.setExteriorRing(exter_ring)

        for index in range(polygon.numInteriorRings()):
            inter_ring = QgsCoordTrans.linestring_trans(polygon.interiorRing(index), from_coord, to_coord)
            ret.addInteriorRing(inter_ring)
        
        return ret
    
    @staticmethod
    def rectangle_trans(rectangle: QgsRectangle, from_coord: str, to_coord: str) -> QgsPolygon:
        p1 = QgsCoordTrans.point_trans(QgsPoint(rectangle.xMinimum(), rectangle.yMinimum()), from_coord, to_coord)
        p2 = QgsCoordTrans.point_trans(QgsPoint(rectangle.xMinimum(), rectangle.yMinimum()), from_coord, to_coord)

        return QgsRectangle(p1.x, p1.y, p2.x, p2.y)

    @staticmethod
    def multipolygon_trans(multi_polygon: QgsMultiPolygon, from_coord: str, to_coord: str) -> QgsMultiPolygon:
        ret = QgsMultiPolygon()
        for index in range(multi_polygon.numGeometries()):
            polygon = QgsCoordTrans.polygon_trans(multi_polygon.geometryN(index), from_coord, to_coord)
            ret.addGeometry(polygon)

        return ret
    
    @staticmethod
    def geometry_trans(geometry: QgsGeometry, from_coord: str, to_coord: str) -> QgsGeometry:
        if geometry is None or geometry.isEmpty():
            return geometry
        
        if from_coord == to_coord:
            return geometry
        
        if isinstance(geometry, QgsRectangle):
            return QgsCoordTrans.rectangle_trans(geometry, from_coord, to_coord)
        else:
            g = geometry.constGet()
            
            if isinstance(g, QgsPoint):
                g = QgsCoordTrans.point_trans(g, from_coord, to_coord)
            elif isinstance(g, QgsMultiPoint):
                g = QgsCoordTrans.multipoint_trans(g, from_coord, to_coord)
            elif isinstance(g, QgsRectangle):
                g = QgsCoordTrans.rectangle_trans(g, from_coord, to_coord)
            elif isinstance(g, QgsLineString):
                g = QgsCoordTrans.linestring_trans(g, from_coord, to_coord)
            elif isinstance(g, QgsMultiLineString):
                g = QgsCoordTrans.multilinestring_trans(g, from_coord, to_coord)
            elif isinstance(g, QgsPolygon):
                g =  QgsCoordTrans.polygon_trans(g, from_coord, to_coord)
            elif isinstance(g, QgsMultiPolygon):
                g = QgsCoordTrans.multipolygon_trans(g, from_coord, to_coord)
            elif isinstance(g, QgsGeometryCollection):
                g1 = QgsGeometryCollection()
                # for gc in g:
                    # QgsMessageLog.logMessage('aaaaa')
                    # g1.addGeometry(QgsCoordTrans.geometry_trans(QgsGeometry(gc), from_coord, to_coord).constGet())
                QgsMessageLog.logMessage('bbbbb')
                # g = g1
                
            else:
                raise Exception(f'unsupport geometry type {g.asWkt()} {type(g).__name__}')
            
            return QgsGeometry(g)
    
    @staticmethod
    def get_geometry_points(geometry: QgsGeometry) -> list[QgsPoint]:
        if geometry is None or geometry.isEmpty():
            return []
        
        g = geometry.constGet()
        seqs = g.coordinateSequence()

        def flatten_list(lst):
            result = []
            for item in lst:
                if isinstance(item, list):
                    result.extend(flatten_list(item))
                else:
                    result.append(item)
            return result

        return flatten_list(seqs)
        
    @staticmethod
    def feature_trans(g: QgsFeature, from_coord: str, to_coord: str) -> QgsFeature:
        if g is None:
            return g
        
        feature = QgsFeature(g)
        feature.setGeometry(QgsCoordTrans.geometry_trans(g.geometry(), from_coord, to_coord))
        return feature
    
    @staticmethod
    def features_trans(g: list[QgsFeature], from_coord: str, to_coord: str) -> list[QgsFeature]:
        if g is None or len(g) == 0:
            return g
        
        return list(map(lambda l : QgsCoordTrans.feature_trans(l, from_coord, to_coord), g))
        
    @staticmethod
    def coords_transform(coords_src: str, src_coords_system: str, dest_coords_sys: str) -> str:
        if src_coords_system == dest_coords_sys:
            return coords_src
        
        coords = list(map(lambda x : float(x.strip()), coords_src.strip().split(',')))
        result = []
        for i in range(0, len(coords), 2):
            x, y = coords[i + 0], coords[i + 1]
            result.append(QgsCoordTrans.point_trans(QgsPoint(x, y), src_coords_system, dest_coords_sys))
        
        result = list(map(lambda l : str(l.x()) + ',' + str(l.y()), result))

        return ','.join(result)


