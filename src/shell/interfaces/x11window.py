# coding: utf-8
"""
Contains code for the X11 window list/interaction interface.
"""
from gi.repository import GdkPixbuf
from ewmh import EWMH
import threading
import Xlib
from Xlib import X

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
		display = self.ewmh.display
		focus_event = Xlib.protocol.event.ClientMessage(
			window=self.x11_window,
			client_type=display.intern_atom('_NET_ACTIVE_WINDOW'),
			data=(
				32, [2, X.CurrentTime, 0, 0, 0]
			)
		)

		mask = (X.SubstructureRedirectMask | X.SubstructureNotifyMask)
		display.send_event(
			destination=display.screen().root,
			propagate=False,
			event_mask=mask,
			event=focus_event
		)

	def close(self):
		"""Closes the window."""
		display = self.ewmh.display
		focus_event = Xlib.protocol.event.ClientMessage(
			window=self.x11_window,
			client_type=display.intern_atom('_NET_CLOSE_WINDOW'),
			data=(
				32, [X.CurrentTime, 2, 0, 0, 0]
			)
		)

		mask = (X.SubstructureRedirectMask | X.SubstructureNotifyMask)
		display.send_event(
			destination=display.screen().root,
			propagate=False,
			event_mask=mask,
			event=focus_event
		)

class X11WindowInterface(ProtocolSpecificInterface):
	"""
	Interface for getting information about open windows, compatible with EWMH.
	"""
	__gtype_name_ = 'X11WindowInterface'

	windows = None

	def __init__(self, window_interface):
		"""Initializes the X11/EWMH window inteface."""
		super().__init__(window_interface)

		self.ewmh = EWMH()
		self.update_windows()

		event_handler = threading.Thread(target=self.event_handler_func, daemon=True)
		event_handler.start()

	def event_handler_func(self):
		"""Handles events."""
		root = self.ewmh.display.screen().root
		mask = (
			X.StructureNotifyMask |
			X.PropertyChangeMask |
			X.VisibilityChangeMask |
			X.FocusChangeMask |
			X.SubstructureNotifyMask
		)
		root.change_attributes(event_mask=mask)

		update_trigger_atoms = [
			self.ewmh.display.intern_atom('_NET_CLOSE_WINDOW'),
			self.ewmh.display.intern_atom('_NET_DESTROY_WINDOW'),
			self.ewmh.display.intern_atom('_NET_CLIENT_LIST'),
			self.ewmh.display.intern_atom('_NET_CLIENT_LIST_STACKING')
		]

		while True:
			event = root.display.next_event()
			if event.type == X.PropertyNotify and event.atom in update_trigger_atoms:
				# Some property we're watching for has changed
				self.update_windows()
			elif event.type == X.FocusIn or event.type == X.FocusOut:
				# Focus changed
				self.update_windows()
			elif event.type == X.DestroyNotify or event.type == X.UnmapNotify:
				# Window closed
				self.update_windows()
			elif event.type == X.MapNotify or event.type == X.MapRequest:
				# Window shown
				self.update_windows()
			# Otherwise, we don't know how to handle the event

	def update_windows(self):
		"""Updates the window list."""
		new_clients = self.ewmh.getClientList()
		if self.windows:
			old_clients = self.clients
			if new_clients != old_clients:
				scan_clients = []
				diff_clients = list(set(old_clients) - set(new_clients)) + \
					list(set(new_clients) - set(old_clients))
				for client in diff_clients:
					if client not in new_clients:
						# Client removed, drop from store
						for window in list(self.windows):
							print(window)
							if window.x11_window == client:
								self.windows.remove(self.windows.find(window)[1])
								break
					else:
						# Client added, add to re-scan list
						scan_clients.append(client)
				self.clients = new_clients
			else:
				# Nothing for us to update
				return
		else:
			self.clients = new_clients
			scan_clients = self.clients

		for window in scan_clients:
			visible = True

			# Get window switcher visibility by parsing window states and type
			window_states = self.ewmh.getWmState(window, str=True)
			for state in window_states:
				if state == '_NET_WM_STATE_SKIP_TASKBAR' or \
				   state == ' _NET_WM_STATE_SKIP_PAGER':
					visible = False

			window_type_output = self.ewmh.getWmWindowType(window, str=True)
			if window_type_output:
				window_type = window_type_output[0]
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
