# -*- coding: utf-8 -*-
import math
from typing import Tuple

class CoordTrans:
    x_pi = math.pi * 3000.0 / 180.0
    a = 6378245.0  # 长半轴
    ee = 0.00669342162296594323  # 扁率

    @staticmethod
    def wgs84_to_gcj02(lng: float, lat: float) -> Tuple[float, float]:
        dlat = CoordTrans.__transform_lat(lng - 105.0, lat - 35.0)
        dlng = CoordTrans.__transform_lng(lng - 105.0, lat - 35.0)

        radlat = lat / 180.0 * math.pi
        magic = math.sin(radlat)
        magic = 1 - CoordTrans.ee * magic * magic

        sqrtmagic = math.sqrt(magic)

        dlat = (dlat * 180.0) / ((CoordTrans.a * (1 - CoordTrans.ee)) / (magic * sqrtmagic) * math.pi)
        dlng = (dlng * 180.0) / (CoordTrans.a / sqrtmagic * math.cos(radlat) * math.pi)

        mglat = lat + dlat
        mglng = lng + dlng

        return (mglng, mglat)

    @staticmethod
    def gcj02_to_wgs84(lng: float, lat: float) -> Tuple[float, float]:
        dlat = CoordTrans.__transform_lat(lng - 105.0, lat - 35.0)
        dlng = CoordTrans.__transform_lng(lng - 105.0, lat - 35.0)

        radlat = lat / 180.0 * math.pi
        magic = math.sin(radlat)
        magic = 1 - CoordTrans.ee * magic * magic

        sqrtmagic = math.sqrt(magic)

        dlat = (dlat * 180.0) / ((CoordTrans.a * (1 - CoordTrans.ee)) / (magic * sqrtmagic) * math.pi)
        dlng = (dlng * 180.0) / (CoordTrans.a / sqrtmagic * math.cos(radlat) * math.pi)

        mglat = lat + dlat
        mglng = lng + dlng

        return (lng * 2 - mglng, lat * 2 - mglat)
    
    @staticmethod
    def webmecator_to_wgs84(x: float, y: float) -> Tuple[float, float]:
        lon = (x / 20037508.34) * 180
        lat = (y / 20037508.34) * 180
        lat = 180 / math.pi * (2 * math.atan(math.exp(lat * math.pi / 180)) - math.pi / 2)
        return (lon, lat)

    @staticmethod
    def wgs84_to_webmecator(lon: float, lat: float) -> Tuple[float, float]:
        x = lon * 20037508.34 / 180
        y = math.log(math.tan((90 + lat) * math.pi / 360)) / (math.pi / 180)
        y = y * 20037508.34 / 180
        return (x, y)
    
    @staticmethod
    def gcj02_to_webmecator(lng: float, lat: float) -> Tuple[float, float]:
        tmp = CoordTrans.gcj02_to_wgs84(lng, lat)
        return CoordTrans.wgs84_to_webmecator(tmp[0], tmp[1])

    @staticmethod
    def webmecator_to_gcj02(lng: float, lat: float) -> Tuple[float, float]:
        tmp = CoordTrans.webmecator_to_wgs84(lng, lat)
        return CoordTrans.wgs84_to_gcj02(tmp[0], tmp[1])

    @staticmethod
    def __transform_lat(lng, lat):
        ret = -100.0 + 2.0 * lng + 3.0 * lat + 0.2 * lat * lat + 0.1 * lng * lat + 0.2 * math.sqrt(math.fabs(lng))

        ret += (20.0 * math.sin(6.0 * lng * math.pi) + 20.0 * math.sin(2.0 * lng * math.pi)) * 2.0 / 3.0

        ret += (20.0 * math.sin(lat * math.pi) + 40.0 * math.sin(lat / 3.0 * math.pi)) * 2.0 / 3.0

        ret += (160.0 * math.sin(lat / 12.0 * math.pi) + 320 * math.sin(lat * math.pi / 30.0)) * 2.0 / 3.0
        return ret

    @staticmethod
    def __transform_lng(lng, lat):
        ret = 300.0 + lng + 2.0 * lat + 0.1 * lng * lng + 0.1 * lng * lat + 0.1 * math.sqrt(math.fabs(lng))

        ret += (20.0 * math.sin(6.0 * lng * math.pi) + 20.0 * math.sin(2.0 * lng * math.pi)) * 2.0 / 3.0

        ret += (20.0 * math.sin(lng * math.pi) + 40.0 * math.sin(lng / 3.0 * math.pi)) * 2.0 / 3.0

        ret += (150.0 * math.sin(lng / 12.0 * math.pi) + 300.0 * math.sin(lng / 30.0 * math.pi)) * 2.0 / 3.0

        return ret
