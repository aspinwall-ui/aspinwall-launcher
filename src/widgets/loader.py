# coding: utf-8
"""
Contains code for loading widgets from files.
"""
from .data import WidgetData

from gi.repository import Gio, GLib
import importlib
import importlib.abc
import os
import sys
import types
import traceback

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

loaded_widgets_data = Gio.ListStore(item_type=WidgetData)

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

def load_widget_from_dir(widget_dir, root):
    widget_path = os.path.join(root, widget_dir, '__widget__.py')
    if not os.path.exists(widget_path):
        return None

    widget_load_id = _COMMON_PREFIX + os.path.basename(widget_dir).replace('.', '_')

    try:
        spec = importlib.util.spec_from_file_location(
                widget_load_id, widget_path,
                submodule_search_locations=[]
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    except: # noqa: E722
        traceback.print_exc()
        raise ValueError("Error while importing widget")

    try:
        widget_class = module._widget_class
    except AttributeError:
        raise ValueError("No widget class in " + widget_path)

    try:
        widget_class.metadata['id']
    except KeyError:
        raise ValueError("No ID set in metadata of " + widget_path)

    _widget_specs[widget_load_id] = spec

    module._widget_class.widget_path = widget_path

    return module._widget_class

def load_available_widgets():
    """
    Loads widgets from files into the available_widgets variable, and
    returns the list of available widgets.
    """
    loaded_ids = []
    errors = []
    for root in widget_dirs:
        for widget_dir in os.listdir(root):
            if widget_dir == '__pycache__':
                continue
            widget_path = os.path.join(root, widget_dir, '__widget__.py')

            try:
                widget_class = load_widget_from_dir(widget_dir, root)
            except ValueError as e:
                errors.append((widget_path, str(e)))

            if widget_class:
                module_id = widget_class.metadata['id']
                if module_id in loaded_ids:
                    print(
                        'WARN: ID conflict between %s (loaded) and %s (attempted to load) while loading %s; ignoring file' # noqa: E501
                        % (loaded_ids[module_id].widget_path,
                        widget_path,
                        module_id)
                    )
                    continue
                loaded_ids.append(module_id)
                loaded_widgets_data.append(WidgetData(widget_class))

    return errors or None

def update_available_widgets():
    """Updates the list of available widgets."""
    old_loaded_ids = [widget.metadata['id'] for widget in loaded_widgets_data].copy()
    new_loaded_ids = old_loaded_ids.copy()
    new_paths = []
    errors = []
    loaded_widget_paths = [widget.path for widget in loaded_widgets_data]
    for root in widget_dirs:
        for widget_dir in os.listdir(root):
            if widget_dir == '__pycache__':
                continue
            widget_path = os.path.join(root, widget_dir, '__widget__.py')
            if widget_path in loaded_widget_paths:
                new_paths.append(widget_path)
                continue

            try:
                widget_class = load_widget_from_dir(widget_dir, root)
            except ValueError as e:
                errors.append((os.path.join(root, widget_dir, '__widget__.py'), str(e)))

            if widget_class:
                module_id = widget_class.metadata['id']
                if module_id in new_loaded_ids:
                    continue
                new_loaded_ids.append(module_id)
                new_paths.append(widget_path)
                loaded_widgets_data.append(WidgetData(widget_class))

    i = 0
    for widget_path in loaded_widget_paths:
        if widget_path not in new_paths:
            loaded_widgets_data.remove(i)
        i += 1

    print(errors)

    return errors or None

def get_widget_class_by_id(widget_id):
    """
    Takes a widget ID and returns the widget class of the widget with the
    provided ID, if available. Returns None if not found.
    """
    for widget in loaded_widgets_data:
        if widget.metadata['id'] == widget_id:
            return widget.widget_class
    return None
