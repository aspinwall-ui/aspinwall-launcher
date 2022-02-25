# coding: utf-8
"""
Contains code for handling wallpapers
"""
from gi.repository import Gtk, Gdk, GdkPixbuf, GLib
from urllib.parse import urlparse
import math
import os
import threading
import traceback
import time
import uuid

from aspinwall.utils.dimmable import Dimmable
from aspinwall.launcher.config import config, bg_config

def color_to_pixel(color):
	"""Turns RGB color value to pixel value."""
	red = color[0]
	green = color[1]
	blue = color[2]
	alpha = 0
	if len(color) == 4:
		alpha = color[3]
	return ((((red)) << 24) |    # noqa: W504
			(((green)) << 16) |  # noqa: W504
			(((blue)) << 8) |    # noqa: W504
			((alpha)))           # noqa: W504

class SlideshowManager:
	"""Convenience class for managing slideshows."""
	def __init__(self):
		"""Initializes the SlideshowManager."""
		self.start_slideshow_mode_if_enabled()
		config.connect('changed::slideshow-mode', self.start_slideshow_mode_if_enabled)
		config.connect('changed::wallpaper-path', self.update_counter)
		config.connect('changed::slideshow-switch-delay', self.update_counter)

	def start_slideshow_mode_if_enabled(self, *args):
		"""
		Starts slideshow mode if the slideshow-mode config option is enabled.
		"""
		# The thread automatically quits if slideshow mode is disabled.
		# Here we can re-create it if needed.
		if config['slideshow-mode']:
			self.thread = threading.Thread(target=self.slideshow_thread_func)
			self.thread.start()

	def update_counter(self, *args):
		"""Updates the counter to match the delay."""
		self.counter = config['slideshow-switch-delay']

	def slideshow_thread_func(self):
		"""Wallpaper update thread."""
		self.counter = config['slideshow-switch-counter']
		while True:
			if not config['slideshow-mode']:
				return

			if self.counter <= 0:
				self.counter = config['slideshow-switch-delay']
				available_wallpapers = config['available-wallpapers']
				current_wallpaper = config['wallpaper-path']

				if current_wallpaper not in available_wallpapers:
					config['wallpaper-path'] = available_wallpapers[0]
				else:
					next_wallpaper_index = available_wallpapers.index(current_wallpaper) + 1
					if next_wallpaper_index >= len(available_wallpapers):
						next_wallpaper_index = 0
					config['wallpaper-path'] = available_wallpapers[next_wallpaper_index]

			self.counter -= 1
			config['slideshow-switch-counter'] = self.counter
			time.sleep(1)

