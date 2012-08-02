import json
import functools
import redis
from flask import Flask, Response, request
from tweetsvm.manage import Manager, CommandError

controller = Manager(redis.StrictRedis(host='localhost', port=6379, db=0))
app = Flask(__name__)
USER = "quinnchr"

# Response decorator


def REST_response(func):
	@functools.wraps(func)
	def response(*args, **kwargs):
		try:
			result = func(*args, **kwargs)
			if result == True:
				return Response(status=204)  # succesful but no response (e.g. DELETE)
			else:
				return json.dumps(result)
		except CommandError as error:
			return json.dumps({'error': error.value}), 404
	return response


def prepare_resource(resource):
	resource_url = "http://" + request.host + "/streams"
	if 'stream' in resource:
		obj = 'stream'
		resource_url += "/" + resource['stream']
	if 'source' in resource:
		obj = 'source'
		resource_url += "/" + resource['source']
	return {'name': resource[obj], 'url': resource_url}

# Controllers


@app.route("/streams/", methods=['GET', 'POST'])
@REST_response
def stream_index():
	if request.method == 'POST':
		stream = request.form['stream']
		return add_stream(stream)
	if request.method == 'GET':
		return get_streams()


@app.route("/streams/<stream>/", methods=['GET', 'POST', 'DELETE'])
@REST_response
def streams(stream=""):
	if request.method == "GET":
		return get_stream(stream)
	if request.method == "DELETE":
		return delete_stream(stream)
	if request.method == "POST":
		return add_source(stream, request.form['source'])


@app.route("/streams/<stream>/<source>/", methods=['GET', 'DELETE'])
@REST_response
def sources(stream="", source=""):
	if request.method == "GET":
		return get_source(stream, source)
	if request.method == "DELETE":
		return delete_source(stream, source)

# Stream Methods


def get_streams():
	streams = []
	for stream in controller.get_streams(user=USER):
		streams.append(prepare_resource({'stream': stream}))
	return streams


def add_stream(stream):
	controller.add_stream(user=USER, stream=stream)
	return prepare_resource({'stream': stream})


def get_stream(stream):
	sources = []
	for source in controller.get_sources(user=USER, stream=stream):
		sources.append(prepare_resource({'source': source, 'stream': stream}))
	return sources


def delete_stream(stream):
	controller.remove_stream(user=USER, stream=stream)
	return True

# Source Methods


def add_source(stream, source):
	controller.add_source(user=USER, stream=stream, source=source)
	return prepare_resource({'source': source, 'stream': stream})


def delete_source(stream, source):
	controller.remove_source(user=USER, stream=stream, source=source)
	return True


def get_source(stream, source):
	return True

if __name__ == "__main__":
	app.run(debug=True)
