# -*- coding: utf-8 -*-
"""
/***************************************************************************
 MapToolKit
                                 A QGIS plugin
 lesteryan map tool kit
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2023-04-26
        copyright            : (C) 2023 by lesteryan
        email                : cgmsyx@163.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load MapToolKit class from file MapToolKit.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .mtk import MapToolKit
    return MapToolKit(iface)