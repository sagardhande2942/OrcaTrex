""" Utility module to send jobs to the master for orchestration """

from __future__ import annotations

import argparse
import pathlib

import code_syncer
import paramiko
import requests


# TODO(sdhande): Create a job splitter utility on our siden which will auto create jfile & efile
def _parse_args():
  """Argparser function"""
  parser = argparse.ArgumentParser(description="Entrypoint in job sender")
  parser.add_argument("--job_file", type=pathlib.Path, help="Path to the job file")
  parser.add_argument("--exec_file", type=pathlib.Path, help="Path to the execution format file")
  parser.add_argument("--master_username", type=str, help="Username of the master for scp")
  parser.add_argument("--master_ip", type=str, help="IP of the master")
  parser.add_argument("--master_port", type=str, help="Port of the master")
  parser.add_arggument("-sync_code", action="store_true", help="Whether you want your code to be synced for this job")
  return vars(parser.parse_args())


def send_codebase(ip: str, username: str, tar_path: pathlib.Path):
  client = paramiko.SSHClient()
  client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
  client.connect(ip, username)
  sftp = client.open_sftp()
  sftp.put(tar_path, f"/home/{username}/tmp/codebase.tar")


def send_jobs(ip: str, port: str, sync_code: bool, jfile: pathlib.Path, efile: pathlib.Path):
  """ Sends job to the master server endpoint

  Args:
    ip (str): Ip of the master server
    port (str): Port of the master server
    sync_code (bool): Whether we are syncing code base for this job
    jfile (str): Path to the job file
    efile (str): Path to the job file
  """
  jdata = jfile.read_text()
  edata = efile.read_text()
  requests.post(f"http://{ip}:{port}/orcatrex/send_job", data={"jdata": jdata, "edata": edata, "sync_code": sync_code})


def _main():
  """Entrypoint to module"""
  args = _parse_args()
  if args["sync_code"]:
    tar_path = code_syncer.sync()    
    send_codebase(args["master_ip"], args["master_username"], tar_path)
  send_jobs(args["master_ip"], args["master_port"], args["sync_code"], args["job_file"], args["exec_file"])


if __name__ == "__main__":
  _main()
