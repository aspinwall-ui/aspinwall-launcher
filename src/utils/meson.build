pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
submoduledir = join_paths(pkgdatadir, 'aspinwall', 'utils')

utils_sources = [
  '__init__.py',
  'dimmable.py',
]

install_data(utils_sources, install_dir: submoduledir)

