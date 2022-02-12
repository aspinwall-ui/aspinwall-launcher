# coding: utf-8
"""
Contains code for loading widgets from files.
"""
from gi.repository import GLib
import importlib
import os

user_widget_dir = os.path.join(GLib.get_user_data_dir(), 'aspinwall', 'widgets')
widget_dirs = [user_widget_dir]

if not os.path.exists(user_widget_dir):
	os.makedirs(user_widget_dir)

for data_dir in GLib.get_system_data_dirs():
	dir = os.path.join(data_dir, 'aspinwall', 'widgets')
	if not os.path.exists(dir):
		continue
	widget_dirs.append(dir)

available_widgets = []

def load_widgets():
	"""
	Loads widgets from files into the available_widgets variable, and
	returns the list of available widgets.
	"""
	loaded_ids = {}
	for dir in widget_dirs:
		for widget_dir in os.listdir(dir):
			if widget_dir == '__pycache__':
				continue
			for widget_file in os.listdir(os.path.join(dir, widget_dir)):
				if widget_file.endswith('.py'):
					widget = os.path.splitext(widget_file)[0]
					widget_path = os.path.join(dir, widget_dir, widget_file)

					spec = importlib.util.spec_from_file_location(widget, widget_path)
					module = importlib.util.module_from_spec(spec)
					spec.loader.exec_module(module)

					if module._widget_class.id in loaded_ids.keys():
						print(
							'WARN: ID conflict between %s (loaded) and %s (attempted to load) while loading %s; ignoring file' # noqa: E501
							% (loaded_ids[module._widget_class.id].widget_path,
							widget_path,
							module._widget_class.metadata['id'])
						)
						continue

					module._widget_class.widget_path = widget_path

					loaded_ids[module._widget_class.id] = module._widget_class
					available_widgets.append(module._widget_class)

	return available_widgets

def get_widget_class_by_id(widget_id):
	"""
	Takes a widget ID and returns the widget class of the widget with the
	provided ID, if available. Returns None if not found.
	"""
	for widget in available_widgets:
		if widget.metadata['id']:
			return widget
	return None
