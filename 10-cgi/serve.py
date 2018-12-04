#! python3

"""
This script creates http server running on localhost on given port that forwards requests to upstream
"""
import sys
import argparse
import os
from http.server import HTTPServer, CGIHTTPRequestHandler
from socketserver import ThreadingMixIn
import http.client

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
  _cgi_args = None

  def do_GET(self):
    self._serve_request(self._get_full_path())


  def do_POST(self):
    self._serve_request(self._get_full_path())


  def _get_full_path(self):
    self.path, _, self._cgi_args = self.path.partition('?')
    verbose_print(self.path + ":" + self._cgi_args)
    return os.path.normpath(self._root_dir + self.path)


  def _serve_request(self, file_path):
    if(os.path.isfile(file_path)):
      verbose_print("file <{}> exists".format(file_path))
      if file_path.endswith('.cgi'):
        verbose_print("file <{}> is CGI script".format(file_path))
        self._execute_cgi(file_path)
      else:
        self._send_file(file_path)

    elif(os.path.isdir(file_path)):
      verbose_print("path <{}> is dir".format(file_path))
      self.send_error(http.client.FORBIDDEN, explain='URL points to directory'.format(file_path))
    else:
      verbose_print("path <{}> does not exist".format(file_path))
      self.send_error(http.client.NOT_FOUND, explain='path "{}" does not exist'.format(file_path))


  def _send_file(self, file_path):
    with open(file_path, 'rb') as file:
      self.send_response(http.client.OK)
      self.send_header("Content-Type", 'application/octet-stream')
      self.send_header("Content-Disposition", 'attachment; filename="{}"'.format(os.path.basename(file_path)))
      self.send_header("Content-Length", os.path.getsize(file_path))
      self.end_headers()
      while True:
        data = file.read(1024)
        if not data:
          break
        self.wfile.write(data)


  def _execute_cgi(self, file_path):
    relpath = os.path.relpath(file_path)
    cgi_file = os.path.basename(relpath)
    if(self._cgi_args):
      cgi_file += '?' + self._cgi_args
    self.cgi_info = os.path.dirname(relpath), cgi_file 
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
