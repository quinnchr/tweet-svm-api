from flask import request
from functools import wraps
from tweetsvm.manage import CommandError
import base64
import hashlib
import hmac
import redis
import urllib


def auth(func):
	@wraps(func)
	def decorator(*args, **kwargs):
		# error out if we don't have a key & digest
		if not request.headers.get('Authorization'):
			raise CommandError('Request not authorized.')
		key, request_digest = request.headers.get('Authorization').split(':')
		# grab private key and compare digests
		# TODO: db lookup goes here
		db = redis.StrictRedis(host='localhost', port=6379, db=0)
		private_key = db.hget('server:credentials', key)
		if not private_key:
			raise CommandError('Request not authorized.')
		kwargs['user'] = db.hget('server:uuids', key)
		kwargs['public_key'] = key
		server_digest = digest(request, private_key)
		print server_digest
		if server_digest != request_digest:
			raise CommandError('Request not authorized.')
		return func(*args, **kwargs)
	return decorator


def access(level):
	def wrapper(func):
		@wraps(func)
		def decorator(*args, **kwargs):
			db = redis.StrictRedis(host='localhost', port=6379, db=0)
			user = kwargs['user']
			if not db.sismember('server:access:' + level, user):
				raise CommandError('Unauthorized access.')
			return func(*args, **kwargs)
		return decorator
	return wrapper


def digest(request, private_key):
	request_args = []
	request_args += [k + '=' + v for k, v in request.form.iteritems() if k not in ('key', 'digest')]
	request_args.append(request.path)
	message = '|'.join(request_args)
	return base64.b64encode(hmac.new(private_key, message, hashlib.sha256).digest())
