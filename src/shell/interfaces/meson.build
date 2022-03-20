pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
submoduledir = join_paths(pkgdatadir, 'aspinwall', 'shell', 'interfaces')

interfaces_sources = [
  '__init__.py',
  'manager.py',
  'notification.py'
]

install_data(interfaces_sources, install_dir: submoduledir)
