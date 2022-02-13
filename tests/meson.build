envdata = environment()
python_paths = [join_paths(get_option('prefix'), 'share', 'aspinwall'), meson.current_source_dir()]
envdata.append('PYTHONPATH', python_paths)

python = import('python').find_installation('python3')

test('Run tests', python,
  args: ['-m', 'pytest', '../tests'],
  env: envdata
)
