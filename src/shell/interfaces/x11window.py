# coding: utf-8
"""
Contains code for the X11 window list/interaction interface.
"""
from gi.repository import GdkPixbuf, GObject
from ewmh import EWMH

from aspinwall.shell.interfaces.window import Window, ProtocolSpecificInterface

class X11Window(Window):
	"""Represents an X11 window."""
	__gtype_name__ = 'X11Window'

	def __init__(self, ewmh, x11_window, **kwargs):
		"""Initializes an X11Window object."""
		super().__init__(**kwargs)
		self.ewmh = ewmh
		self.x11_window = x11_window

	def focus(self):
		"""Focuses the window."""
		self.ewmh.setActiveWindow(self.x11_window)

	def close(self):
		"""Closes the window."""
		self.ewmh.setCloseWindow(self.x11_window)

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

			# The icon data is provided as an array of "32-bit packed CARDINAL
			# ARGB with high byte being A, low byte being B". We need to
			# convert this to a format that GdkPixbuf can understand.
			icon_data = self.ewmh._getProperty('_NET_WM_ICON', window)
			icon_pixbuf = None

			if icon_data:
				new_data = []

				# The first two items represent the width/height of the icon
				icon_width = icon_data[0]
				icon_height = icon_data[1]

				# The remainder of the data is used for image data. We need to
				# extract the argb values and add them to the list that will be
				# used by GdkPixbuf (which follows a format of "r, g, b, a, r,
				# g, b, a, ...")
				count = -1
				current_height = 1
				current_width = 1
				for bit in icon_data:
					count += 1
					if count <= 1:
						continue
					a = (bit & 0xff000000) >> 24
					r = (bit & 0x00ff0000) >> 16
					g = (bit & 0x0000ff00) >> 8
					b = (bit & 0x000000ff)

					new_data.append(r)
					new_data.append(g)
					new_data.append(b)
					new_data.append(a)

				rowstride = GdkPixbuf.Pixbuf.calculate_rowstride(
					GdkPixbuf.Colorspace.RGB, True, 8, icon_width, icon_height
				)

				icon_pixbuf = GdkPixbuf.Pixbuf.new_from_data(
					new_data,
					GdkPixbuf.Colorspace.RGB,
					True, 8,
					icon_width, icon_height,
					rowstride
				)

			window_object = X11Window(
				ewmh=self.ewmh,
				x11_window=window,
				title=title,
				icon_pixbuf=icon_pixbuf,
				visible=visible
			)
			self.windows.append(window_object)
