# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GBDX
                                 A QGIS plugin
 GBDX is a DigitalGlobe platform enabling data search, download and analytics capabilities for vector and raster commercial, open source and proprietary data sources.  
                              -------------------
        begin                : 2015-09-08
        git sha              : $Format:%H$
        copyright            : (C) 2015 by Michael Trotter/DigitalGlobe, Inc.
        email                : michael.trotter@digitalglobe.com
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
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, Qt, pyqtSlot
from PyQt4.QtGui import QAction, QIcon
# Initialize Qt resources from file resources.py
from Settings import Settings
from Settings.SettingsTool import SettingsTool
import resources

# Import the code for the DockWidget

import os.path

from About.AboutDialog import AboutDialog
from BBox.BBoxTool import BBoxTool
from Catalog.CatalogTool import CatalogTool
from InfoCube.InfoCubeConnect import InfoCubeConnect
from Vectors.VectorsTool import VectorsTool


class GBDX:
    @pyqtSlot()
    def on_about_close(self):
        if self.about:
            self.about = None
        self.about_is_active = False

    @pyqtSlot()
    def on_settings_close(self):
        if self.settings:
            self.settings = None
        self.settings_is_active = False

    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.
        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface

        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)

        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'GBDX_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&GBDX')
        self.toolbar = self.iface.addToolBar(u'GBDX')
        self.toolbar.setObjectName(u'GBDX')

        #print "** INITIALIZING GBDX"

        self.about_is_active = False
        self.catalog_is_active = False
        self.infocube_is_active = False
        self.vectors_is_active = False
        self.settings_is_active = False

        self.about = None
        self.catalog = None
        self.infocube = None
        self.vectors = None
        self.settings = None


    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.
        We implement this ourselves since we do not inherit QObject.
        :param message: String for translation.
        :type message: str, QString
        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('GBDX', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.
        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str
        :param text: Text that should be shown in menu items for this action.
        :type text: str
        :param callback: Function to be called when the action is triggered.
        :type callback: function
        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool
        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool
        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool
        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str
        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget
        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.
        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action


    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""
        self.add_action(':/plugins/GBDX/About.png',
                        text=self.tr(u'About'),
                        callback=self.run_about,
                        parent=self.iface.mainWindow())
        '''
        self.add_action(':/plugins/GBDX/InfoCube.png',
                        text=self.tr(u'InfoCube'),
                        callback=self.run_infocube,
                        parent=self.iface.mainWindow())
        '''
        self.add_action(':/plugins/GBDX/Vectors.png',
                        text=self.tr(u'Vectors'),
                        callback=self.run_vectors,
                        parent=self.iface.mainWindow())
        self.add_action(':/plugins/GBDX/Catalog.png',
                        text=self.tr(u'Catalog'),
                        callback=self.run_catalog,
                        parent=self.iface.mainWindow())
        self.add_action(':/plugins/GBDX/Settings.png',
                        text=self.tr(u'Settings'),
                        callback=self.run_settings,
                        parent=self.iface.mainWindow())

    #--------------------------------------------------------------------------

    def onClosePlugin(self):
        """Cleanup necessary items here when plugin dockwidget is closed"""

        #print "** CLOSING GBDX"

        # disconnects

        # remove this statement if dockwidget is to remain
        # for reuse if plugin is reopened
        # Commented next statement since it causes QGIS crashe
        # when closing the docked window:
        # self.dockwidget = None

        self.about = None

        if self.catalog:
            self.catalog.unload()
        self.catalog = None
        if self.infocube:
            self.infocube.unload()
        self.infocube = None
        if self.vectors:
            self.vectors.unload()
        self.vectors = None

        self.about_is_active = False
        self.catalog_is_active = False
        self.infocube_is_active = False
        self.vectors_is_active = False
        self.settings_is_active = False


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""

        #print "** UNLOAD GBDX"

        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&GBDX'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    #--------------------------------------------------------------------------

    def run_about(self):
        if not self.about_is_active:
            self.about_is_active = True

            if self.about is None:
                self.about = AboutDialog()
                self.about.accepted.connect(self.on_about_close)
                self.about.rejected.connect(self.on_about_close)

            self.about.show()

    def run_catalog(self):
        # deactivate infocube
        if self.infocube_is_active:
            self.infocube.unload()
            self.infocube = None
            self.infocube_is_active = False

        if not self.catalog_is_active:
            self.catalog_is_active = True
            if self.catalog is None:
                self.catalog = CatalogTool(self.iface, BBoxTool(self.iface))

        self.catalog.run()

    def run_infocube(self):
        # deactivate catalog
        if self.catalog_is_active:
            self.catalog.unload()
            self.catalog = None
            self.catalog_is_active = False
        # deactivate vectors
        if self.vectors_is_active:
            self.vectors.unload()
            self.vectors = None
            self.vectors_is_active = False

        if not self.infocube_is_active:
            self.infocube_is_active = True

            if self.infocube is None:
                self.infocube = InfoCubeConnect(self.iface)
                self.infocube.initGui()

        self.infocube.run()

    def run_vectors(self):
        # deactivate infocube
        if self.infocube_is_active:
            self.infocube.unload()
            self.infocube = None
            self.infocube_is_active = False

        if not self.vectors_is_active:
            self.vectors_is_active = True
            if self.vectors is None:
                self.vectors = VectorsTool(self.iface, BBoxTool(self.iface))

        self.vectors.run()

    def run_settings(self):
        if not self.settings_is_active:
            self.settings_is_active = True

            if self.settings is None:
                self.settings = SettingsTool(self.iface)
                self.settings.dialog.accepted.connect(self.on_settings_close)
                self.settings.dialog.rejected.connect(self.on_settings_close)

                self.settings.dialog.show()