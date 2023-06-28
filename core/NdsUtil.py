# -*- coding: utf-8 -*-

    
import math
from typing import List, Tuple

from shapely.geometry import Polygon
from qgis.core import *

class NdsUtil:
    @staticmethod
    def compact_bits(morton: int) -> int:
        """莫顿码"""
        morton &= 0x5555555555555555
        morton = (morton ^ (morton >> 1)) & 0x3333333333333333
        morton = (morton ^ (morton >> 2)) & 0x0F0F0F0F0F0F0F0F
        morton = (morton ^ (morton >> 4)) & 0x00FF00FF00FF00FF
        morton = (morton ^ (morton >> 8)) & 0x0000FFFF0000FFFF
        morton = (morton ^ (morton >> 16)) & 0x00000000FFFFFFFF
        return int(morton)

    @staticmethod
    def signed_bit_restore(val: int):
        return val | 0x80000000 if val & 0x40000000 else val

    @staticmethod
    def get_nds_coord_from_morton(morton: int) -> Tuple[int, int]:
        x = NdsUtil.compact_bits(morton)
        y = NdsUtil.signed_bit_restore(NdsUtil.compact_bits(morton >> 1))
        return x, y

    @staticmethod
    def get_tile_level(tile_id: int):
        level = 15
        while not tile_id & 0x80000000:
            tile_id <<= 1
            level -= 1
        return level

    @staticmethod
    def get_tile_width(level):
        return int(math.pow(2, (31 - level)))

    @staticmethod
    def get_center_nds_of_tile(tile_id: int) -> Tuple[float, float]:
        level = NdsUtil.get_tile_level(tile_id)
        tile = (0xFFFFFFFF >> (31 - 2 * level)) & tile_id
        code = tile << (62 - 2 * level)
        tile_width = NdsUtil.get_tile_width(level)
        x, y = NdsUtil.get_nds_coord_from_morton(code)
        return x + tile_width / 2, y + tile_width / 2

    @staticmethod
    def nds_to_lonlat(x: float, y: float) -> Tuple[float, float]:
        def nds_to_deg(nds_val):
            return float(90.0 * nds_val / (1 << 30))

        lng = nds_to_deg(x)
        lat = nds_to_deg(y)
        return lng, lat

    @staticmethod
    def get_tile_polygon_of_deg(tile_id) -> list[Tuple[float, float]]:
        level = NdsUtil.get_tile_level(tile_id)
        center_x, center_y = NdsUtil.get_center_nds_of_tile(tile_id)
        width = NdsUtil.get_tile_width(level)
        lu = center_x - width / 2, center_y + width / 2
        ld = center_x - width / 2, center_y - width / 2
        ru = center_x + width / 2, center_y + width / 2
        rd = center_x + width / 2, center_y - width / 2
        lu = NdsUtil.nds_to_lonlat(*lu)
        ld = NdsUtil.nds_to_lonlat(*ld)
        ru = NdsUtil.nds_to_lonlat(*ru)
        rd = NdsUtil.nds_to_lonlat(*rd)

        return [lu, ru, rd, ld]

    @staticmethod
    def get_tile_box_of_deg(tile_id):
        level = NdsUtil.get_tile_level(tile_id)
        center_x, center_y = NdsUtil.get_center_nds_of_tile(tile_id)
        width = NdsUtil.get_tile_width(level)
        lu = center_x - width / 2, center_y + width / 2
        rd = center_x + width / 2, center_y - width / 2
        return NdsUtil.nds_to_lonlat(*lu), NdsUtil.nds_to_lonlat(*rd)

    @staticmethod
    def lonlat_to_nds(lng: float, lat: float):
        def deg_to_nds(deg_val):
            return int((1 << 30) * deg_val / 90.0)

        lat = float(lat)
        lng = float(lng)
        x = deg_to_nds(lng)
        y = deg_to_nds(lat)
        return x, y
    
    @staticmethod
    def interleave(x: int) -> int:
        x &= 0x0000ffff
        x = (x ^ (x << 8)) & 0x00ff00ff
        x = (x ^ (x << 4)) & 0x0f0f0f0f
        x = (x ^ (x << 2)) & 0x33333333
        x = (x ^ (x << 1)) & 0x55555555
        return x

    @staticmethod
    def encode(x: int, y: int) -> int:
        return NdsUtil.interleave(y) << 1 | NdsUtil.interleave(x)
    
    @staticmethod
    def get_bound_tileids(min_lng: float, min_lat: float, max_lng: float, max_lat: float, level: int) -> list[int]:
        xyBitCount = 2 * level + 1
        invalidBitCounter = int(32 - (int(xyBitCount / 2) + xyBitCount % 2))
        levelNumber = int((1 << 31) >> (15 - level))
        factor = 360.0 / (1 << 32)
        
        mX0 = (int(min_lng / factor)) >> invalidBitCounter
        mY0 = (int(min_lat / factor)) >> invalidBitCounter

        tmp_x = max_lng / factor
        tmp_y = max_lat / factor
        mX1 = (int(tmp_x)) >> invalidBitCounter
        mY1 = (int(tmp_y)) >> invalidBitCounter

        if tmp_x != math.floor(tmp_x):
            mX1 = mX1 + 1

        if tmp_y != math.floor(tmp_x):
            mY1 = mY1 + 1

        tileidList = []
        NdsUtil.get_morton_code_from_nds(int(min_lng / factor), int(min_lat / factor))
        NdsUtil.get_tile_id_from_nds(level,int(min_lng / factor), int(min_lat / factor) )
        for x in range(mX0, mX1):
            for y in range(mY0, mY1):
                tile_number = NdsUtil.get_morton_code_from_nds(x, y)

                # QgsMessageLog.logMessage("tile_number: " + str(tile_number | levelNumber))  
                tileidList.append(levelNumber | tile_number)
        
        return tileidList

    @staticmethod
    def lonlat_to_tileid(lng, lat, level=13):
        x, y = NdsUtil.lonlat_to_nds(lng, lat)
        return NdsUtil.get_tile_id_from_nds(level, x, y)

    @staticmethod
    def get_tile_id_from_nds(level, x, y):
        morton = NdsUtil.get_morton_code_from_nds(x, y)
        tile_id = NdsUtil.get_tile_id_from_morton(level, morton)
        return tile_id

    @staticmethod
    def get_morton_code_from_nds(x, y):
        return NdsUtil.part(int(x)) | (NdsUtil.part((int(y)) & 0x7FFFFFFF) << 1)

    @staticmethod
    def get_tile_id_from_morton(level, morton):
        packed_tile_id = morton >> (62 - 2 * level)
        packed_level = 1 << (16 + level)
        tile_id = packed_tile_id | packed_level
        return tile_id

    @staticmethod
    def part(val):
        # for negative values take only lower 32 bits
        if val < 0:
            val &= 0xFFFFFFFF
        val = (val | (val << 16)) & 0x0000FFFF0000FFFF
        val = (val | (val << 8)) & 0x00FF00FF00FF00FF
        val = (val | (val << 4)) & 0x0F0F0F0F0F0F0F0F
        val = (val | (val << 2)) & 0x3333333333333333
        val = (val | (val << 1)) & 0x5555555555555555
        return val

    @staticmethod
    def move_x(tile_id: int, inc: bool):
        """
        >>> move_x(557467565, True)
        557467576
        >>> move_x(557467565, False)
        557467564
        """

        level = NdsUtil.get_tile_level(tile_id)

        morton = tile_id & (~(1 << (level + 16)))

        x = morton & 0x5555555555555555
        y = morton & 0xAAAAAAAAAAAAAAAA

        z = 0xAAAAAAAAAAAAAAAA >> (64 - (2 * level))

        if inc:
            x = x + (z + 1)
        else:
            x |= z
            x -= z + 1

        x &= 0x5555555555555555 >> (64 - (2 * level))

        return (x | y) | (1 << (level + 16))

    @staticmethod
    def move_y(tile_id, inc: bool):
        """
        >>> move_y(557467565, True)
        557467567
        >>> move_y(557467565, False)
        557467559
        """
        level = NdsUtil.get_tile_level(tile_id)
        tile_id &= ~(1 << (level + 16))

        x = tile_id & 0x5555555555555555
        y = tile_id & 0xAAAAAAAAAAAAAAAA

        z = 0x5555555555555555 >> (64 - (2 * level + 2))

        if inc:
            y = y + (z + 1)
        else:
            y |= z
            y -= z + 1

        y &= 0xAAAAAAAAAAAAAAAA >> (64 - (2 * level + 2))

        return x | y | (1 << (level + 16))

    @staticmethod
    def get_neighbors(tile_id: int) -> List[int]:
        """
        +---+---+---+
        | 7 | 0 | 1 |
        +---+---+---+
        | 6 | x | 2 |
        +---+---+---+
        | 5 | 4 | 3 |
        +---+---+---+
        >>> get_neighbors(557467054)
        [557467396, 557467397, 557467055, 557467053, 557467052, 557467049, 557467051, 557467393]
        """
        return [
            # x   , y+1
            NdsUtil.move_y(tile_id, True),
            # x+1 , y+1
            NdsUtil.move_y(NdsUtil.move_x(tile_id, True), True),
            # x+1 , y
            NdsUtil.move_x(tile_id, True),
            # x+1 , y-1
            NdsUtil.move_y(NdsUtil.move_x(tile_id, True), False),
            # x   , y - 1
            NdsUtil.move_y(tile_id, False),
            # x-1 , y - 1
            NdsUtil.move_y(NdsUtil.move_x(tile_id, False), False),
            # x-1 , y
            NdsUtil.move_x(tile_id, False),
            # x-1 , y + 1
            NdsUtil.move_y(NdsUtil.move_x(tile_id, False), True),
        ]


if __name__ == '__main__':
    # NdsUtil.get_bound_tileids(116.32596942703773,39.885315880171014,116.49921659610142,39.93752870529855, 13)

    
    NdsUtil.get_bound_tileids(2.2945,48.858222,2.2945 + 0.01,48.858222 + 0.01, 13)