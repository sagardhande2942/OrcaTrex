import datetime
import pathlib

from django.forms.models import model_to_dict
from django.http import HttpResponse
from django.views import View
from orcatrex.models import Slave as ModelSlave
from orcatrex.utils import PriorityQueue, copy_project_dirs, get_slave_data

SLAVE_DATA = get_slave_data()
SLAVE_PQ = PriorityQueue()


class GetJobs(View):
  command: str
  files: list[str]

  def post(self, request):
    self.command = request.POST.get("command")
    self.dir_name = request.POST.get("dir")
    trade = pathlib.Path("/home/tradeai/")

    # Need to sync code
    return HttpResponse(status=200)


class SlaveAdder(View):

  # @Arsenalist Only Method
  def post(self, request):
    global SLAVE_DATA
    username = request.POST.get("username")
    hostname = request.POST.get("hostname")
    active = request.POST.get("active", False)
    is_gcloud = request.POST.get("is_gcloud", False)
    new_slave = ModelSlave(username=username, hostname=hostname, active=active, is_gcloud=is_gcloud)
    new_slave.save()
    SLAVE_DATA[new_slave.hostname] = model_to_dict(new_slave)


class HealthChecker(View):

  # Takes in the heart beat from slaves which contains data about CPU and Memonry usage
  def post(self, request):
    ...
