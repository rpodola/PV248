#! python3

"""
This script solves equations given in human readable file
"""
import sys
import argparse
import numpy as np
import os
import re


def eprint(*args, **kwargs):
  "This function prints message to error output"
  print(*args, file=sys.stderr, **kwargs)


def parse_args():
  "This function parses command-line arguments and does basic checks"
  parser = argparse.ArgumentParser()
  parser.add_argument("filename", help="File with equations to solve")

  args = parser.parse_args()

  if not os.path.isfile(args.filename):
    eprint("Filename doesn't refer to a valid file")
    exit(2)

  return args.filename


def parse_equation(line):
  """
  output is dict, const: {"x": 0, "a": -5}
  """
  eqn = {}

  rgx_left = re.compile(r"(?P<sign>[+-])?\s*(?P<coef>\d*)(?P<var>[a-z]+)\s*")

  left = [f.groupdict() for f in rgx_left.finditer(line)]
  right = re.findall(r"[=]\s*(\d+)", line)

  for term in left:
    term["coef"] = int(term["coef"]) if term["coef"] != '' else 1
    if term["sign"] == '-':
      term["coef"] = -term["coef"]
    eqn[term["var"]] = term["coef"]

  if eqn and len(right) == 1:
    return eqn, int(right[0])
  else:
    raise ValueError("Equation not well formated")


#dict with index of all appeared variables
variables = {}

filename = parse_args()
equations = []
constants = []

with open(filename, 'r', encoding='utf-8') as FILE:
  for line in FILE:
    try:
      eqn, cnst = parse_equation(line.strip())
      for e in eqn.keys():
        if e not in variables:
          variables[e] = len(variables)
    except ValueError as ve:
      eprint("Given equation <{}> failed with error: {}".format(line.strip(), ve))
      continue

    equations.append(eqn)
    constants.append(cnst)

for idx, e in enumerate(equations): 
  print(e, constants[idx])

print(variables)