import json
import functools
import redis
from flask import Flask, Response, request
from tweetsvm.manage import Manager, CommandError
from auth import auth, access

controller = Manager(redis.StrictRedis(host='localhost', port=6379, db=0))
app = Flask(__name__)

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
@auth
def stream_index(**kwargs):
	if request.method == 'POST':
		stream = request.form['stream']
		return add_stream(kwargs['user'], stream)
	if request.method == 'GET':
		return get_streams(kwargs['user'])


@app.route("/streams/<stream>/", methods=['GET', 'POST', 'DELETE'])
@REST_response
@auth
def streams(stream="", **kwargs):
	if request.method == "GET":
		return get_stream(kwargs['user'], stream)
	if request.method == "DELETE":
		return delete_stream(kwargs['user'], stream)
	if request.method == "POST":
		return add_source(kwargs['user'], stream, request.form['source'])


@app.route("/streams/<stream>/<source>/", methods=['GET', 'DELETE'])
@REST_response
@auth
def sources(stream="", source="", **kwargs):
	if request.method == "GET":
		return get_source(kwargs['user'], stream, source)
	if request.method == "DELETE":
		return delete_source(kwargs['user'], stream, source)


@app.route("/users/", methods=['POST'])
@REST_response
@auth
@access("admin")
def user_index(user="", **kwargs):
	return add_user()


@app.route("/users/<uuid>", methods=['DELETE'])
@REST_response
@auth
@access("admin")
def users(uuid="", **kwargs):
	return delete_user(uuid)

# Stream Methods


def get_streams(user):
	streams = []
	for stream in controller.get_streams(user=user):
		streams.append(prepare_resource({'stream': stream}))
	return streams


def add_stream(user, stream):
	controller.add_stream(user=user, stream=stream)
	return prepare_resource({'stream': stream})


def get_stream(user, stream):
	sources = []
	for source in controller.get_sources(user=user, stream=stream):
		sources.append(prepare_resource({'source': source, 'stream': stream}))
	return sources


def delete_stream(user, stream):
	controller.remove_stream(user=user, stream=stream)
	return True

# Source Methods


def add_source(user, stream, source):
	controller.add_source(user=user, stream=stream, source=source)
	return prepare_resource({'source': source, 'stream': stream})


def delete_source(user, stream, source):
	controller.remove_source(user=user, stream=stream, source=source)
	return True


def get_source(stream, source):
	return True

# User Methods


def add_user():
	user = controller.add_user()
	print user
	return {'uuid': user[0], 'public_key': user[1], 'private_key': user[2]}


def delete_user(user):
	controller.remove_user(user=user)
	return True

if __name__ == "__main__":
	app.run(debug=True)
