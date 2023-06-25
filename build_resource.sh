#!/bin/sh

pyuic5 -o mtk_widget_base.py mtk_widget_base.ui 
pyrcc5 -o resources.py resources.qrc 