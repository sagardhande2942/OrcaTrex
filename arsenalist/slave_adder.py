""" Utility module to send slave data to the master for new slave workers"""

from __future__ import annotations

import argparse
import pathlib

import requests


def _parse_args():
  """Argparser function"""
  parser = argparse.ArgumentParser(description="Entrypoint in job sender")
  # TODO(sdhande): Replace the default with gcloud user
  parser.add_argument("--slave_account", type=str, help="Account name of the slave", default="cloudshell")
  parser.add_argument("--slave_id", type=str, help="Account ip in case of normal linux. Email in case of GCP", required=True)
  parser.add_argument("--master_ip", type=str, help="IP of the master")
  parser.add_argument("--master_port", type=str, help="Port of the master")
  return vars(parser.parse_args())


# TODO(sdhande): Fix and complete the send_slaves function
def send_slaves(ip: str, port: str, slave_account, slave_id):
  """ Sends job to the master server endpoint

  Args:
    ip (str): Ip of the master server
    port (str): Port of the master server
  """
  # jdata = jfile.read_text()
  # edata = efile.read_text()
  # requests.post(f"http://{ip}:{port}/orcatrex/send_job", data={"jdata": jdata, "edata": edata})


def _main():
  """Entrypoint to module"""
  args = _parse_args()
  send_slaves(args["master_ip"], args["master_port"], args["slave_account"], args["slave_id"])


if __name__ == "__main__":
  _main()
