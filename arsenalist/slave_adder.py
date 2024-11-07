"""Utility module to send slave data to the master for new slave workers"""

from __future__ import annotations

import argparse

import requests


def _parse_args():
  """Argparser function"""
  parser = argparse.ArgumentParser(description="Entrypoint in job sender")
  parser.add_argument("-active", type=bool, action="store_true", help="Whether the slave is active initially", default=True)
  parser.add_argument("-gcloud", type=bool, action="store_true", help="Whether the slave is gcloud", default=True)
  parser.add_argument("--slave_account", type=str, help="Account name of the slave", default="cloudshell")
  parser.add_argument("--slave_id", type=str, help="Account ip in case of normal linux. Email in case of GCP", required=True)
  parser.add_argument("--master_ip", type=str, help="IP of the master")
  parser.add_argument("--master_port", type=str, help="Port of the master")
  return vars(parser.parse_args())


def _main():
  """Entrypoint to module"""
  args = _parse_args()
  requests.post(
    f"http://{args['master_ip']}:{args['master_port']}/orcatrex/add_slave", data={
      "username": args["slave_account"],
      "hostname": args["slave_id"],
      "active": args["active"],
      "is_gcloud": args["gcloud"]
    })


if __name__ == "__main__":
  _main()
