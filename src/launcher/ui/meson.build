pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
submoduledir = join_paths(pkgdatadir, 'aspinwall', 'launcher')

launcher_ui_sources = [
  'about.ui',
  'appchooser.ui',
  'appicon.ui',
  'clockbox.ui',
  'launcher.ui',
  'launcherwidget.ui',
  'settings.ui',
  'wallpaper.ui',
  'wallpapericon.ui',
  'widgetbox.ui',
  'widgetchooser.ui',
  'widgetheader.ui',
  'widgetinfobox.ui',
]

install_data(launcher_ui_sources, install_dir: join_paths(submoduledir, 'ui'))
