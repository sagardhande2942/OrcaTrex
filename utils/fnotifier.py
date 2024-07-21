"""Module defining the job change checker"""

from __future__ import annotations

import pathlib


class Fnotifier:

  def __init__(self, file_path: pathlib.Path):
    self.file_path = file_path
    self.file_path.parent.mkdir(parents=True)
    self.file_path.touch(exist_ok=True)
    self.last_m_time = self.file_path.stat().st_mtime

  def change_checker(self) -> bool:
    # TODO(sdhande): As soon as new job file is detected, create a dir with job_id under ~/tmp/<job_id>/ to sync the code tar & then unzip it here with same name
    m_time = self.file_path.stat().st_mtime
    change = False
    if self.last_m_time < m_time:
      self.last_m_time = m_time
      change = True

    return change
