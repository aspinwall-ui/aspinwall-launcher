pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())

x11_sources = [
  'autostart',
]

install_data(x11_sources, install_dir: join_paths(pkgdatadir, 'aspinwall', 'x11'))

install_data('aspinwall.desktop',
  install_dir: join_paths(get_option('datadir'), 'xsession')
)
