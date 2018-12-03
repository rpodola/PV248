#! python3

"""
This script creates http server running on localhost on given port that forwards requests to upstream
"""
import sys
import argparse
import json
import http.server
import http.client
import ssl
import socket


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
  parser.add_argument("port", type=int, help="Port of upstream server")
  parser.add_argument("upstream", help="Upstream server address")
  parser.add_argument("-v", action='store_true', help="Activation of verbose mode")

  args = parser.parse_args()

  return args.port, args.upstream, args.v


def parse_url(url):
  http = True
  for i in ('http://', 'https://'):
    if(url.startswith(i)):
      if(i == 'https://'):
        http = False
      url = url.replace(i, '')

  url_parts = url.split('/', 1)
  if(len(url_parts) == 1):
    url_parts.append('')

  url_parts.append(http)

  return url_parts


def https_request(url, type, headers, body, timeout=1):
  response = {}
  domain, path, secure = parse_url(url)

  verbose_print("type: " + type)
  verbose_print("url: " + url)
  verbose_print("headers: " + json.dumps(headers))
  verbose_print("body: " + str(body))
  try:
    if(secure):
      conn = http.client.HTTPConnection(domain, timeout=timeout)
    else:
      conn = http.client.HTTPSConnection(domain, timeout=timeout, context=ssl._create_unverified_context())

    if(type == 'POST'):
      conn.request(type, '/'+path, body=body, headers=headers)
    else:
      conn.request(type, '/'+path, headers=headers)

    resp = conn.getresponse()
    data = resp.read().decode('utf-8')

    response['headers'] = dict(resp.getheaders())
    response['code'] = resp.status
    try:
      response['json'] = json.loads(data.replace("\n", ""))
    except json.decoder.JSONDecodeError:
      response['content'] = data

  except socket.timeout:
    response['code'] = 'timeout'
  except Exception as e:
    eprint(e)
  finally:
    conn.close()

  return response


class ForwardHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
  _upstream = None

  def do_GET(self):
    headers = {'Content-type': 'text/plain; charset=utf-8'}
    response = https_request(self._upstream, "GET", headers, None)

    self._reply(response)


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


  def _reply(self, response):
    json_response = bytes(json.dumps(response), 'utf-8')

    self.send_response(200)
    self.send_header('Content-Type', 'application/json')
    self.end_headers()
    self.wfile.write(json_response)


def run_server(upstream, port):
  ForwardHTTPRequestHandler._upstream = upstream
  fw_server = http.server.HTTPServer(('localhost', port), ForwardHTTPRequestHandler)
  fw_server.serve_forever()


if __name__ == "__main__":
  PORT, UPSTREAM, VERBOSE = parse_args()
  run_server(UPSTREAM, PORT)
