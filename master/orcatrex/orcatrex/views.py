import threading
from collections import deque

from django.forms.models import model_to_dict
from django.http import HttpResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from orcatrex.models import Jobs
from orcatrex.models import Slave as ModelSlave
from orcatrex.utils import (PriorityQueue, check_job_queue, copy_to_server, execute_jobs, get_best_slave, get_jobs_data,
                            get_slave_data, run_in_background)

SLAVE_DATA = get_slave_data()
SLAVE_PQ = PriorityQueue()
JOBS_Q = get_jobs_data()

# Background job queue checker
job_queue_executor = threading.Thread(target=run_in_background, args=(check_job_queue, 10, SLAVE_DATA, SLAVE_PQ, JOBS_Q))
job_queue_executor.daemon = True
job_queue_executor.start()


@csrf_exempt
class GetJobs(View):
  command: str
  files: list[str]

  def post(self, request):
    self.command = request.POST.get("command")
    self.dir_name = request.POST.get("dir")
    best_slave = get_best_slave(SLAVE_DATA, SLAVE_PQ)
    job_data = Jobs(command=self.command, dir_name=self.dir_name)
    job_data.save()
    if not best_slave:
      JOBS_Q.append(job_data)
      return HttpResponse(status=420)
    SLAVE_DATA[best_slave]["number_of_existing_executions"] += 1
    execute_jobs(best_slave, model_to_dict(job_data))
    job_update = Jobs.objects.get(id=job_data.id)
    job_update.update(status="Running")
    SLAVE_DATA[best_slave]["number_of_existing_executions"] -= 1
    job_update = Jobs.objects.get(id=job_data.id)
    job_update.update(status="Completed")
    return HttpResponse(status=200)


@csrf_exempt
class SlaveAdder(View):

  # @Arsenalist Only Method
  def post(self, request):
    global SLAVE_DATA
    username = request.POST.get("username")
    hostname = request.POST.get("hostname")
    active = request.POST.get("active", False)
    is_gcloud = request.POST.get("is_gcloud", False)
    if not username and not hostname:
      return HttpResponse(content=b"Username/hostname not provided", status=420)
    new_slave = ModelSlave(username=username, hostname=hostname, active=active, is_gcloud=is_gcloud)
    new_slave.save()
    SLAVE_DATA[new_slave.hostname] = model_to_dict(new_slave)
    return HttpResponse(status=200)
