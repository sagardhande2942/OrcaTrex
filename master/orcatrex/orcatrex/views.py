from django.http import HttpResponse
from django.views import View
from job_alerter import JobAlerter
from job_distributor import JobDistributor

# TODO(sdhande): Need global variables to store current job data, slave data (get from SlaveAdder), Arsenalist data(username), slave health, PQ for slave CPU & Mem
# TODO(sdhande): Need a daemon thread here for executing JobDistributor in background with global vars
# TODO(sdhande): Add util to not accept job from a Arsenalist if they are not registered. Similary slave will be considered active for executing if it is registered.
# TODO(sdhande): Add util to revive the slave. Re-revive the slave. With the fnotifier running
"""
1. Create Slave class (Global util?)
2. Create Arsenalist class (Global util?)
2. Auto revive slave once added
3. Reset Slave cpu and mem usage if inactive (PQ)
"""


class GetJobs(View):
  jdata: str
  edata: str

  def post(self, request):
    self.jdata = request.POST.get("jfile")
    self.edata = request.POST.get("efile")
    return HttpResponse(status=200)


# TODO(sdhande): Store the slave data in global SlaveData var.
# TODO(sdhande): Add utility to dump Slave Data to json file for recovering from crashes.
class SlaveAdder(View):

  # @Arsenalist Only Method
  def post(self, request):
    ...


# TODO(sdhande): Need a priority queue implementation for getting the idle CPU for job execution
class HealthChecker(View):

  # Takes in the heart beat from salves which contains data about CPU and Memonry usage
  def post(self, request):
    ...


class RegisterAccount(View):

  # TODO(sdhande): Takes the account details for Arsenalists. Data like username, public ip (maybe private ip as well), hostname, alert method (slack channel id)
  # TODO(sdhande): Store this data in the global Arsenalist data vars.
  # TODO(sdhande): Add ability to return appropriate response when user is already registered.
  def post(self, request):
    ...


# TODO(sdhande): Create a result getter utility to get result from slaves
# TODO(sdhande): Create a alerter utility to alert the Arsenalist in their preffered way (Slack for now)
class ResultGetter(View):

  def post(self, reuqest):
    ...
