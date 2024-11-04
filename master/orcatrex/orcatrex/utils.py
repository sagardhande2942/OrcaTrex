#!/usr/bin/python3
"""Module contains Arsenalist and Slave class for master purpose"""
from dataclasses import dataclass
from typing import *

from orcatrex.gcloud_utils import DockerUtility, GCloudUtility, ServerUtility


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
  number_of_existing_executions: int = 0
  is_gcloud: bool = False


"""
To be run after code sync from api endpoint under job_id folder
"""


def slave_job_executor(slave, job_data):
  if slave.is_gcloud:
    server_obj = GCloudUtility(slave.hostname)
    server_obj.activate_gcloud_account()
  else:
    server_obj = ServerUtility(slave.hostname)
  docker = DockerUtility(server_obj)
  docker.load_docker_image()
  docker.start_docker_image()
  output = docker.run_docker_command(job_data["command"])
  return output


def execute_jobs(slave_data, slave_pq, job_data):
  best_slave = slave_pq.get()

  # Currently keep only 1 ongoing execution per slave
  if not best_slave or slave_data[best_slave].number_of_existing_executions > 0:
    raise NoSlaveException("No healthy slave currently available")

  return slave_job_executor(slave_data[best_slave], job_data)


class CpuData(NamedTuple):
  cpu: float
  used_mem: float
  free_mem: float
  number_of_existing_executions: int = 0


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
  def add(self, data_id, cpu, used_mem, free_mem):
    self.queue[data_id] = CpuData(cpu, used_mem, free_mem)

  def update(self, data_id, cpu, used_mem, free_mem):
    if data_id not in self.queue:
      raise PQError("Data_id not present in PQ")
    self.add(data_id, cpu, used_mem, free_mem)

  def get(self, data_id=None):
    if data_id:
      return self.queue.get(data_id, None)

    min_key, min_value = 10**9, 10**9
    for key, value in self.queue.items():
      if value.number_of_existing_executions < min_value:
        min_key = key
        min_value = value.number_of_existing_executions

    return min_key

  # for popping an element based on Priority
  def delete(self) -> CpuData:
    try:
      max_val = -1 * 100000
      max_key = None
      for key in self.queue:
        if self.queue[key].cpu > 70 or (self.queue[key].used_mem / self.queue[key].free_mem) < 0.3:
          continue
        consumption = self.queue[key].cpu * (self.queue[key].used_mem / self.queue[key].free_mem)
        if consumption > max_val:
          max_key = key
      item = self.queue[max_key]
      del self.queue[max_key]
      return item
    except IndexError:
      print()
      exit()
