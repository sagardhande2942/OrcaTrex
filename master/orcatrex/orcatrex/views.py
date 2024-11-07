import threading
from collections import deque

from django.forms.models import model_to_dict
from django.http import HttpResponse
from orcatrex.models import Jobs
from orcatrex.models import Slave as ModelSlave
from orcatrex.utils import (PriorityQueue, check_job_queue, copy_to_server, execute_jobs, get_best_slave, get_jobs_data,
                            get_slave_data, run_in_background)
from rest_framework.response import Response
from rest_framework.views import APIView

SLAVE_DATA = get_slave_data()
SLAVE_PQ = PriorityQueue()
JOBS_Q = get_jobs_data()

# Background job queue checker
job_queue_executor = threading.Thread(target=run_in_background, args=(check_job_queue, 10, SLAVE_DATA, SLAVE_PQ, JOBS_Q))
job_queue_executor.daemon = True
job_queue_executor.start()


class GetJobs(APIView):

  def post(self, request):
    command = request.data.get("command")
    dir_name = request.data.get("dir")

    best_slave = get_best_slave(SLAVE_DATA, SLAVE_PQ)
    job_data = Jobs(command=command, dir_name=dir_name)
    job_data.save()

    if not best_slave:
      JOBS_Q.append(job_data)
      return Response(data={'data': best_slave}, status=420)

    SLAVE_DATA[best_slave]["number_of_existing_executions"] += 1
    execute_jobs(best_slave, model_to_dict(job_data))

    # Update job status to Running and then Completed
    job_update = Jobs.objects.filter(id=job_data.id)
    job_update.update(status="Running")
    SLAVE_DATA[best_slave]["number_of_existing_executions"] -= 1
    job_update.update(status="Completed")

    return Response(status=200)


class SlaveAdder(APIView):

  def post(self, request):
    global SLAVE_DATA

    username = request.data.get("username")
    hostname = request.data.get("hostname")
    active = request.data.get("active", False)
    is_gcloud = request.data.get("is_gcloud", False)

    if not username or not hostname:
      return Response(data={"error": "Username/hostname not provided"}, status=420)

    new_slave = ModelSlave(username=username, hostname=hostname, active=active, is_gcloud=is_gcloud)
    new_slave.save()

    SLAVE_DATA[new_slave.hostname] = model_to_dict(new_slave)

    return Response(status=200)
