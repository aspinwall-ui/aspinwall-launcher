# coding: utf-8
"""
Contains tests for the widget API.
"""
import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk
from uuid import uuid4

from aspinwall_launcher.widgets import Widget

class ExampleWidget(Widget):
	"""Example widget class used for tests."""
	metadata = {
		"id": "org.dithernet.aspinwall.widgets.testwidget",
		"name": "Test widget",
		"icon": 'dialog-information-symbolic',
		"description": "This is a widget used for tests.",
		"tags": 'test,test widget,example'
	}

	# Normally this is set by the loader, but we make it manually here
	widget_path = '/'

	def __init__(self, instance):
		super().__init__(instance)

def test_widget():
	"""Creates a widget and tests its basic functions."""
	widget = ExampleWidget(instance=uuid4)
	assert widget
	assert widget.instance

	# Make sure style provider is created correctly
	assert type(widget.css_provider) == Gtk.CssProvider

	# By default, widgets that don't set their own refresh function have an
	# empty placeholder function that always returns None:
	assert widget.refresh() is None

	# Test properties
	assert widget.id == widget.metadata['id']
	assert widget.name == widget.metadata['name']
	assert widget.icon_name == widget.metadata['icon']
	assert widget.description == widget.metadata['description']
	assert widget.tags == widget.metadata['tags'].split(',')
