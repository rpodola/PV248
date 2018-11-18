#! python3

"""
This script analyze signal and prints 3 largest peaks for each sliding windows in musical signature
"""
import sys
import os
import argparse
import numpy as np
import json
import pandas as pd
from datetime import datetime as dt


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
  parser.add_argument("id", help="ID of student or average")
  parser.add_argument("-v", action='store_true', help="Activation of verbose mode")

  args = parser.parse_args()

  if not os.path.isfile(args.filename):
    eprint("Filename doesn't refer to a valid file")
    exit(2)

  if args.id == "average":
    args.id = None
  else:
    try:
      args.id = int(args.id)
    except ValueError:
      eprint("Invalid type of ID")
      exit(2)

  return args.filename, args.id, args.v


def load_structure(filename, id):
  """
  Returns: Loaded dictionary of following structure
            {"01": {"2018-09-26": 0,
                    "2018-09-30": 1.5 },
             "02": {}
            }
  """
  struct = {}
  df = pd.read_csv(filename)

  if id is not None:
    df = df.loc[df['student'] == id]
    keys = df.columns.values.tolist()
  else:
    df = df.mean(axis=0)
    keys = df.keys()

  if not df.empty:
    for col in keys:
      if col != "student":
        exc = str(col[-2:])
        date = "{}-{}-{}".format(col[0:4], col[5:7], col[8:10])
        if exc not in struct:
          struct[exc] = {}
        struct[exc][date] = df[col].item()

  return struct


def get_exc_stats(structure):
  exercises = {}
  for exc, dates in structure.items():
    for data in dates.values():
      if exc in exercises:
        exercises[exc] += data
      else:
        exercises[exc] = data

  data = np.array(list(exercises.values()))

  stats = {}
  stats["mean"] = np.mean(data)
  stats["median"] = np.median(data)
  stats["passed"] = np.where(data > 0)[0].size
  stats["total"] = np.sum(data)

  return stats


def get_date_stats(structure):
  stats = {}
  START_DATE = dt.strptime("2018-09-17",'%Y-%m-%d').date().toordinal()

  joined_dates = {}
  for exc, dates in structure.items():
    for date, data in dates.items():
      ordinal_date = dt.strptime(date, '%Y-%m-%d').date().toordinal() - START_DATE
      if ordinal_date in joined_dates:
        joined_dates[ordinal_date] += data
      else:
        joined_dates[ordinal_date] = data

  dates_array = np.array(sorted(joined_dates.keys()))
  sorted_points = [joined_dates[key] for key in dates_array]
  for idx in range(1, len(sorted_points)):
    sorted_points[idx] += sorted_points[idx-1]

  dates_array = dates_array[:, np.newaxis]
  slope = np.linalg.lstsq(dates_array, sorted_points, rcond=None)[0].item()
  stats["regression slope"] = slope

  date_20 = dt.fromordinal(START_DATE + int(20 / slope)).date()
  date_16 = dt.fromordinal(START_DATE + int(16 / slope)).date()
  stats["date 20"] = str(date_20)
  stats["date 16"] = str(date_16)

  return stats


def print_stats(structure):
  if not structure:
    print(structure)
    return

  output = {**get_exc_stats(structure), **get_date_stats(structure)}

  print(json.dumps(output, indent=2))


if __name__ == "__main__":
  FILENAME, ID, VERBOSE = parse_args()
  structure = load_structure(FILENAME, ID)
  print_stats(structure)
