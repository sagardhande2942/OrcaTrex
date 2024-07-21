import tarfile

FILES_REGEX = [
  "abc/exec_*.py",
  "utils/*.py",
  "execptions/main.py"
]


def sync(tar_path: pathlib.Path = pathlib.Path("<home>/tmp/code_base.tar")):

  with tarfile.open(tar_path, "a") as tar:
    for regex in FILES_REGEX:
      for file in pathlib.Path("your/path/till/project/base/").glob(regex):
        tar.add(file, arcname=file.name)

  return tar_path

