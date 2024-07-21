import dataclasses

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

SLAVE_DATA = []

class GetJobs(View):
  jdata: str
  edata: str

  def post(self, request):
    self.jdata = request.POST.get("jfile")
    self.edata = request.POST.get("efile")
    return HttpResponse(status=200)


class SlaveAdder(View):

  # @Arsenalist Only Method
  def post(self, request):
    global SLAVE_DATA
    username = request.POST.get("username")  
    hostname = request.POST.get("hostname")
    active = True if request.POST.get("active").lower() == "true" else False
    SLAVE_DATA.append(Slave(username, hostname, active))


class SlaveDumper(View):

  def get(self, request):
    dump_dict = {}
    for slave in SLAVE_DATA:
      dump_dict[slave.hostname] = dataclasses.asdict(slave)

    dump_path = pathlib.Path(f"/home/ubuntu/slave_dump/dump.json")
    dump_path.parent.mkdir(exist_ok=True)
    dump_path.write_text(json.dumps(dump_dict))

class SlaveLoader(View):
  global slave_data

  def get(self, request):
    dump_str = pathlib.Path("/home/ubuntu/slave_dump/dump.json").read_text()
    dump_dict = json.loads(dump_str)
    slave_hostnames = [slave.hostname for slave in SLAVE_DATA]
    for hostname, slave in dump_dict:
      if hostname not in slave_hostnames:
        SLAVE_DATA.append(Slave(**slave))


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
