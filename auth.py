from flask import request
from functools import wraps
from tweetsvm.Manage import CommandError
import base64
import hashlib
import hmac


def auth(func):
	@wraps(func)
	def decorator(*args, **kwargs):
		digest = request.form['digest']
		key = request.form['key']
		# error out if we don't have a key & digest
		if not (digest and key):
			raise CommandError('Request not authorized.')
		# grab private key and compare digests
		# TODO: db lookup goes here
		private_key = 'sdfklgjnLKJB^&gkJHB^&^'
		message = '|'.join(request.args + request.form)
		server_digest = base64.base64(hmac.new(private_key, message, hashlib.sha256).digest())
		if server_digest != digest:
			raise CommandError('Request not authorized.')
		return func(*args, **kwargs)
	return decorator
