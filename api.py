import json
import redis
from flask import Flask
from flask import request
from tweetsvm.manage import Manager

controller = Manager(redis.StrictRedis(host='localhost', port=6379, db=0))
app = Flask(__name__)


@app.route("/streams", methods=['GET', 'POST'])
def get_streams():
	if request.method == 'POST':
		stream = request.form['stream']
		controller.add_stream(user="quinnchr", stream=stream)
		return True
	if request.method == 'GET':
		streams = []
		for stream in controller.get_streams(user='quinnchr'):
			streams.append({'stream': stream, 'url': '/streams/' + stream})
		return json.dumps(streams)


@app.route("/streams/<stream>", methods=['GET', 'POST', 'DELETE'])
def streams(stream=""):
	if request.method == "GET":
		return get_stream(stream)
	if request.method == "DELETE":
		return delete_stream(stream)


@app.route("/streams/<stream>/<source>", methods=['GET', 'POST', 'DELETE'])
def sources(stream="", source=""):
	if request.method == "GET":
		return get_source(stream, source)
	if request.method == "POST":
		return add_source(stream, source)
	if request.method == "DELETE":
		return delete_source(stream, source)


# Stream Methods


def get_stream(stream):
	sources = []
	for source in controller.get_sources(user='quinnchr', stream=stream):
		sources.append({'source': source, 'url': '/streams/' + stream + '/' + source})
	return json.dumps(sources)


def delete_stream(stream):
	controller.remove_stream(user="quinnchr", stream=stream)
	return True

# Source Methods


def add_source(stream, source):
	controller.add_source(user="quinnchr", stream=stream, source=source)
	return True


def delete_source(stream, source):
	controller.remove_source(user="quinnchr", stream=stream, source=source)
	return True


def get_source(stream, source):
	return True

if __name__ == "__main__":
	app.run(debug=True)
