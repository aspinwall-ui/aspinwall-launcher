# coding: utf-8
"""
Contains code for loading widgets from files.
"""
from gi.repository import GLib
import importlib
import importlib.abc
import os
import sys
import types

user_widget_dir = os.path.join(GLib.get_user_data_dir(), 'aspinwall', 'widgets')
widget_dirs = [user_widget_dir]

if not os.path.exists(user_widget_dir):
    os.makedirs(user_widget_dir)

for data_dir in GLib.get_system_data_dirs():
    dir = os.path.join(data_dir, 'aspinwall', 'widgets')
    if not os.path.exists(dir):
        continue
    widget_dirs.append(dir)

if os.getenv('ASPINWALL_WIDGET_DIR'):
    widget_dirs += [os.getenv('ASPINWALL_WIDGET_DIR')]

available_widgets = []

# The implementation here is somewhat inspired by the following:
# - https://dev.to/dangerontheranger/dependency-injection-with-import-hooks-in-python-3-5hap
# Here, however, it's much simpler. The reason as to why this is needed
# in the first place is that this allows us to handle relative imports
# by making sure all loaded widgets are loaded as *modules*.

_COMMON_PREFIX = "aspinwall_launcher.loaded_widgets."
_widget_specs = {}

class WidgetDummyLoader(importlib.abc.Loader):
    """Dummy loader needed by WidgetFinder."""
    def __init__(self):
        self._dummy_module = types.ModuleType(_COMMON_PREFIX[:-1])
        self._dummy_module.__path__ = []

    def provides(self, fullname):
        return _COMMON_PREFIX.startswith(fullname)

    def create_module(self, spec):
        return self._dummy_module

    def exec_module(self, module):
        pass

class WidgetFinder(importlib.abc.MetaPathFinder):
    """Custom importlib finder implementation for Aspinwall widgets."""
    def __init__(self):
        self._dummy_loader = WidgetDummyLoader()

    def find_spec(self, fullname, path, target=None):
        # Handle aspinwall_launcher and aspinwall_launcher.loaded_widgets
        if _COMMON_PREFIX.startswith(fullname):
            spec = importlib.machinery.ModuleSpec(fullname, self._dummy_loader)
            return spec

        # If the path name is not provided, we may be trying to access
        # a relative import. We look in our dict of loaded widget paths:
        if not path and fullname in _widget_specs:
            return _widget_specs[fullname]

_finder = WidgetFinder()
sys.meta_path.append(_finder)

def load_available_widgets():
    """
    Loads widgets from files into the available_widgets variable, and
    returns the list of available widgets.
    """
    loaded_ids = {}
    errors = []
    for dir in widget_dirs:
        for widget_dir in os.listdir(dir):
            if widget_dir == '__pycache__':
                continue

            widget_path = os.path.join(dir, widget_dir, '__widget__.py')
            if not os.path.exists(widget_path):
                continue

            widget_load_id = _COMMON_PREFIX + os.path.basename(widget_dir).replace('.', '_')

            spec = importlib.util.spec_from_file_location(widget_load_id, widget_path, submodule_search_locations=[])
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            try:
                widget_class = module._widget_class
            except AttributeError:
                print("No widget class in " + widget_path)
                errors.append((widget_path, 'No widget class'))
                continue

            try:
                module_id = widget_class.metadata['id']
            except:
                print("No ID set in metadata of " + widget_path)
                errors.append((widget_path, 'No widget class'))
                continue

            if module_id in loaded_ids.keys():
                print(
                    'WARN: ID conflict between %s (loaded) and %s (attempted to load) while loading %s; ignoring file' # noqa: E501
                    % (loaded_ids[module_id].widget_path,
                    widget_path,
                    module_id)
                )
                continue

            _widget_specs[widget_load_id] = spec

            module._widget_class.widget_path = widget_path

            loaded_ids[module_id] = module._widget_class
            available_widgets.append(module._widget_class)

    return (available_widgets, errors)

def get_widget_class_by_id(widget_id):
    """
    Takes a widget ID and returns the widget class of the widget with the
    provided ID, if available. Returns None if not found.
    """
    for widget in available_widgets:
        if widget.metadata['id'] == widget_id:
            return widget
    return None
