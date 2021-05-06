from flask import Flask, request, jsonify
from concurrent.futures import ThreadPoolExecutor
from app.quantum_gen import generate_seeds
from random import shuffle


app = Flask(__name__)
ex = ThreadPoolExecutor(max_workers=1)
process = None
seeds = [
	6, 
	15, 
	5, 
	261, 
	2, 
	1, 
	8, 
	250, 
	3, 
	4, 
	41, 
	10, 
	44, 
	3, 
	4, 
	8, 
	20, 
	26, 
	13, 
	7, 
	2, 
	16, 
	63, 
	10, 
	63, 
	18, 
	45, 
	37, 
	31, 
	5, 
	2, 
	1,
]


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
	return jsonify(seeds)
	# return dict(zip(range(len(seeds)), seeds)), 200

# @app.route("/get-seeds/<int:count>", methods=["GET"])
# def get_count_seeds(count):
# 	global seeds, process
# 	shuffle(seeds)
# 	if process == None:
# 		process = ex.submit(generate_seeds)
# 		process.add_done_callback(seeds_computed)
# 	return dict(zip(range(len(seeds)), seeds)), 200


# quantum_job.queue_info().estimated_complete_time.strftime("%H:%M:%S")