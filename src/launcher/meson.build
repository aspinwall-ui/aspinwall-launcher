pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
submoduledir = join_paths(pkgdatadir, 'aspinwall_launcher', 'launcher')
gnome = import('gnome')

gnome.compile_resources('aspinwall.launcher',
  join_paths('ui', 'aspinwall.launcher.gresource.xml'),
  gresource_bundle: true,
  install: true,
  install_dir: pkgdatadir,
)

launcher_sources = [
  '__init__.py',
  'about.py',
  'app_chooser.py',
  'clockbox.py',
  'settings.py',
  'wallpaper.py',
  'widget_chooser.py',
  'widgetbox.py',
  'widgetview.py',
  'widgetmanager.py',
  'window.py',
]

install_data(launcher_sources, install_dir: submoduledir)

subdir('ui')
