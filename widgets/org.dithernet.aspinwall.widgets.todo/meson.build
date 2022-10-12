pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
submoduledir = join_paths(pkgdatadir, 'widgets', 'org.dithernet.aspinwall.widgets.todo')

todo_sources = [
    '__widget__.py'
]

install_data(todo_sources, install_dir: submoduledir)

subdir('schemas')
subdir('po')
