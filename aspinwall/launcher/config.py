# coding: utf-8
"""
Handles configuration for the Aspinwall launcher
"""
from gi.repository import GLib
import json
import os

class LauncherConfig:
	"""Contains the launcher configuration."""
	first_run = False

	def __init__(self, config_file):
		"""Initializes the config file."""
		self.config_file = config_file
		self.config_dict = {}
		if os.path.exists(config_file):
			with open(self.config_file, 'r') as file:
				self.config_dict = json.load(file)
		else:
			with open(self.config_file, 'w') as file:
				json.dump({}, file, indent=4)
			self.first_run = True

	def get(self, key):
		"""Gets a key from the configuration file."""
		try:
			return self.config_dict[key]
		except KeyError:
			return None

	def set(self, key, value):
		"""Sets the value of the provided key in the configuration file."""
		self.config_dict[key] = value

	def save(self):
		"""Saves the current configuration to the configuration file."""
		with open(self.config_file, 'w') as file:
			json.dump(self.config_dict, file, indent=4)

	def reload(self):
		"""Reloads the config file"""
		with open(self.config_file, 'r') as file:
			self.config_dict = json.load(file)

config_dir = os.path.join(GLib.get_user_config_dir(), 'aspinwall')
config_file = os.path.join(config_dir, 'launcher.json')
if not os.path.exists(config_dir):
	os.makedirs(config_dir)

config = LauncherConfig(config_file)
