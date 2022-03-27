# coding: utf-8
"""
Contains code for the X11 window list/interaction interface.
"""
from gi.repository import GObject
from ewmh import EWMH

from aspinwall.shell.interfaces.window import Window, ProtocolSpecificInterface

class X11WindowInterface(ProtocolSpecificInterface):
	"""
	Interface for getting information about open windows, compatible with EWMH.
	"""
	__gtype_name_ = 'X11WindowInterface'

	def __init__(self, window_interface):
		"""Initializes the X11/EWMH window inteface."""
		super().__init__(window_interface)

		self.ewmh = EWMH()
		self.update_windows()

	def update_windows(self):
		"""Updates the window list."""
		self.clients = self.ewmh.getClientList()
		for window in self.clients:
			visible = True

			# Get window switcher visibility by parsing window states and type
			window_states = self.ewmh.getWmState(window, str=True)
			for state in window_states:
				if state == '_NET_WM_STATE_SKIP_TASKBAR' or \
				   state == ' _NET_WM_STATE_SKIP_PAGER':
					visible = False

			window_type = self.ewmh.getWmWindowType(window, str=True)[0]
			if window_type == '_NET_WM_WINDOW_TYPE_DESKTOP' or \
			   window_type == '_NET_WM_WINDOW_TYPE_DOCK':
				visible = False

			# Get title
			title = None
			for property in ['_NET_WM_VISIBLE_NAME', '_NET_WM_NAME', 'WM_NAME']:
				result = self.ewmh._getProperty(property, window)
				if result:
					if property != 'WM_NAME':
						title = result.decode('utf-8')
					else:
						title = result
					break

			# Get icon data (TODO: Actually use it?)
			icon_data = self.ewmh._getProperty('_NET_WM_ICON', window)

			window_object = Window(
				title=title,
				visible=visible
			)
			self.windows.append(window_object)
