from __future__ import annotations

import json
import pathlib
from typing import *

from job import Job
from jsoncomment import JsonComment


class JobHandler:

  def __init__(self, job_location: pathlib.Path, execution_format: pathlib.Path):
    self.job_location = job_location
    self.execution_format = execution_format
    self.parser = JsonComment(json)
    self.job_maps: dict[str, Any] = {}
    self.execution_data: dict[str, Any] = {}
    self.jid_pid_map: dict[str, str] = {}
    self.init_job: None | Job = None
    self.log_files: list[pathlib.Path] = []
    self.parse_jobs()
    self.parse_execution()

  def parse_jobs(self):
    data = self.parser.loads(self.job_location.read_text())
    for jid, data in data.items():
      job = Job(jid, data["command"], data["args"], data["env"])
      if "init_job" in data and data["init_job"]:
        self.init_job = job
      self.job_maps[jid] = job
      self.log_files.append(job.log_file)

  def parse_execution(self):
    data = self.parser.loads(self.execution_format.read_text())
    self.execution_data = {jid: data for jid, data in data.items()}

  def start_jobs(self):
    if self.init_job is None:
      # TODO(sdhande): Create own exception and replace here
      raise ValueError("No initial job")
    self.init_job.start()

  def start(self):
    self.start_jobs()

  def complete(self):
    if self.init_job is None:
      raise ValueError("No initial job")
    return self.init_job.complete()
