"""Main slave module"""

from __future__ import annotations

import argparse
import pathlib
import time

from job_handler import JobHandler

from utils.fnotifier import Fnotifier


def _parse_args():
  parser = argparse.ArgumentParser(description="ClI for Slave Module")
  parser.add_argument("--job_file", type=pathlib.Path, help="Job info file")
  parser.add_argument("--exec_file", type=pathlib.Path, help="Execution format for jobs")
  return vars(parser.parse_args())


def _main():
  args = _parse_args()
  running_jobs = []
  fnotifier = Fnotifier(args["job_file"])
  while True:
    completed_jobs = []
    if fnotifier.change_checker():
      handler = JobHandler(args["job_file"], args["exec_file"])
      running_jobs.append(handler)
      handler.start()

    completed_jobs = [job for job in running_jobs if job.complete()]
    running_jobs = [job for job in running_jobs if not job.complete()]

    #TODO(sdhande): Get logs from completed jobs and send to api
    time.sleep(1)


if __name__ == "__main__":
  _main()
