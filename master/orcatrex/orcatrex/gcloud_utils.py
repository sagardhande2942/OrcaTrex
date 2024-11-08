from __future__ import annotations

import re
import subprocess


class GCloudUtility:

  def __init__(self, account_email):
    self.account_email = account_email

  @staticmethod
  def run_command(command):
    """Runs a gcloud command and returns the output."""
    try:
      final_command = f'gcloud cloud-shell ssh --authorize-session --command="{command}"'
      result = subprocess.run(final_command, check=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
      return result.stdout.strip()
    except subprocess.CalledProcessError as e:
      print(f"Error running command: {e}")
      print(f"Output: {e.output}")
      print(f"Error: {e.stderr}")
      return None

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
    output = self.run_command(command)
    return output

  def scp(self, src, dest):
    try:
      final_command = f'gcloud cloud-shell scp localhost:{src} cloudshell:{dest}'
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
      final_command = f"docker kill $(docker ps -q)"
      result = subprocess.run(final_command, check=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
      return result.stdout.strip()
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
        start_command = f'docker run -d {self.image}'
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
