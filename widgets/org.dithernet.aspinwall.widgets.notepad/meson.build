pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
submoduledir = join_paths(pkgdatadir, 'widgets', 'org.dithernet.aspinwall.widgets.notepad')

notepad_sources = [
    '__widget__.py'
]

install_data(notepad_sources, install_dir: submoduledir)

subdir('schemas')
subdir('stylesheet')
subdir('po')
