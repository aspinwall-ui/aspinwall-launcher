# coding: utf-8
"""
Contains the Dimmable mixin for objects that can be dimmed.
"""

class Dimmable:
    """
    Mixin for objects that can be dimmed.

    Dimmable objects must have the .dimmable style class.

    Dimmed objects are given the .dim style class, and undimming the object
    removes the .dim style class.
    """

    def dim(self):
        """Dims the object."""
        self.add_css_class('dim')

    def undim(self):
        """Undims the object."""
        self.remove_css_class('dim')
