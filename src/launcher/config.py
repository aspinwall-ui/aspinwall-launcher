# coding: utf-8
"""
Handles configuration for the Aspinwall launcher
"""
from gi.repository import Gio

config = Gio.Settings.new('org.dithernet.aspinwall.launcher')

# Load background settings from GNOME if the GNOME schemas are available.
# This code looks up whether the schema is present in the default schema
# source; if we just tried to make Gio.Settings from a schema that can't
# be found, the program would crash on startup (and the crash couldn't be
# caught from a try/except block).
_default_schema_source = Gio.SettingsSchemaSource.get_default()
if _default_schema_source.lookup('org.gnome.desktop.background', True):
	bg_config = Gio.Settings.new('org.gnome.desktop.background')
else:
	bg_config = None
