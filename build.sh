#!/bin/sh
pyuic5 -o mtk_dialog_base.py mtk_dialog_base.ui
pyrcc5 -o resources.py resources.qrc
