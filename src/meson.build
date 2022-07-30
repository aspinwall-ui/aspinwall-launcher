pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
moduledir = join_paths(pkgdatadir, 'aspinwall_launcher')
gnome = import('gnome')

python = import('python')

conf = configuration_data()
conf.set('PYTHON', python.find_installation('python3').path())
conf.set('VERSION', meson.project_version())
conf.set('localedir', join_paths(get_option('prefix'), get_option('localedir')))
conf.set('pkgdatadir', pkgdatadir)

configure_file(
  input: 'aspinwall-launcher.in',
  output: 'aspinwall-launcher',
  configuration: conf,
  install: true,
  install_dir: get_option('bindir')
)

module_sources = [
  '__init__.py',
  'config.py',
  'main.py',
]

install_data(module_sources, install_dir: moduledir)

subdir('launcher')
subdir('utils')
subdir('widgets')
