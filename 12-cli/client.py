#! python3

"""
This script represents game client for game Tic-Tac-Toe
"""
import sys
import argparse
import json
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
  parser.add_argument("host", help="Game server address")
  parser.add_argument("port", type=int, help="Game server port")
  parser.add_argument("-v", action='store_true', help="Activation of verbose mode")

  args = parser.parse_args()

  return args.host, args.port, args.v


def run_client(host, port):
  pass

if __name__ == "__main__":
  HOST, PORT, VERBOSE = parse_args()
  run_client(HOST, PORT)
