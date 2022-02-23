# coding: utf-8
"""
Contains code for handling wallpapers
"""
import math
import os
from gi.repository import Gtk, Gdk, GdkPixbuf
from urllib.parse import urlparse

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
	return ((((red * 255)) << 24) |    # noqa: W504
			(((green * 255)) << 16) |  # noqa: W504
			(((blue * 255)) << 8) |    # noqa: W504
			((alpha * 255)))           # noqa: W504

@Gtk.Template(resource_path='/org/dithernet/aspinwall/launcher/ui/wallpaper.ui')
class Wallpaper(Gtk.Box, Dimmable):
	"""Wallpaper image that reads wallpaper data from the config."""
	__gtype_name__ = 'Wallpaper'

	wallpaper = Gtk.Template.Child()
	# TODO: properly source these two
	background_color = color_to_pixel([0, 0, 0])
	scale = 1

	def __init__(self):
		"""Initializes a Wallpaper object."""
		super().__init__()
		self.pixbuf = GdkPixbuf.Pixbuf()

		self.set_image_from_config()

		self.wallpaper.set_draw_func(self.draw)
		self.wallpaper.connect('resize', self.update)

		config.connect('changed::wallpaper-path', self.load_and_update_aspinwall)
		config.connect('changed::use-gnome-background', self.load_image_and_update)
		if bg_config:
			bg_config.connect('changed::picture-uri', self.load_and_update_gnome)

	def draw(self, area, cr, *args):
		"""Draws the background."""
		x = 0
		y = 0
		cr.save()
		cr.scale(1.0 / self.scale, 1.0 / self.scale)
		Gdk.cairo_set_source_pixbuf(cr, self.pixbuf, x * self.scale, y * self.scale)
		cr.paint()
		cr.restore()
		return True

	def set_image_from_config(self):
		"""
		Sets the image to a pixbuf created from the image file provided
		in the config file.
		"""
		# Use GNOME settings if available, and enabled
		if bg_config and config['use-gnome-background']:
			uri = urlparse(bg_config['picture-uri'])
			wallpaper_path = os.path.abspath(os.path.join(uri.netloc, uri.path))
		else:
			wallpaper_path = config['wallpaper-path']
		if wallpaper_path and not wallpaper_path == '/' and os.path.exists(wallpaper_path):
			self.image = GdkPixbuf.Pixbuf.new_from_file(wallpaper_path)
		else:
			self.image = None

	def update(self, *args):
		"""Updates the background."""
		window = self.get_root()
		width = window.get_width()
		height = window.get_height()

		if self.image:
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

	def load_image_and_update(self, *args):
		"""Convenience function for calling set_image_from_config and update"""
		self.set_image_from_config()
		self.update()
		self.wallpaper.queue_draw()

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
		bg = self.blank_bg()

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
