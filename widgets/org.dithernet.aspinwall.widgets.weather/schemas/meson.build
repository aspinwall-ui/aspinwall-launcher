submodule_schemas_dir = join_paths(submoduledir, 'schemas')

gnome = import('gnome')

compile_schemas = find_program('glib-compile-schemas', required: true)
run_command(compile_schemas, '.', check: true)

install_data(
  ['org.dithernet.aspinwall.widgets.weather.gschema.xml',
   'gschemas.compiled',],
  install_dir: submodule_schemas_dir
)
