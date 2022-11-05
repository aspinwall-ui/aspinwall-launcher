pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
submoduledir = join_paths(pkgdatadir, 'widgets', 'org.dithernet.aspinwall.widgets.worldclock')

notepad_sources = [
    '__widget__.py',
    'settings.py'
]

install_data(notepad_sources, install_dir: submoduledir)

subdir('schemas')
subdir('stylesheet')
subdir('po')

gnome.compile_resources('org.dithernet.aspinwall.widgets.WorldClock',
  'org.dithernet.aspinwall.widgets.WorldClock.gresource.xml',
  gresource_bundle: true,
  install: true,
  install_dir: submoduledir,
)
