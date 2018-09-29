#! python3
import sys
import argparse
from os import path
from scorelib import load

def eprint(*args, **kwargs):
  "This function prints message to error output"
  print(*args, file=sys.stderr, **kwargs)


def parse_args():
  "This function parses command-line arguments and does basic checks"
  parser = argparse.ArgumentParser()
  parser.add_argument("filename", help="source file")

  args = parser.parse_args()

  if not path.isfile(args.filename):
    eprint("Filename doesn't refer to a valid file")
    exit(2)

  return args.filename


#script body
filename = parse_args()
print_list = load(filename)
for p in print_list:
	p.format()
	print("\n")