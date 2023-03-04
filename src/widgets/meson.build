pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
submoduledir = join_paths(pkgdatadir, 'aspinwall_launcher', 'widgets')
python = import('python')

widgets_sources = [
  '__init__.py',
  'data.py',
  'loader.py',
  'package.py',
]

install_data(widgets_sources, install_dir: submoduledir)
