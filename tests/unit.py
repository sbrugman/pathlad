import pytest

from pathlad.find_pattern import fix_str


unchanged = [
    'root = Path(tmp_path / "dummy_project").resolve()',
    'import sqlalchemy.dialects.postgresql as postgresqltypes',
]

spacing = {
    "import os\n\nos.path.abspath(\n    \"/home/test\"\n)\n\nos.path.abspath(\"/home/test\")\n":  "import os\nfrom pathlib import Path\n\nPath(\"/home/test\").resolve()\n\nPath(\"/home/test\").resolve()\n",
    "os.path.isabs(\n\txyz\n)": 'Path(xyz).is_absolute()',
}

tests = {
    'context_path = os.path.join(project_path, "great_expectations")': 'context_path = Path(project_path) / "great_expectations"',
    'asset_config_path = os.path.join(context_path, "expectations")': 'asset_config_path = Path(context_path) / "expectations"',
    'os.makedirs(asset_config_path, exist_ok=True, mode=0o666)': 'Path(asset_config_path).mkdir(exist_ok=True, mode=0o666, parents=True)',
    'os.makedirs(asset_config_path, exist_ok=True)': 'Path(asset_config_path).mkdir(exist_ok=True, parents=True)',
    'os.makedirs(asset_config_path)': 'Path(asset_config_path).mkdir(parents=True)',
    'os.mkdir(asset_config_path)': 'Path(asset_config_path).mkdir()',
    'os.mkdir(asset_config_path, mode=0o666)': 'Path(asset_config_path).mkdir(mode=0o666)',
    'open(doc_path, \'w\')': 'Path(doc_path).open(\'w\')',
    'open(doc_path, "r", encoding="utf-8")': 'Path(doc_path).open("r", encoding="utf-8")',
    'open(doc_path)': 'Path(doc_path).open()',
    'xyz = os.getcwd()': 'xyz = Path.cwd()',
    'os.path.same(xyz, abc)': 'Path(xyz).samefile(abc)',
    'os.path.isabs(xyz)': 'Path(xyz).is_absolute()',
    'os.path.isdir(xyz)': 'Path(xyz).is_dir()',
    'os.path.isfile(xyz)': 'Path(xyz).is_file()',
    'os.path.isfile(path=xyz)': 'Path(xyz).is_file()',
    'os.path.islink(xyz)': 'Path(xyz).is_symlink()',
    'os.path.exists(xyz)': 'Path(xyz).exists()',
    'os.path.basename(xyz)': 'Path(xyz).name',
    'os.path.dirname(xyz)': 'Path(xyz).parent',
    'os.path.expanduser(xyz)': 'Path(xyz).expanduser()',
    'os.remove(xyz)': 'Path(xyz).unlink()',
    'os.unlink(xyz)': 'Path(xyz).unlink()',
    'os.rmdir(xyz)': 'Path(xyz).rmdir()',
    'os.rename(xyz, abc)': 'Path(xyz).rename(abc)',
    'os.replace(xyz, abc)': 'Path(xyz).replace(abc)',
    'os.link(xyz, abc)': 'Path(xyz).link(abc)',
    'os.chmod(xyz, 0o444)': 'Path(xyz).chmod(0o444)',
    'os.stat(xyz)': 'Path(xyz).stat()',
    "os.path.join(self._datasource.data_context.root_directory, self._base_directory)": "Path(self._datasource.data_context.root_directory) / self._base_directory",
    "os.path.isabs(self._base_directory)": "Path(self._base_directory).is_absolute()",
    'open(file_relative_path(__file__, "checkpoint_template.py"))': 'Path(file_relative_path(__file__, "checkpoint_template.py")).open()',
    "os.mkdir(os.path.join(project_root_dir, 'great_expectations'))": "Path(Path(project_root_dir) / 'great_expectations').mkdir()",
    'os.makedirs(os.path.join(context_path, "plugins"))': 'Path(Path(context_path) / "plugins").mkdir(parents=True)',
    'os.path.normpath(xyz)': 'Path(xyz).resolve()',
    'os.path.realpath(xyz)': 'Path(xyz).resolve()',
    'os.path.getsize(xyz)': 'Path(xyz).stat().st_size',
    '{"base_directory": os.path.join(datasource.data_context.root_directory, "datasources", datasource.name, "generators", name), "other": True}': '{"base_directory": Path(datasource.data_context.root_directory) / "datasources" / datasource.name / "generators" / name, "other": True}',
    'static_assets_source_dir = file_relative_path(__file__, os.path.join("..", "..", "render", "view", "static"))': 'static_assets_source_dir = file_relative_path(__file__, Path("..") / ".." / "render" / "view" / "static")',
    'os.makedirs(os.path.join(asset_config_path, "my_dag_node"),exist_ok=True,)': 'Path(Path(asset_config_path) / "my_dag_node").mkdir(exist_ok=True, parents=True)',
    'os.listdir(xyz)': 'list(Path(xyz).glob("*"))',
    'os.listdir(path=xyz)': 'list(Path(xyz).glob("*"))',
    'os.listdir()': 'list(Path(".").glob("*"))',
    'os.path.join(self.full_base_directory, *prefix)': 'Path(self.full_base_directory).joinpath(*prefix)',
    'open(os.path.join(root, "setup.cfg"), "a")': 'Path(Path(root) / "setup.cfg").open("a")'

    # Future work:
    # 'os.path.join(xyz, os.pardir)', 'Path(xyz).parent',
    # 'glob.glob(os.path.join(self.base_directory, glob_config["glob"]))': 'Path(self.base_directory).glob(glob_config["glob"])',
    # 'import glob': '',
    # 'import glob.glob': '',
    # 'from glob import glob': '',
    # 'import os': '',
    # 'os.path.isdir(os.path.join(local_site_dir, "snor"))': '(Path(local_site_dir) / "snor").is_dir()',
    # "with Path(\"f1.csv\").open() as fp:\n\tdata = fp.read()": 'data = Path("f1.csv").read_text()',
    # "with Path(\"f1.csv\").open('rb') as fp:\n\tdata = fp.read()": 'data = Path("f1.csv").read_bytes()',
    # 'with open(nb_file, "w") as f:\n    f.write("")': 'Path(nb_file).touch()',
    # 'with open(nb_file, "w") as f:\n    f.write("test")': 'Path(nb_file).write_text("test")',
    # "glob.glob(os.path.join(path, \"*.py\"))": "Path(path).glob(\"*.py\")",
    # 'os.path.splittext(xyz)': '(Path(xyz).stem, Path(xyz).suffix)',
    # 'os.path.splittext(xyz)[0]': 'Path(xyz).stem',
    # 'os.path.splittext(xyz)[1]': 'Path(xyz).suffix',
    # 'os.path.split(xyz)`: `(Path(xyz).parent, Path(xyz).name)`,
    # 'os.path.split(xyz)[0]`: `Path(xyz).parent`,
    # 'os.path.split(xyz)[1]`: `Path(xyz).name`,
    # 'os.walk(xyz)': 'Path(xyz).glob()',
    # 'os.scandir(xyz)': 'Path(xyz).glob()',
    # 'glob("/path/to/directory/*/")': 'Path("/path/to/directory/").glob("*/")',
    # 'os.removedirs(xyz)': 'shutils',
    # "open(filename, mode='wt').write('')": "Path(filename).touch()"
    # 'Path("/home/very/long/path") / ".."': 'Path("/home/very/long/path").parent'

}


@pytest.mark.parametrize(argnames="input,output", argvalues=tests.items())
def test_path_rewrite(input, output):
    result = fix_str(input)
    assert result == output


@pytest.mark.parametrize(argnames="value", argvalues=unchanged)
def test_path_unchanged(value):
    result = fix_str(value)
    assert result == value


@pytest.mark.parametrize(argnames="input,output", argvalues=spacing.items())
def test_path_spacing(input, output):
    result = fix_str(input)
    assert result == output
