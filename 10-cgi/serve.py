#! python3

"""
This script creates http server running on localhost on given port that forwards requests to upstream
"""
import sys
import argparse
import os
from http.server import HTTPServer, BaseHTTPRequestHandler, CGIHTTPRequestHandler
from socketserver import ThreadingMixIn
import time


def eprint(*args, **kwargs):
  "This function prints message to error output"
  print(*args, file=sys.stderr, **kwargs)


def verbose_print(*args, **kwargs):
  "This function prints message in verbose mode"
  if VERBOSE:
    print(*args, file=sys.stderr, **kwargs)


def parse_args():
  "This function parses command-line arguments and does basic checks"
  parser = argparse.ArgumentParser()
  parser.add_argument("port", type=int, help="Server port")
  parser.add_argument("root_dir", help="Root dir for serving content")
  parser.add_argument("-v", action='store_true', help="Activation of verbose mode")

  args = parser.parse_args()

  return args.port, args.root_dir, args.v


class CGIHandler(CGIHTTPRequestHandler):
  _root_dir = None

  def do_GET(self):
    file_path = os.path.normpath(self._root_dir + self.path)
    verbose_print("normalizing path <{}> to <{}>".format(self._root_dir + self.path, file_path))

    if(os.path.isfile(file_path)):
      verbose_print("file <{}> exists".format(file_path))
      if file_path.endswith('.cgi'):
        verbose_print("file <{}> is CGI script".format(file_path))
        self._execute_cgi(file_path)
      else:
        self._send_file(file_path)

    elif(os.path.isdir(file_path)):
      verbose_print("path <{}> is dir".format(file_path))
    else:
      verbose_print("path <{}> does not exist".format(file_path))
      self.send_error(404, explain="path <{}> does not exist".format(file_path))



  def do_POST(self):
    try:
      length = int(self.headers['Content-Length'])
      json_content = json.loads(self.rfile.read(length).decode('utf-8'))

      req_type = json_content.get('type', 'GET')
      req_timeout = int(json_content.get('timeout', 1))
      req_url = json_content.get('url')
      req_headers = json_content.get('headers', {})
      req_content = bytes(json_content.get('content', ''), 'utf-8')

      if(req_url is None):
        raise ValueError
      if(req_type == 'POST' and 'content' not in json_content.keys()):
        raise ValueError
      if(req_type not in ('GET', 'POST')):
        raise ValueError

      response = https_request(req_url, req_type, req_headers, req_content, timeout=req_timeout)

    except ValueError:
      response = {'code': 'invalid json'}

    self._reply(response)


  def _send_file(self, file_path):
    with open(file_path, 'rb') as file:
      self.send_response(200)
      self.send_header("Content-Type", 'application/octet-stream')
      self.send_header("Content-Disposition", 'attachment; filename="{}"'.format(os.path.basename(file_path)))
      self.send_header("Content-Length", os.path.getsize(file_path))
      self.end_headers()
      self.wfile.write(file.read())


  def _execute_cgi(self, file_path):
    relpath = os.path.relpath(file_path)
    self.cgi_info = os.path.dirname(relpath), os.path.basename(relpath)
    self.run_cgi()


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
  """Handle requests in a separate thread."""


def run_server(port, root_dir):
  CGIHandler._root_dir = os.path.abspath(root_dir)
  server = ThreadedHTTPServer(('localhost', port), CGIHandler)
  server.serve_forever()


if __name__ == "__main__":
  PORT, ROOT_DIR, VERBOSE = parse_args()
  run_server(PORT, ROOT_DIR)
