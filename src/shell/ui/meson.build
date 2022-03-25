pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
submoduledir = join_paths(pkgdatadir, 'aspinwall', 'shell')

shell_ui_sources = [
  'controlpanel.ui',
  'controlpanelbutton.ui',
  'controlpanelcontainer.ui',
  'notificationbox.ui',
  'notificationpopup.ui',
  'panel.ui',
  'windowswitcher.ui',
  'windowview.ui',
]

install_data(shell_ui_sources, install_dir: join_paths(submoduledir, 'ui'))
