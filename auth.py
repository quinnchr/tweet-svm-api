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
		if not ('digest' in request.form and 'key' in request.form):
			raise CommandError('Request not authorized.')
		request_digest = request.form['digest']
		key = request.form['key']
		# grab private key and compare digests
		# TODO: db lookup goes here
		db = redis.StrictRedis(host='localhost', port=6379, db=0)
		private_key = db.hget('server:credentials', key)
		if not private_key:
			raise CommandError('Request not authorized.')
		kwargs['user'] = db.hget('server:uuids', key)
		server_digest = digest(request, private_key)
		print private_key
		print urllib.quote(server_digest)
		print kwargs
		if server_digest != request_digest:
			raise CommandError('Request not authorized.')
		return func(*args, **kwargs)
	return decorator


def digest(request, private_key):
	request_args = []
	request_args += [k + '=' + v for k, v in request.form.iteritems() if k not in ('key', 'digest')]
	request_args.append(request.path)
	message = '|'.join(request_args)
	return base64.b64encode(hmac.new(private_key, message, hashlib.sha256).digest())
