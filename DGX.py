# -*- coding: utf-8 -*-
"""
/***************************************************************************
 DGX
                                 A QGIS plugin
 DGX is a DigitalGlobe product enabling data search, download and analytics capabilities for vector and raster commercial, open source and proprietary data sources.  
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
import os.path

from About.AboutDialog import AboutDialog
from Catalog.CatalogTool import CatalogTool
from InfoCube.InfoCubeConnect import InfoCubeConnect
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, Qt, pyqtSlot
from PyQt4.QtGui import QAction, QIcon
from Vectors.VectorsTool import VectorsTool
import resources

TOOL_CATALOG = "Catalog"
TOOL_INFO_CUBE = "InfoCube"
TOOL_VECTORS = "Vectors"
TOOLS = [TOOL_CATALOG, TOOL_INFO_CUBE, TOOL_VECTORS]


class DGX:
    @pyqtSlot()
    def on_about_close(self):
        if self.about:
            self.about = None
        self.about_is_active = False

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
            'DGX_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&DGX')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'DGX')
        self.toolbar.setObjectName(u'DGX')

        #print "** INITIALIZING DGX"

        self.about = None
        self.about_is_active = False

        self.tool_is_active_dict = {}
        self.tool_dict = {}
        for tool_key in TOOLS:
            self.tool_is_active_dict[tool_key] = False
            self.tool_dict[tool_key] = None


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
        return QCoreApplication.translate('DGX', message)


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
        self.add_action(':/plugins/DGX/About.png',
                        text=self.tr(u'About'),
                        callback=self.run_about,
                        parent=self.iface.mainWindow())
        self.add_action(':/plugins/DGX/InfoCube.png',
                        text=self.tr(u'InfoCube'),
                        callback=self.run_infocube,
                        parent=self.iface.mainWindow())
        self.add_action(':/plugins/DGX/Catalog.png',
                        text=self.tr(u'Catalog'),
                        callback=self.run_catalog,
                        parent=self.iface.mainWindow())
        self.add_action(':/plugins/DGX/Vectors.png',
                        text=self.tr(u'Vectors'),
                        callback=self.run_vectors,
                        parent=self.iface.mainWindow())

    #--------------------------------------------------------------------------

    def onClosePlugin(self):
        """Cleanup necessary items here when plugin dockwidget is closed"""

        #print "** CLOSING DGX"

        # disconnects

        # remove this statement if dockwidget is to remain
        # for reuse if plugin is reopened
        # Commented next statement since it causes QGIS crashe
        # when closing the docked window:
        # self.dockwidget = None

        self.about = None

        for tool_key in self.tool_dict:
            tool = self.tool_dict.get(tool_key)
            if tool:
                tool.unload()
            self.tool_dict[tool_key] = None
            self.tool_is_active_dict[tool_key] = False


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""

        #print "** UNLOAD DGX"

        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&DGX'),
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

    def run_tool(self, target_tool_key):
        # stop other tools
        for tool_key in TOOLS:
            if tool_key != target_tool_key:
                if self.tool_is_active_dict[tool_key]:
                    tool = self.tool_dict[tool_key]
                    tool.unload()
                    self.tool_dict[tool_key] = None
                    self.tool_is_active_dict[tool_key] = False

        # start target tool
        if not self.tool_is_active_dict[target_tool_key]:
            self.tool_is_active_dict[target_tool_key] = True

            if self.tool_dict[target_tool_key] is None:
                tool = None
                if target_tool_key == TOOL_CATALOG:
                    tool = CatalogTool(self.iface)
                elif target_tool_key == TOOL_INFO_CUBE:
                    tool = InfoCubeConnect(self.iface)
                elif target_tool_key == TOOL_VECTORS:
                    tool = VectorsTool(self.iface)
                else:
                    raise ValueError("Unable to run tool; target tool key is invalid: %s" % target_tool_key)
                self.tool_dict[target_tool_key] = tool

        self.tool_dict[target_tool_key].run()

    def run_infocube(self):
        self.run_tool(TOOL_INFO_CUBE)

    def run_catalog(self):
        self.run_tool(TOOL_CATALOG)

    def run_vectors(self):
        self.run_tool(TOOL_VECTORS)
