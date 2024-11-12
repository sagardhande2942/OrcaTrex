from __future__ import annotations

import re
import subprocess
import requests
import json

class GCloudUtility:

  def __init__(self, account_email,ip=None,port=6000):
    self.account_email = account_email
    self.username = self.account_email.split('@')[0]
    self.ip = ip
    self.port = port

  def run_command(self,command):
    """Runs a gcloud command and returns the output."""
    try:
      final_command = f'ssh -i /home/tradeai/.ssh/google_compute_engine -p 6000 -o StrictHostKeyChecking=no -o ServerAliveInterval=60 -o ServerAliveCountMax=5 {self.username}@{self.ip} "{command}"'
      print(final_command)
      result = subprocess.run(final_command, check=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
      return result.stdout.strip()
    except subprocess.CalledProcessError as e:
      print(f"Error running command: {e}")
      print(f"Output: {e.output}")
      print(f"Error: {e.stderr}")
      return None

  def start_machine(self):
    """Start The Gcloud shell machine"""
    access_token = self.get_access_token()
    url = "https://content-cloudshell.googleapis.com/v1/users/me/environments/default:start"

    headers = {
      'Content-Type': 'application/json',
      'Authorization': f'Bearer {access_token}'
    }

    response = requests.request("POST", url, headers=headers)

    if response.status_code !=200:
      return None
    else:
      return True

  def get_access_token(self):
    """
    fetches access token from gcloud cli

    Returns:
        _type_: string
    """
    self.activate_gcloud_account()
    command = f"gcloud auth print-access-token"
    result = subprocess.run(command, check=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return result.stdout.strip()
  
  def get_machine_ip_port(self):
    """Get Machine IP and Port"""
    url = "https://content-cloudshell.googleapis.com/v1/users/me/environments/default"

    payload = {}
    access_token = self.get_access_token()
    headers = {
      'Authorization': f'Bearer {access_token}'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 401:
      return None,None
    response = response.json()
    if response["state"] != 'RUNNING':
      return None,None
    else:
      return response["sshHost"],response["sshPort"]
    
  @staticmethod
  def list_gcloud_accounts():
    """Lists all authenticated Google Cloud accounts."""
    command = "gcloud auth list"
    output = GCloudUtility.run_command(command)
    emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', output)
    return emails

  def activate_gcloud_account(self):
    """Activates a specified Google Cloud account."""
    command = f"gcloud config set account {self.account_email}"
    result = subprocess.run(command, check=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return result.stdout.strip()

  def scp(self, src, dest):
    try:
      final_command = f'scp -i /home/tradeai/.ssh/google_compute_engine -P 6000 -o StrictHostKeyChecking=no -o ServerAliveInterval=60 -o ServerAliveCountMax=5 {src} {self.username}@{self.ip}:{dest}'
      result = subprocess.run(final_command, check=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
      return result.stdout.strip()
    except subprocess.CalledProcessError as e:
      print(f"Error running command: {e}")
      print(f"Output: {e.output}")
      print(f"Error: {e.stderr}")
      return None
  
  


class ServerUtility:

  def __init__(self, hostname, username):
    self.hostname = hostname
    self.username = username

  def run_command(self, command):
    """Runs a gcloud command and returns the output."""
    try:
      final_command = f'ssh self.hostname "{command}"'
      result = subprocess.run(final_command, check=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
      return result.stdout.strip()
    except subprocess.CalledProcessError as e:
      print(f"Error running command: {e}")
      print(f"Output: {e.output}")
      print(f"Error: {e.stderr}")
      return None

  def scp(self, src, dest):
    try:
      final_command = f'scp localhost:{src} {self.username}@{self.hostname}:{dest}'
      result = subprocess.run(final_command, check=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
      return result.stdout.strip()
    except subprocess.CalledProcessError as e:
      print(f"Error running command: {e}")
      print(f"Output: {e.output}")
      print(f"Error: {e.stderr}")
      return None


class DockerUtility:

  def __init__(self, server_obj):
    self.image = None
    self.image_id = None
    self.server = server_obj
    self.container_id = None

  def set_image(self, image):
    self.image = image

  def copy_files_to_container(self, src, dest):
    try:
      if not self.image or not self.container_id:
        raise ValueError("image/container for the docker is not set")
      final_command = f"docker cp {src} {self.container_id}:{dest}"
      result = subprocess.run(final_command, check=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
      return result.stdout.strip()
    except subprocess.CalledProcessError as e:
      print(f"Error running command: {e}")
      print(f"Output: {e.output}")
      print(f"Error: {e.stderr}")
      return None

  def kill_all_containers(self):
    try:
      command = f"docker ps -q"
      result = self.server.run_command(command)
      final_command = f"docker kill {result}"
      result = self.server.run_command(final_command)
      return result
    except subprocess.CalledProcessError as e:
      print(f"Error running command: {e}")
      print(f"Output: {e.output}")
      print(f"Error: {e.stderr}")
      return None

  # TODO(sdhande): Add feature to check if image is already loaded
  def load_docker_image(self):
    """Loads a Docker image into the remote machine."""
    if not self.image:
      raise ValueError("image for the docker container is not set")
    try:
      command = f'docker load -i {self.image}'
      output = self.server.run_command(command)
      output = re.search(r"sha256:([a-f0-9]{64})", output).group(1)
      self.image_id = output
      command = f'docker tag {output} trade-ai-image:latest'
      tag_output = self.server.run_command(command)
      return output
    except Exception as e:
      print(f"Error loading Docker image: {e}")
      return None

  def check_if_container_up(self):
    if not self.image:
      raise ValueError("Image for the docker container is not set")
    command = "docker ps"
    result = self.server.run_command(command)
    return len(result.split("\n")) >= 2

  def start_docker_image(self):
    """Starts a Docker image if it's not already running and returns the container ID."""
    if not self.image:
      raise ValueError("Image for the docker container is not set")
    try:
      container_id = self.get_docker_container_id()
      if container_id:
        return f"Container '{container_id}' is already running."
      else:
        if self.check_if_container_up():
          return
        start_command = f'docker run -d {self.image_id}'
        result = self.server.run_command(start_command)
        self.container_id = result.strip()
        return f"Started new container '{self.container_id}' from image '{self.image}'."
    except Exception as e:
      print(f"Error starting Docker container: {e}")
      return None

  def get_docker_container_id(self):
    """Gets the Docker container ID based on the image name."""
    if not self.image:
      raise ValueError("Image for the docker container is not set")
    try:
      command = f'docker ps -q -f ancestor={self.image}'
      result = self.server.run_command(command)
      container_id = result.strip()
      self.container_id = container_id
      return container_id if container_id else None
    except Exception as e:
      print(f"Error retrieving Docker container ID: {e}")
      return None

  def run_docker_command(self, docker_command):
    """Runs a Docker command on the remote machine."""
    try:
      command = f'docker exec -e NUM_CPUS=$(nproc) {self.container_id} {docker_command}'
      return self.server.run_command(command)
    except Exception as e:
      print(f"Error running Docker command: {e}")
      return None

  def get_cpu_usage(self):
    """Fetches CPU usage for all CPUs from the remote machine."""
    try:
      docker_command = "mpstat 1 1 | awk '$12 ~ /[0-9.]+/ { print 100 - $12 }' | tail -n 1"
      return self.run_docker_command(docker_command)
    except Exception as e:
      print(f"Error fetching CPU usage: {e}")
      return None

  def get_memory_usage(self):
    """Fetches memory usage from the remote machine."""
    try:
      docker_command = "free | grep Mem | awk '{print \$3/\$2 * 100.0}"
      return self.run_docker_command(docker_command)
    except Exception as e:
      print(f"Error fetching memory usage: {e}")
      return None
