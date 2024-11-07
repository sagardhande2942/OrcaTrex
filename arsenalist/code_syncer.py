import subprocess

FILES_REGEX = ["abc/exec_*.py", "utils/*.py", "execptions/main.py"]


def sync(user, hostname, files, dir_name):
  command = f"""sshpass -pViS29@@@ rsync -a -m --include='{"' --include='".join(files)} ~/trad/ {user}@{hostname}:~/temp/"""
  result = subprocess.run(command, check=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
  return result


def execute_remote(command):
  result = subprocess.run(command, check=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
  return result
