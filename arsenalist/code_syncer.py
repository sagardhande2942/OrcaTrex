import subprocess

FILES_REGEX = ["abc/exec_*.py", "utils/*.py", "execptions/main.py"]


def sync(user, hostname, files, dir_name):
  command = f"""sshpass -pViS29@@@ rsync -a -m --include='{"' --include='".join(files)}' --include='*/' --exclude='*' ~/trad/ {user}@{hostname}:~/temp/{dir_name}"""
  print(command)
  result = subprocess.run(command, check=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
  return result


def execute_remote(master_ip, master_account, command):
  result = ""
  try:
    result = subprocess.run(f'sshpass -pViS29@@@ ssh {master_account}@{master_ip} "' + command + '"', check=True, shell=True,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
  except Exception as e:
    print(result)
    print(e)
    raise e
  return result
