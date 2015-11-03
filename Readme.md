
## DigitalGlobe Connect for [QGIS](https://github.com/qgis) ##

DigitalGlobe Connect for QGIS is a Plugin application allowing users to tap into the power of DigitalGlobe GBDx.  Users can browse and download results from our vast archive imagery catalog as well as our Vector Index.



<h3>Instructions</h3>

<ol>
    <li>In your plugin directory, compile the resources file using pyrcc4 (simply run <b>make</b> if you have automake or use <b>pb_tool</b>)
    <li>Test the generated sources using <b>make test</b> (or run tests from your IDE)
    <li>Copy the entire directory containing your new plugin to the QGIS plugin directory (see Notes below)
    <li>Test the plugin by enabling it in the QGIS plugin manager
    <li>Customize it by editing the implementation file <b>DGX.py</b>
    <li>Create your own custom icon, replacing the default <b>icon.png</b>
    <li>Modify your user interface by opening <b>DGX_dialog_base.ui</b> in Qt Designer
</ol>

##### Notes: #####
<ul>
    <li>You can use the <b>Makefile</b> to compile and deploy when you
        make changes. This requires GNU make (gmake). The Makefile is ready to use, however you 
        will have to edit it to add addional Python source files, dialogs, and translations.
    <li>You can also use <b>pb_tool</b> to compile and deploy your plugin. Tweak the <i>pb_tool.cfg</i> file included with your plugin as you add files. Install <b>pb_tool</b> using 
        <i>pip</i> or <i>easy_install</i>. See <a href="http://loc8.cc/pb_tool">http://loc8.cc/pb_tool</a> for more information.
<li>For information on writing PyQGIS code, see <a href="http://loc8.cc/pyqgis_resources">http://loc8.cc/pyqgis_resources</a> for a list of resources.
</ul>

### Account access ###

Please contact <a href="analytics.support@digitalglobe.com">analytics.support@digitalglob.com</a> for a user account to access the full content and data holdings within GBDx







