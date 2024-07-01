""" Utility module to send jobs to the master for orchestration """

from __future__ import annotations

import argparse
import pathlib

import requests


# TODO(sdhande): Create a job splitter utility on our siden which will auto create jfile & efile
def _parse_args():
  """Argparser function"""
  parser = argparse.ArgumentParser(description="Entrypoint in job sender")
  parser.add_argument("--job_file", type=pathlib.Path, help="Path to the job file")
  parser.add_argument("--exec_file", type=pathlib.Path, help="Path to the execution format file")
  parser.add_argument("--master_ip", type=str, help="IP of the master")
  parser.add_argument("--master_port", type=str, help="Port of the master")
  return vars(parser.parse_args())


def send_jobs(ip: str, port: str, jfile: pathlib.Path, efile: pathlib.Path):
  """ Sends job to the master server endpoint

  Args:
    ip (str): Ip of the master server
    port (str): Port of the master server
    jfile (str): Path to the job file
    efile (str): Path to the job file
  """
  jdata = jfile.read_text()
  edata = efile.read_text()
  requests.post(f"http://{ip}:{port}/orcatrex/send_job", data={"jdata": jdata, "edata": edata})


def _main():
  """Entrypoint to module"""
  args = _parse_args()
  send_jobs(args["master_ip"], args["master_port"], args["job_file"], args["exec_file"])


if __name__ == "__main__":
  _main()
