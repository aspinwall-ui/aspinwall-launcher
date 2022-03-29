# coding: utf-8
"""
PulseAudio interface.
"""
from gi.repository import GObject
import pulsectl
import threading

from aspinwall.shell.interfaces import Interface

class PulseAudioInterface(Interface):
	"""
	Interface for PulseAudio. Supports volume changes and muting.
	"""
	__gtype_name__ = 'PulseAudioInterface'

	latest_change_is_ours = False

	def __init__(self):
		"""Initializes the PulseAudio interface."""
		super().__init__()
		try:
			# Use a separate client for listening to events. In theory, it might
			# be possible to use one with some clever thread manipulation,
			# and using event_listen_stop when needed, but it's much more complex
			# (and potentially has a higher chance of failure) than just using
			# two separate clients.
			self.listener_client = pulsectl.Pulse('aspinwall-shell-listener')
			self.client = pulsectl.Pulse('aspinwall-shell')
		except: # noqa: E722
			self.set_property('available', False)
			return
		else:
			self.set_property('available', True)

		if not self.client.sink_list():
			self.set_property('available', False)
			return

		self.setup_sinks()
		self.notify('volume')
		self.notify('muted')

		self.listener_client.event_listen_stop()
		self.listener_thread = threading.Thread(target=self.listener_func, daemon=True)
		self.listener_thread.start()

	def setup_sinks(self):
		"""Sets up the sinks handled by the daemon."""
		# Get default sink; this will be the sink used for volume control
		default_sink_name = self.client.server_info().default_sink_name
		self.sink = None
		for sink in self.client.sink_list():
			if sink.name == default_sink_name:
				self.sink = sink
				break
		if not self.sink:
			self.sink = self.client.sink_list()[0]

		# Get default input sink; this will be used for microphone control
		default_source_name = self.client.server_info().default_source_name
		self.source = None
		if self.client.source_list():
			for sink in self.client.source_list():
				if sink.name == default_source_name:
					self.source = sink
					break
			if not self.source:
				self.source = self.client.source_list()[0]

	def listener_func(self, *args):
		"""Function for the listener thread."""
		self.listener_client.event_mask_set('sink', 'sink_input')
		self.listener_client.event_callback_set(self.handle_event)
		self.listener_client.event_listen()

	def handle_event(self, event):
		"""Handles sink events."""
		if self.latest_change_is_ours:
			# If we performed the change, then we don't need to update the
			# sinks to get the new values
			self.latest_change_is_ours = False
		else:
			# If the change was done externally, the sink values don't
			# update automatically; we need to get the sinks again
			self.setup_sinks()
		self.notify('volume')
		self.notify('muted')

	@GObject.Property(type=int)
	def volume(self):
		"""Default sink's volume level (0-100)."""
		# Note that pulsectl uses 0.0-1.0 for volume, with higher
		# numbers being used for software volume boosting; thus,
		# we have to multiply the number accordingly.

		if self.sink:
			return self.client.volume_get_all_chans(self.sink) * 100
		return 0

	@volume.setter
	def set_volume(self, value):
		"""Sets the sink's volume."""
		if self.sink:
			self.latest_change_is_ours = True
			self.client.volume_set_all_chans(self.sink, value / 100)

	@GObject.Property(type=bool, default=False)
	def muted(self):
		"""Whether the default sink is muted or not."""
		return self.sink.mute

	@muted.setter
	def set_muted(self, value):
		"""Mutes/unmutes the sink according to the value."""
		if self.sink:
			self.latest_change_is_ours = True
			if value is True:
				self.client.mute(self.sink, True)
			else:
				self.client.mute(self.sink, False)

	def toggle_mute(self, *args):
		"""Toggles between muted/unmuted mode."""
		self.set_property('muted', not self.props.muted)

	@GObject.Property(type=bool, default=False)
	def input_muted(self):
		"""Whether the default input sink is muted or not."""
		if self.source:
			self.latest_change_is_ours = True
			return self.source.mute
		return False

	@input_muted.setter
	def set_input_muted(self, value):
		"""Mutes/unmutes the input sink according to the value."""
		if self.source:
			self.latest_change_is_ours = True
			if value is True:
				self.client.mute(self.source, True)
			else:
				self.client.mute(self.source, False)

	def toggle_input_mute(self, *args):
		"""Toggles between muted/unmuted mode."""
		self.set_property('input-muted', not self.props.input_muted)

	@GObject.Property(type=bool, default=False, flags=GObject.ParamFlags.READABLE)
	def has_input(self):
		"""Whether there's an input device present or not."""
		if self.source:
			return True
		return False
