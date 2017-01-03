# -*- coding: utf-8 -*-

import threading
from wsgiref.simple_server import make_server, WSGIRequestHandler

from bottle import Bottle, ServerAdapter, response, redirect, abort
from bottle import request #get, request, run, route # or route

import sys, xbmc
from log import debug, print_tb

from parse import parse
from remotesettings import Settings
s = Settings(None)

import bottle
bottle.BaseRequest.MEMFILE_MAX = 1024 * 1024

class HTTP:
	engines = []
	
	def test(self):
		debug('test')
		return "<p>Test - Ok</p>"
		
	def engine_by(self, pid):
		return next((engn for engn in self.engines if engn.pid() == pid), None)
		
	def engine(self):
		try:
			pid = int(request.params.get('pid'))
			return self.engine_by(pid)
		except:
			return None
		
	def do_popen(self):
		try:
			debug('do_popen')
			
			args_str    = request.forms.get('args')
			tdata       = request.forms.get('torrent_data')
			dict_str    = request.forms.get("dict")

			argv = ['args=' + args_str,
					'torrent_data=' + tdata,
					'dict=' + dict_str]

			engn = parse(argv, s)
			self.engines.append(engn) 

			return str(engn.pid()) + '.' + str(engn.bind_port)
		except BaseException as e:
			print_tb(e)
			return "None"
			
	def close(self):
		engn = self.engine()
		self.engines.remove(engn)
		
	def poll(self):
		try:
			return str(self.engine().process.poll())
		except BaseException as e:
			print_tb(e)
			return "None"
			
	def wait(self):
		try:
			return str(self.engine().process.wait())
		except BaseException as e:
			print_tb(e)
			return "0"

	def terminate(self):
		try:
			return self.engine().process.terminate()
		except BaseException as e:
			print_tb(e)
			return "Fail"

	def kill(self):
		try:
			return self.engine().process.kill()
		except BaseException as e:
			print_tb(e)
			return "Fail"
			
	def do_can_bind(self):
		try:
			from ..util import can_bind

			host = ''
			port = request.forms.get('port')
			debug('can_bind: ' + port)
			return str(can_bind(host, int(port)))
		except BaseException as e:
			print_tb(e)
			return "False"
		
	def do_find_free_port(self):
		try:
			from ..util import find_free_port
			
			host = ''
			debug('find_free_port: ')
			return str(find_free_port(host))
		except BaseException as e:
			print_tb(e)
			return "0"
		
class Server:
	def __init__(self):
		self.server = None
		self.http = HTTP()
		
		self.run()

	def loop(self):
		pass
	
	def run(self):
		debug('Run')
		threading.Thread(target=self._run).start()

	def _run(self):
		debug('Running in thread')
		app = Bottle()
		app.route('/test', callback=self.http.test)
		
		app.route('/popen', method='POST', callback=self.http.do_popen)
		app.route('/can_bind', method='POST', callback=self.http.do_can_bind)
		app.route('/find_free_port', method='POST', callback=self.http.do_find_free_port)
		
		app.route('/poll', callback=self.http.poll)
		app.route('/wait', callback=self.http.wait)
		app.route('/terminate', callback=self.http.terminate)
		app.route('/kill', callback=self.http.kill)

		app.route('/close', callback=self.http.close)

		#debug('host: ' + s.remote_host)
		#debug('port: ' + s.remote_port)
		self.server = BottleServer(host=s.remote_host, port=s.remote_port)
		try:
			app.run(server=self.server)
		except Exception, e:
			print_tb(e)
		debug('Server stopped')
		self.server = None

	def stop(self):
		if self.server:
			self.server.stop()
			while self.server:
				xbmc.sleep(300)


# BOTTLE WEB SERVER

class QuietHandler(WSGIRequestHandler):
	def log_request(*args, **kwargs):
		pass


class BottleServer(ServerAdapter):
	server = None

	def run(self, handler):
		if self.quiet:
			self.options['handler_class'] = QuietHandler
		self.server = make_server(self.host, self.port, handler, **self.options)
		self.server.serve_forever()

	def stop(self):
		self.server.shutdown()
