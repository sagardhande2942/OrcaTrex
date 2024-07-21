"""Module contains Arsenalist and Slave class for master purpose"""
from dataclasses import dataclass
from typing import *


class PQError(Exception):

  def __init__(self, value: str) -> None:
    self.value = value

  def __str__(self):
    return f"Priority Queue error {self.value}"


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


"""
cpupq.getlowest() -> first element
cpupq.update(slave_id, cpu, mem) -> (get the element in pq with slave_id and update & also update the pq comp)
"""


class CpuData(NamedTuple):
  cpu: float
  used_mem: float
  free_mem: float


class PriorityQueue(object):

  def __init__(self):
    self.queue = {}

  def __str__(self):
    return ' '.join([f"{str(key)}: {str(value)}" for key, value in self.queue])

  # for checking if the queue is empty
  def isEmpty(self):
    return len(self.queue) == 0

  # for inserting an element in the queue
  def add(self, data_id, cpu, used_mem, free_mem):
    self.queue[data_id] = CpuData(cpu, used_mem, free_mem)

  def update(self, data_id, cpu, used_mem, free_mem):
    if data_id not in self.queue:
      raise PQError("Data_id not present in PQ")
    self.add(data_id, cpu, used_mem, free_mem)

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