@Gtk.Template(resource_path='/org/dithernet/aspinwall/launcher/ui/wallpaper.ui')
class Wallpaper(Gtk.Box, Dimmable):
	"""Wallpaper image that reads wallpaper data from the config."""
	__gtype_name__ = 'Wallpaper'

	wallpaper = Gtk.Template.Child()
	wallpaper_fade = Gtk.Template.Child()
	wallpaper_fade_drawable = Gtk.Template.Child()

	# TODO: properly source this
	scale = 1

	def __init__(self):
		"""Initializes a Wallpaper object."""
		super().__init__()
		self.pixbuf = GdkPixbuf.Pixbuf()
		self.fade_pixbuf = GdkPixbuf.Pixbuf()

		self.update_background_color()
		self.set_image_from_config()

		self.wallpaper.set_draw_func(self.draw)
		self.wallpaper.connect('resize', self.update)

		self.wallpaper_fade_drawable.set_draw_func(self.draw, 'fade_pixbuf')

		config.connect('changed::wallpaper-path', self.load_and_update_aspinwall)
		if bg_config:
			bg_config.connect('changed::picture-uri', self.load_and_update_gnome)
		config.connect('changed::wallpaper-scaling', self.load_image_and_update)
		config.connect('changed::wallpaper-color', self.load_image_and_update)
		config.connect('changed::use-gnome-background', self.load_image_and_update)

		self.slideshow_manager = SlideshowManager()

	def draw(self, area, cr, *args):
		"""Draws the background."""
		if args[-1] == 'fade_pixbuf':
			source_pixbuf = self.fade_pixbuf
		else:
			source_pixbuf = self.pixbuf
		x = 0
		y = 0
		cr.save()
		cr.scale(1.0 / self.scale, 1.0 / self.scale)
		Gdk.cairo_set_source_pixbuf(cr, source_pixbuf, x * self.scale, y * self.scale)
		cr.paint()
		cr.restore()
		return True

	def set_image_from_config(self):
		"""
		Sets the image to a pixbuf created from the image file provided
		in the config file.
		"""
		# Use GNOME settings if available and enabled
		if bg_config and config['use-gnome-background']:
			uri = urlparse(bg_config['picture-uri'])
			wallpaper_path = os.path.abspath(os.path.join(uri.netloc, uri.path))
		else:
			wallpaper_path = config['wallpaper-path']
		if wallpaper_path and not wallpaper_path == '/' and os.path.exists(wallpaper_path):
			try:
				self.image = GdkPixbuf.Pixbuf.new_from_file(wallpaper_path)
			except GLib.GError:
				traceback.print_exc()
				self.image = None
		else:
			self.image = None

	def update(self, *args):
		"""Updates the background."""
		window = self.get_root()
		width = window.get_width()
		height = window.get_height()

		self.fade_pixbuf = self.pixbuf

		if self.image:
			if config['wallpaper-scaling'] == 0:
				self.pixbuf = self.blank_bg(width, height)
			elif config['wallpaper-scaling'] == 1:
				self.pixbuf = self.scale_to_fit(width, height)
			else:
				self.pixbuf = self.scale_to_min(width, height)
		else:
			self.pixbuf = self.blank_bg(width, height)

	def load_and_update_gnome(self, *args):
		"""Reloads the GNOME background image if applicable."""
		if config['use-gnome-background'] and bg_config:
			self.load_image_and_update()

	def load_and_update_aspinwall(self, *args):
		"""Reloads the Aspinwall background image if applicable."""
		if not config['use-gnome-background']:
			self.load_image_and_update()

	def update_background_color(self, *args):
		"""Sets the background color based on the wallpaper-color setting."""
		self.background_color = color_to_pixel(config['wallpaper-color'])

	def load_image_and_update(self, *args):
		"""
		Convenience function to call when the wallpaper is changed.
		Automatically takes care of the wallpaper transition.
		"""
		self.wallpaper_fade_drawable.queue_draw()
		_fade_thread = threading.Thread(target=self.crossfade_wallpaper)
		_fade_thread.start()

		self.update_background_color()
		self.set_image_from_config()
		self.update()
		self.wallpaper.queue_draw()

	def crossfade_wallpaper(self, *args):
		"""Convenience function for fading out the wallpaper."""
		fading_out = str(uuid.uuid4())
		self.fading_out = fading_out

		self.wallpaper_fade.set_opacity(1)
		while self.wallpaper_fade.get_opacity() > 0:
			# Make sure another fadeout thread isn't running; if it is, let it
			# take over control.
			if self.fading_out != fading_out:
				return
			self.wallpaper_fade.set_opacity(self.wallpaper_fade.get_opacity() - 0.01)
			time.sleep(0.01)
		self.fading_out = False

	def blank_bg(self, width, height):
		"""Returns an empty pixbuf, filled with the background color."""
		bg = GdkPixbuf.Pixbuf.new(GdkPixbuf.Colorspace.RGB, False, 8, width, height)
		bg.fill(self.background_color)
		return bg

	def scale_to_min(self, min_width, min_height):
		"""Returns the background, zoomed in to fit."""
		src_width = self.image.get_width()
		src_height = self.image.get_height()

		factor = max(min_width / src_width, min_height / src_height)

		new_width = math.floor(src_width * factor + 0.5)
		new_height = math.floor(src_height * factor + 0.5)

		dest = GdkPixbuf.Pixbuf.new(
			GdkPixbuf.Colorspace.RGB,
			self.image.get_has_alpha,
			8, min_width, min_height
		)
		if not dest:
			return None

		# crop the result
		self.image.scale(dest,
			0, 0,
			min_width, min_height,
			(new_width - min_width) / -2,
			(new_height - min_height) / -2,
			factor,
			factor,
			GdkPixbuf.InterpType.BILINEAR
		)
		return dest

	def scale_to_fit(self, width, height):
		"""Returns the background, scaled to fit."""
		bg = self.blank_bg(width, height)

		orig_width = self.image.get_width()
		orig_height = self.image.get_height()
		ratio_horiz = width / orig_width
		ratio_vert = height / orig_height

		if ratio_horiz > ratio_vert:
			ratio = ratio_vert
		else:
			ratio = ratio_horiz
		final_width = math.ceil(ratio * orig_width)
		final_height = math.ceil(ratio * orig_height)

		off_x = (width - final_width) / 2
		off_y = (height - final_height) / 2
		self.image.composite(
			bg,
			off_x, off_y,
			final_width,
			final_height,
			off_x, off_y,
			ratio,
			ratio,
			GdkPixbuf.InterpType.BILINEAR,
			255)

		return bg
