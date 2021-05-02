from flask import Flask, request
from concurrent.futures import ThreadPoolExecutor
from app.quantum_gen import generate_seeds
from random import shuffle


app = Flask(__name__)
ex = ThreadPoolExecutor(max_workers=1)
process = None
seeds = [18, 750, 140, 38, 622, 1125, 48, 122, 941, 308, 1197, 33, 75, 772, 989, 893, 558, 623, 197, 835]


def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

def seeds_computed(*args):
	global process, seeds
	seeds = process.result()
	process = None


@app.route("/ping", methods=["GET"])
def ping():
	return {"msg": "System online"}

@app.route("/", methods=["GET"])
def index_ping():
	return {"msg": "System online"}

@app.route("/get-seeds", methods=["GET"])
def get_seeds():
	global seeds, process
	shuffle(seeds)
	if process == None:
		process = ex.submit(generate_seeds)
		process.add_done_callback(seeds_computed)
	return dict(zip(range(len(seeds)), seeds)), 200

@app.route("/get-seeds/<int:count>", methods=["GET"])
def get_count_seeds(count):
	global seeds, process
	shuffle(seeds)
	if process == None:
		process = ex.submit(generate_seeds)
		process.add_done_callback(seeds_computed)
	return dict(zip(range(len(seeds)), seeds)), 200


# quantum_job.queue_info().estimated_complete_time.strftime("%H:%M:%S")