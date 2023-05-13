# -*- coding: utf-8 -*-
import math
from typing import Tuple


class CoordTrans:
    x_pi = 3.14159265358979324 * 3000.0 / 180.0
    pi = 3.1415926535897932384626  # π
    a = 6378245.0  # 长半轴
    ee = 0.00669342162296594323  # 扁率

    @staticmethod
    def wgs84_to_gcj02(lng: float, lat: float) -> Tuple[float, float]:
        """
        WGS84转GCJ02(火星坐标系)
        :param lng:WGS84坐标系的经度
        :param lat:WGS84坐标系的纬度
        :return:
        """
        dlat = CoordTrans.__transform_lat(lng - 105.0, lat - 35.0)
        dlng = CoordTrans.__transform_lng(lng - 105.0, lat - 35.0)

        radlat = lat / 180.0 * CoordTrans.pi
        magic = math.sin(radlat)
        magic = 1 - CoordTrans.ee * magic * magic

        sqrtmagic = math.sqrt(magic)

        dlat = (dlat * 180.0) / ((CoordTrans.a * (1 - CoordTrans.ee)) / (magic * sqrtmagic) * CoordTrans.pi)
        dlng = (dlng * 180.0) / (CoordTrans.a / sqrtmagic * math.cos(radlat) * CoordTrans.pi)

        mglat = lat + dlat
        mglng = lng + dlng

        return (mglng, mglat)

    @staticmethod
    def gcj02_to_wgs84(lng: float, lat: float) -> Tuple[float, float]:
        """
        GCJ02(火星坐标系)转GPS84
        :param lng:火星坐标系的经度
        :param lat:火星坐标系纬度
        :return:
        """
        dlat = CoordTrans.__transform_lat(lng - 105.0, lat - 35.0)
        dlng = CoordTrans.__transform_lng(lng - 105.0, lat - 35.0)

        radlat = lat / 180.0 * CoordTrans.pi
        magic = math.sin(radlat)
        magic = 1 - CoordTrans.ee * magic * magic

        sqrtmagic = math.sqrt(magic)

        dlat = (dlat * 180.0) / ((CoordTrans.a * (1 - CoordTrans.ee)) / (magic * sqrtmagic) * CoordTrans.pi)
        dlng = (dlng * 180.0) / (CoordTrans.a / sqrtmagic * math.cos(radlat) * CoordTrans.pi)

        mglat = lat + dlat
        mglng = lng + dlng

        return (lng * 2 - mglng, lat * 2 - mglat)

    @staticmethod
    def __transform_lat(lng, lat):
        ret = -100.0 + 2.0 * lng + 3.0 * lat + 0.2 * lat * lat + 0.1 * lng * lat + 0.2 * math.sqrt(math.fabs(lng))

        ret += (20.0 * math.sin(6.0 * lng * CoordTrans.pi) + 20.0 * math.sin(2.0 * lng * CoordTrans.pi)) * 2.0 / 3.0

        ret += (20.0 * math.sin(lat * CoordTrans.pi) + 40.0 * math.sin(lat / 3.0 * CoordTrans.pi)) * 2.0 / 3.0

        ret += (160.0 * math.sin(lat / 12.0 * CoordTrans.pi) + 320 * math.sin(lat * CoordTrans.pi / 30.0)) * 2.0 / 3.0
        return ret

    @staticmethod
    def __transform_lng(lng, lat):
        ret = 300.0 + lng + 2.0 * lat + 0.1 * lng * lng + 0.1 * lng * lat + 0.1 * math.sqrt(math.fabs(lng))

        ret += (20.0 * math.sin(6.0 * lng * CoordTrans.pi) + 20.0 * math.sin(2.0 * lng * CoordTrans.pi)) * 2.0 / 3.0

        ret += (20.0 * math.sin(lng * CoordTrans.pi) + 40.0 * math.sin(lng / 3.0 * CoordTrans.pi)) * 2.0 / 3.0

        ret += (150.0 * math.sin(lng / 12.0 * CoordTrans.pi) + 300.0 * math.sin(lng / 30.0 * CoordTrans.pi)) * 2.0 / 3.0

        return ret
