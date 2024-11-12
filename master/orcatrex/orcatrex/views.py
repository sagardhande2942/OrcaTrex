import threading
from collections import deque

from django.forms.models import model_to_dict
from django.http import HttpResponse
from orcatrex.models import Jobs
from orcatrex.models import Slave as ModelSlave
from orcatrex.utils import (check_job_queue, copy_image, execute_jobs, run_in_background,kill_all_glcoud_server_containers)
from rest_framework.response import Response
from rest_framework.views import APIView

# Background job queue checker
job_queue_executor = threading.Thread(target=run_in_background, args=(check_job_queue, 10))
job_queue_executor.daemon = True
job_queue_executor.start()


class GetJobs(APIView):

  def post(self, request):
    command = request.data.get("command")
    dir_name = request.data.get("dir")

    best_slave = ModelSlave.objects.filter(number_of_executions=0)
    job_data = Jobs(command=command, dir_name=dir_name)
    job_data.save()

    if not best_slave.exists():
      return Response(data={'data': best_slave}, status=404)
    best_slave = best_slave.first()

    best_slave.number_of_executions = best_slave.number_of_executions + 1
    best_slave.save()
    job_update = Jobs.objects.filter(id=job_data.id)
    job_update.update(status="Running")
    execute_jobs(model_to_dict(best_slave), model_to_dict(job_data))
    # Update job status to Running and then Completed
    best_slave.number_of_executions = best_slave.number_of_executions - 1
    best_slave.save()
    job_update.update(status="Completed")

    return Response(status=200)


class SlaveAdder(APIView):

  def post(self, request):

    username = request.data.get("username")
    hostname = request.data.get("hostname")
    active = request.data.get("active", False)
    is_gcloud = request.data.get("is_gcloud", False)

    if not username or not hostname:
      return Response(data={"error": "Username/hostname not provided"}, status=420)

    new_slave = ModelSlave(username=username, hostname=hostname, active=active, is_gcloud=is_gcloud)
    new_slave.save()

    copy_image(model_to_dict(new_slave), "/home/tradeai/trade-ai-image")

    return Response(status=200)


class UpdateImage(APIView):

  def post(self, request):
    global SLAVE_DATA
    hostname = request.data.get("hostname")

    copy_image(model_to_dict(ModelSlave.objects.filter(hostname=hostname).first()), "/home/tradeai/trade-ai-image")

    return Response(status=200)
  
class KillAllServerContainers(APIView):
  
  def post(self,request):
    kill_all_glcoud_server_containers()
    return Response(status=200)