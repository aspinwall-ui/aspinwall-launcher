# coding: utf-8
"""
Basic tests for the launcher
"""
import time
import os
import pytest
from gi import require_version as gi_require_version
gi_require_version("Gtk", "4.0")
gi_require_version('Adw', '1')
from gi.repository import Adw, Gtk, Gdk, Gio # noqa: F401
from gi.repository.Adw import Flap, ToastOverlay, ButtonContent, Leaflet # noqa: F401

@pytest.fixture
def window():
	"""Creates the launcher window for use in later tests"""
	resource = Gio.Resource.load(
		os.path.join(os.getenv('PWD'), 'output', 'data', 'aspinwall.gresource')
	)
	resource._register()

	launcher_resource = Gio.Resource.load(
		os.path.join(os.getenv('PWD'), 'output', 'src', 'launcher', 'aspinwall.launcher.gresource')
	)
	launcher_resource._register()

	import aspinwall.launcher.window

	app = Adw.Application(application_id='org.dithernet.aspinwall.Launcher')
	app.connect('activate', aspinwall.launcher.window.on_activate)

	aspinwall.launcher.window.on_activate(app)

	assert aspinwall.launcher.window.win is not None
	return aspinwall.launcher.window.win

def test_app_chooser(window):
	"""Tests the app chooser revealer."""
	assert window.launcher_flap

	window.show_app_chooser()
	time.sleep(0.1)
	window.launcher_flap.hide()

def test_widget_chooser(window):
	"""Tests the widget chooser."""
	assert window.widgetbox.widget_chooser

	window.widgetbox.show_chooser()
	time.sleep(0.1)
	window.widgetbox.widget_chooser.hide()
