pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
submoduledir = join_paths(pkgdatadir, 'aspinwall', 'shell')

shell_ui_sources = [
  'panel.ui',
]

install_data(shell_ui_sources, install_dir: join_paths(submoduledir, 'ui'))
