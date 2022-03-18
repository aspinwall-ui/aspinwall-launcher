pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
submoduledir = join_paths(pkgdatadir, 'widgets', 'org.dithernet.aspinwall.widgets.welcome')

welcome_sources = [
	'welcome.py'
]

install_data(welcome_sources, install_dir: submoduledir)

subdir('po')
