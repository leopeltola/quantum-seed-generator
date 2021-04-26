from flask import Flask, request
from concurrent.futures import ThreadPoolExecutor
from app.quantum_gen import generate_seeds
from app.quantum_gen import job as quantum_job

app = Flask(__name__)
ex = ThreadPoolExecutor(max_workers=1)
process = None

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()


@app.route("/start", methods=["GET"])
def start():
	global process
	global ex
	if process != None:
		return {"msg": "calculation in process"}, 403
	process = ex.submit(generate_seeds)
	return {"msg": "calculation started"}, 202

@app.route("/status", methods=["GET"])
def status():
	global process
	if process == None:
		return {"msg": "no calculation in process"}, 403
	if not process.done():
		return {
			"msg": "processing",
			# "estimated_complete_time": quantum_job.queue_info().estimated_complete_time.strftime("%H:%M:%S"),
		}, 202
	return {"msg": "calculation complete"}, 201

@app.route("/result", methods=["GET"])
def result():
	global process
	if process == None:
		return {"msg": "no calculation in process"}, 403
	if process.done():
		seeds = process.result()
		process = None
		return dict(zip(range(len(seeds)), seeds)), 200
	return {"msg": "processing"}, 202

@app.route('/shutdown', methods=["GET"])
def shutdown():
    shutdown_server()
    return "server shutting down", 200
