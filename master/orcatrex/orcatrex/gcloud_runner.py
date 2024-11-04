from flask import Flask, jsonify, request
from orcatrex.gcloud_utils import GCloudUtility

app = Flask(__name__)

gcloud_utility: dict[str, GCloudUtility]


@app.route('/accounts', methods=['GET'])
def list_accounts():
  """Endpoint to list authenticated Google Cloud accounts."""
  accounts = GCloudUtility.list_gcloud_accounts()
  return jsonify(accounts)


@app.route('/accounts/activate', methods=['POST'])
def activate_account():
  """Endpoint to activate a Google Cloud account."""
  data = request.get_json()
  if 'account_email' not in data:
    return jsonify({'error': 'Missing account_email parameter'}), 400
  account_email = data['account_email']
  gcloud_utility[account_email] = GCloudUtility(account_email=account_email)
  result = gcloud_utility[account_email].activate_gcloud_account(account_email)
  return jsonify({'result': result})


@app.route('/docker/start', methods=['POST'])
def start_docker():
  """Endpoint to start a Docker container."""
  data = request.get_json()
  if 'image_name' not in data:
    return jsonify({'error': 'Missing image_name parameter'}), 400
  account_email = data['account_email']
  image_name = data['image_name']
  gcloud_utility[account_email].set_image(image=image_name)
  result = gcloud_utility[account_email].start_docker_image()
  return jsonify({'result': result})


@app.route('/docker/load_image', methods=['POST'])
def load_docker_image():
  """Endpoint to start a Docker container."""
  data = request.get_json()
  if 'image_name' not in data:
    return jsonify({'error': 'Missing image_name parameter'}), 400
  account_email = data['account_email']
  result = gcloud_utility[account_email].load_docker_image()
  return jsonify({'result': result})


@app.route('/docker/run', methods=['POST'])
def run_docker_command():
  """Endpoint to run a Docker command."""
  data = request.get_json()
  if 'container_id' not in data or 'docker_command' not in data:
    return jsonify({'error': 'Missing container_id or docker_command parameter'}), 400
  account_email = data['account_email']
  docker_command = data['docker_command']
  result = gcloud_utility[account_email].run_docker_command(docker_command)
  return jsonify({'result': result})


@app.route('/docker/get_container_id', methods=['POST'])
def get_container_id():
  """Endpoint to get the container ID."""
  data = request.get_json()
  if 'image_name' not in data:
    return jsonify({'error': 'Missing image_name parameter'}), 400
  account_email = data['account_email']
  container_id = gcloud_utility[account_email].get_docker_container_id()
  return jsonify({'container_id': container_id})


@app.route('/resources/cpu', methods=['GET'])
def get_cpu_usage():
  """Endpoint to fetch CPU usage."""
  data = request.get_json()
  account_email = data['account_email']
  cpu_usage = gcloud_utility[account_email].get_cpu_usage()
  return jsonify({'cpu_usage': cpu_usage})


@app.route('/resources/memory', methods=['GET'])
def get_memory_usage():
  """Endpoint to fetch memory usage."""
  data = request.get_json()
  if 'container_id' not in data:
    return jsonify({'error': 'Missing container_id or docker_command parameter'}), 400
  account_email = data['account_email']
  memory_usage = gcloud_utility[account_email].get_memory_usage()
  return jsonify({'memory_usage': memory_usage})


if __name__ == '__main__':
  app.run(host='0.0.0.0', port=4001)
