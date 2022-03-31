pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())

conf = configuration_data()
conf.set('VERSION', meson.project_version())
conf.set('bindir', join_paths(get_option('prefix'), get_option('bindir')))

configure_file(
  input: 'autostart.in',
  output: 'autostart',
  configuration: conf,
  install: true,
  install_dir: join_paths(pkgdatadir, 'x11')
)

install_data('aspinwall.desktop',
  install_dir: join_paths(get_option('datadir'), 'xsessions')
)
