pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
submoduledir = join_paths(pkgdatadir, 'aspinwall_launcher', 'utils')

utils_sources = [
  '__init__.py',
  'clock.py',
  'dimmable.py',
]

install_data(utils_sources, install_dir: submoduledir)

