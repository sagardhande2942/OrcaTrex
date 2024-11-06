from django.db import models


class Slave(models.Model):
  username = models.CharField(max_length=100, help_text="Username of the host machine")
  hostname = models.CharField(max_length=100, help_text="hostname/email of the host machine", primary_key=True)
  active = models.BooleanField(default=True, help_text="Is the server active?")
  cpu = models.FloatField(default=0, help_text="Cpu usage of the server")
  used_mem = models.FloatField(default=0, help_text="Mem usage of the server")
  free_mem = models.FloatField(default=0, help_text="Free mem available on the server")
  number_of_executions = models.IntegerField(default=0, help_text="Ongoing number of executions on the server")
  is_glcoud = models.BooleanField(default=False, help_text="Whether the server is a gcloud server")


class Jobs(models.Model):
  command = models.CharField(max_length=200, help_text="Command to be executed")
  dir_name = models.CharField(max_length=200, help_text="Dir name of updated files")
  status = models.TextChoices("Completed", "Pending", "Running", default="Pending", help_text="Is Job still pending?")
  created_at = models.DateTimeField(auto_now_add=True)
