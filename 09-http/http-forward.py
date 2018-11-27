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
  for i in ('http://', 'https://'):
    if(url.startswith(i)):
      url = url.replace(i, '')

  url_parts = url.split('/', 1)
  if(len(url_parts) == 1):
    url_parts.append('') 

  return url_parts


def https_request(url, type, headers, body, timeout=1):
  response = {}
  domain, path = parse_url(url)

  try:
    conn = http.client.HTTPSConnection(domain, timeout=timeout, context=ssl._create_unverified_context())

    if(type == 'POST'):
      conn.request(type, '/'+path, body, headers=headers)
    elif(type == 'GET'):
      conn.request(type, '/'+path, headers=headers)
    else:
      raise ValueError

    resp = conn.getresponse()
    headers = resp.getheaders()
    data = resp.read().decode('utf-8')

    #TODO
    #response['headers'] = 
    response['code'] = resp.status
    try:
      response['json'] = json.loads(data.replace("\n", ""))
    except json.decoder.JSONDecodeError:
      response['content'] = data

  except:
    response['code'] = 'timeout'
  finally:
    conn.close()

  return response


class ForwardHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
  _upstream = None

  def do_GET(self):
    headers = {'Content-type': 'application/json'}
    response = https_request(self._upstream, "GET", headers, None)

    json_response = bytes(json.dumps(response), 'utf-8')
    self.send_response(200)
    self.send_header('Content-Type', 'application/json')
    self.end_headers()
    self.wfile.write(json_response)


  def do_POST(self):
    pass


def run_server(upstream, port):
  ForwardHTTPRequestHandler._upstream = upstream
  fw_server = http.server.HTTPServer(('localhost', port), ForwardHTTPRequestHandler)
  fw_server.serve_forever()


if __name__ == "__main__":
  PORT, UPSTREAM, VERBOSE = parse_args()
  run_server(UPSTREAM, PORT)
