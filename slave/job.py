"""Module which defines the job class"""

from __future__ import annotations

import pathlib
import subprocess


class Job:

  def __init__(self, jid: str, command: str, args: list[str], env: str):
    self.jid = jid
    self.command = command
    self.args = args
    self.env = env
    self.log_dir = pathlib.Path.cwd().parent / "tmplogs"
    self.log_dir.mkdir(parents=True, exist_ok=True)
    self.log_file = self.log_dir / f"~/tmplogs/{jid}"
    self.log_file.unlink()
    self.log_file.touch(exist_ok=True)
    self.process: None | subprocess.Popen = None

  def __str__(self):
    return f"jid: {self.jid}\n command: {self.command}\n args: {' '.join(self.args)}\n env: {self.env}"

  def complete(self) -> bool:
    if self.process is None:
      raise subprocess.SubprocessError(f"Job not started {self}")
    if self.process.poll() is None:
      return False
    else:
      return True

  def start(self):
    args_str = " ".join(self.args)
    process = subprocess.Popen(["source", f"{self.env};", "{command}", args_str, "&>", str(self.log_file)])
    self.process = process
    return process
