import argparse

import requests
from exceptions import AccountError


def _parse_args():
  parser = argparse.ArgumentParser()
  opt_parser = parser.add_subparsers(dest="account_type", help="Type of account")
  arsenalist = opt_parser.add_parser("arsenalist", description="Arsenalist account parser")
  slave = opt_parser.add_parser("slave", description="Slave account parser")
  # Arsenalist
  arsenalist.add_argument("--slack_channel_id", help="Slack channel id to send alerts to", required=True)
  for acc in [arsenalist, slave]:
    acc.add_argument("--username", help="Actual username on machine", required=True)
    acc.add_argument("--hostname", help="Hostname of machine", required=True)

  return vars(parser.parse_args())


def register_account(username: str, hostname: str, slack_id: str | None = None):
  """Register your OrcaTrex account here

  Args:
    username (str): Username of the account on your machine.
    hostname (str): Hostname of the account on your machine.
    slack_id (str | None): Slack id of the account you want your job results on.
  """
  account_data = {"username": username, "hostname": hostname}
  if slack_id is not None:
    account_data["slack_id"] = slack_id

  response = requests.post("<url>/register_account", data={"username": username, "hostname": hostname, "slack_id": slack_id})
  if response.status_code == 200:
    print("Success")
  else:
    raise AccountError("Error while creating your account.")


def _main():
  """Entry point for CLI usage"""
  args = _parse_args()
  if args["account_type"] == "arsenalist":
    register_account(args["username"], args["hostname"], args["slack_channel_id"])
  else:
    register_account(args["username"], args["hostname"])


if __name__ == "__main__":
  _main()
