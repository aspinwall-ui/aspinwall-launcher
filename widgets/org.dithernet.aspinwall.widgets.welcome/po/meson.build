pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
submoduledir = join_paths(pkgdatadir, 'widgets', 'org.dithernet.aspinwall.widgets.welcome')

i18n.gettext('org.dithernet.aspinwall.widgets.welcome', 
	preset: 'glib', install_dir: join_paths(submoduledir, 'po'),
	args: '--keyword=translatable')
