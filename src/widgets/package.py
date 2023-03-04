# coding: utf-8
"""
Contains code for extracting widget packages.
"""
from gi.repository import GObject
import os
import json
import shutil
import tarfile

from .loader import user_widget_dir

class WidgetPackage(GObject.Object):
    """Class for handling widget packages."""

    def __init__(self, path):
        super().__init__()
        self.path = path

        with tarfile.open(path, 'r') as pkgfile:
            # Get metadata
            try:
                metafile = pkgfile.extractfile('metadata.json')
            except KeyError:
                raise ValueError("No metadata.json file")
            self.metadata = json.load(metafile)

            # Make sure widget folder is present and contains widget
            try:
                pkgfile.getmember(self.metadata['id'])
            except KeyError:
                raise ValueError("No widget folder in package")

            try:
                pkgfile.getmember(os.path.join(self.metadata['id'], '__widget__.py'))
            except KeyError:
                raise ValueError("No __widget__.py file in package")

    def install(self):
        """Installs the widget package."""
        if os.path.exists(os.path.join(user_widget_dir, self.metadata['id'])):
            shutil.rmtree(os.path.join(user_widget_dir, self.metadata['id']))

        with tarfile.open(self.path, 'r') as pkgfile:
            pkgfile.extractall(path=user_widget_dir,
                members=[tarinfo for tarinfo in pkgfile.getmembers()
                    if tarinfo.name.startswith(self.metadata['id'] + '/')
                        and '/..' not in tarinfo.name and './' not in tarinfo.name # noqa: W503
                ]
            )

    @GObject.Property(type=str)
    def id(self):
        """The ID of the widget, as defined in its metadata."""
        return self.metadata['id']

    @GObject.Property(type=str)
    def version(self):
        """The version of the widget, as defined in its metadata."""
        return self.metadata['version']

    @GObject.Property(type=str)
    def name(self):
        """The name of the widget, as defined in its metadata."""
        return self.metadata['name']

    @GObject.Property(type=str)
    def author(self):
        """The author of the widget, as defined in its metadata."""
        return self.metadata['author']

    @GObject.Property(type=str)
    def icon_name(self):
        """The icon name of the widget, as defined in its metadata."""
        return self.metadata['icon']

    @GObject.Property(type=str)
    def description(self):
        """The description of the widget, as defined in its metadata."""
        return self.metadata['description']

    @GObject.Property
    def tags(self):
        """The tags of the widget, as defined in its metadata."""
        return self.metadata['tags'].split(',')
