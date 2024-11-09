#!/usr/bin/python3
"""Module contains Arsenalist and Slave class for master purpose"""
from __future__ import annotations

import os
import pathlib
import time
from collections import deque
from dataclasses import dataclass
from typing import *

from django.forms.models import model_to_dict
from orcatrex.gcloud_utils import DockerUtility, GCloudUtility, ServerUtility
from orcatrex.models import Jobs
from orcatrex.models import Slave as ModelSlave


class PQError(Exception):

  def __init__(self, value: str) -> None:
    self.value = value

  def __str__(self):
    return f"Priority Queue error {self.value}"


class NoSlaveException(Exception):

  def __init__(self, value: str) -> None:
    self.value = value

  def __str__(self):
    return f"NoSlaveException error: {self.value}"


@dataclass
class Arsenalist:
  username: str
  hostname: str
  slack_id: str


@dataclass
class Slave:
  username: str
  hostname: str
  active: bool = False
  cpu: float | None = None
  used_mem: float | None = None
  free_mem: float | None = None
  number_of_executions: int = 0
  is_gcloud: bool = False


def get_slave_data():
  slaves = ModelSlave.objects.all().filter(active=True)
  data = {}
  for slave in slaves:
    data[slave.hostname] = model_to_dict(slave)
  return data


def get_jobs_data():
  jobs = Jobs.objects.filter(status="Pending").order_by("-created_at")
  jobs_q = deque()
  for job in jobs:
    jobs_q.append(model_to_dict(job))
  return jobs_q


def run_in_background(func, freq, *args, **kwargs):
  while True:
    func(*args, **kwargs)
    time.sleep(freq)


def slave_job_executor(slave, job_data):
  if slave["is_gcloud"]:
    server_obj = GCloudUtility(slave["hostname"])
    server_obj.activate_gcloud_account()
  else:
    server_obj = ServerUtility(slave["hostname"], slave["username"])
  docker = DockerUtility(server_obj)
  docker.kill_all_containers()
  docker.set_image("trade-ai-image")
  docker.load_docker_image()
  docker.start_docker_image()
  copy_to_server(slave, job_data["dir_name"])
  output = docker.run_docker_command(job_data["command"])
  return output


def walk_dir(files_list, path):
  for root, dirs, files in os.walk(path):
    for file in files:
      full_file_path = os.path.join(root, file).split("/")
      full_file_path.insert(2, "temp")
      full_file_path = "/".join(full_file_path)
      files_list.append(full_file_path)
    for dir_name in dirs:
      walk_dir(files_list, f"{path}/{dir_name}")


def copy_to_server(slave, dir_name):
  if slave["is_gcloud"]:
    server_obj = GCloudUtility(slave["hostname"])
    server_obj.activate_gcloud_account()
  else:
    server_obj = ServerUtility(slave["hostname"], slave["username"])

  files_list = []
  walk_dir(files_list, f"/home/tradeai/temp/{dir_name}")

  for file in files_list:
    temp_index = file.split("/").index("temp")
    file_dest = "/home/tradeai/" + "/".join(file.split("/")[temp_index + 1:])
    server_obj.scp(file, file_dest)


def get_best_slave(slave_data, slave_pq):
  best_slave = slave_pq.get()
  if not best_slave or slave_data[best_slave]["number_of_executions"] > 0:
    return None
  return slave_data[best_slave]


def execute_jobs(slave, job_data):
  # Currently keep only 1 ongoing execution per slave
  return slave_job_executor(slave, job_data)


# Recurring function to execute pending jobs when slaves are available
def check_job_queue(slave_data, slave_pq, job_q: deque):
  best_slave = slave_pq.get()
  if not best_slave or slave_data[best_slave]["number_of_executions"] > 0 or not len(job_q):
    return
  job_data = job_q.popleft()
  try:
    execute_jobs(slave_data[best_slave], job_data)
  except Exception as e:
    print(e)
    job_q.append(job_data)


def copy_image(slave, image_path):
  if slave["is_gcloud"]:
    server_obj = GCloudUtility(slave["hostname"])
  else:
    server_obj = ServerUtility(slave["hostname"], slave["username"])
  server_obj.scp(src=image_path, dest="~/trade-ai-image")


def check_slave_queue(slave_pq):
  for slave in ModelSlave.objects.all().order_by("number_of_executions").filter(active=True):
    slave_pq.add(model_to_dict(slave))
  return slave_pq


class CpuData(NamedTuple):
  cpu: float
  used_mem: float
  free_mem: float
  number_of_executions: int = 0


class PriorityQueue(object):

  def __init__(self):
    self.queue = {}

  def __str__(self):
    return ' '.join([f"{str(key)}: {str(value)}" for key, value in self.queue])

  # for checking if the queue is empty
  def isEmpty(self):
    return len(self.queue) == 0

  def isPresent(self, key):
    return key in self.queue

  # for inserting an element in the queue
  def add(self, data):
    self.queue[data["hostname"]] = data

  def update(self, data_id, cpu, used_mem, free_mem):
    if data_id not in self.queue:
      raise PQError("Data_id not present in PQ")
    self.add(data_id, cpu, used_mem, free_mem)

  def get(self, data_id=None):
    if data_id:
      return self.queue.get(data_id, None)

    min_key, min_value = 10**9, 10**9
    for key, value in self.queue.items():
      if value["number_of_executions"] < min_value:
        min_key = key
        min_value = value["number_of_executions"]

    return min_key if min_key != 10**9 else None

  # for popping an element based on Priority
  def delete(self) -> CpuData:
    try:
      max_val = -1 * 100000
      max_key = None
      for key in self.queue:
        if self.queue[key]["cpu"] > 70 or (self.queue[key]["used_mem"] / self.queue[key]["free_mem"]) < 0.3:
          continue
        consumption = self.queue[key]["cpu"] * (self.queue[key]["used_mem"] / self.queue[key]["free_mem"])
        if consumption > max_val:
          max_key = key
      item = self.queue[max_key]
      del self.queue[max_key]
      return item
    except IndexError:
      print()
      exit()
