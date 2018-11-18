#! python3

"""
This script analyze signal and prints 3 largest peaks for each sliding windows in musical signature
"""
import sys
import os
import argparse
import numpy as np
import json


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
  parser.add_argument("filename", help="Filename of the CSV data file")
  parser.add_argument("mode", choices=["dates", "deadlines", "exercises"], help="Mode of execution")
  parser.add_argument("-v", action='store_true', help="Activation of verbose mode")

  args = parser.parse_args()

  if not os.path.isfile(args.filename):
    eprint("Filename doesn't refer to a valid file")
    exit(2)

  return args.filename, args.mode, args.v


def load_structure(filename):
  """
  Returns: Loaded dictionary of following structure
            {"01": {"2018-09-26": [0,1,0,2,0],
                    "2018-09-30": [0,2,0,0,1] },
             "02": {}
            }
  """
  struct = {}
  with open(filename, "r") as f:
    csv_data = np.genfromtxt((",".join(ln.split(',')[1:]) for ln in f), delimiter=',', names=True)

  for col in csv_data.dtype.names:
    exc = str(col[-2:])
    date = "{}-{}-{}".format(col[0:4], col[4:6], col[6:8])
    if exc not in struct:
      struct[exc] = {}
    struct[exc][date] = csv_data[col]

  return struct


def fill_stat_element(data):
  stats = {}
  stats["mean"] = np.mean(data)
  stats["median"] = np.median(data)
  stats["passed"] = np.where(data > 0)[0].size
  stats["first"] = np.percentile(data, [25])[0]
  stats["last"] = np.percentile(data, [75])[0]

  return stats


def print_dates(structure):
  joined = {}
  for exc, dates in structure.items():
    for date, data in dates.items():
      if date in joined:
        joined[date] += data
      else:
        joined[date] = data

  output = {}
  for date, data in joined.items():
    output[date] = fill_stat_element(data)

  print(json.dumps(output, indent=2))


def print_deadlines(structure):
  output = {}
  for exc, dates in structure.items():
    for date, data in dates.items():
      dl_key = "{}/{}".format(date, exc)
      output[dl_key] = fill_stat_element(data)

  print(json.dumps(output, indent=2))


def print_exercises(structure):
  joined = {}
  for exc, dates in structure.items():
    for data in dates.values():
      if exc in joined:
        joined[exc] += data
      else:
        joined[exc] = data

  output = {}
  for exc, data in joined.items():
    output[exc] = fill_stat_element(data)

  print(json.dumps(output, indent=2))


if __name__ == "__main__":
  FILENAME, MODE, VERBOSE = parse_args()
  structure = load_structure(FILENAME)
  globals()["print_"+MODE](structure)
