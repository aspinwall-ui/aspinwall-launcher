pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
submoduledir = join_paths(pkgdatadir, 'widgets', 'org.dithernet.aspinwall.widgets.todo')

notepad_sources = [
	'todo.py'
]

install_data(notepad_sources, install_dir: submoduledir)

subdir('schemas')
subdir('po')
