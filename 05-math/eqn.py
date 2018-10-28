#! python3

"""
This script solves equations given in human readable file
"""
import sys
import os
import re
import argparse
import numpy as np


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
  parser.add_argument("filename", help="File with system of equations to solve")
  parser.add_argument("-v", action='store_true', help="Activation of verbose mode")

  args = parser.parse_args()

  if not os.path.isfile(args.filename):
    eprint("Filename doesn't refer to a valid file")
    exit(2)

  return args.filename, args.v


def parse_equation(line):
  """
  This function parses string of humad-readable equation

  Returns: record with variables and theirs coeficients(dict), constant(int)
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


FILENAME, VERBOSE = parse_args()

#dict with index of all appeared variables
variables = {}
#list of all equations
equations = []
#list of all constants
constants = np.array([])

with open(FILENAME, 'r', encoding='utf-8') as FILE:
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
    constants = np.append(constants, cnst)

#filling matrix with coeficients
matrix = np.zeros((len(equations), len(variables)))
for idx, eqn in enumerate(equations):
  for var, coef in eqn.items():
    matrix[idx][variables[var]] = coef

for idx, e in enumerate(equations):
  verbose_print(e, constants[idx])
verbose_print(*variables.keys())
verbose_print(matrix)

#creating augmented matrix
augm_matrix = np.array(np.column_stack((matrix, constants)))
verbose_print(augm_matrix)

#calculating rank of matrixes
rank_coef = np.linalg.matrix_rank(matrix)
verbose_print("Rank matrix: " + str(rank_coef))
rank_augm = np.linalg.matrix_rank(augm_matrix)
verbose_print("Rank augmented matrix: " + str(rank_augm))

#equation has a solution
if rank_augm <= rank_coef:
  #equation has a sinle solution
  if rank_augm == len(variables):
    solution = np.linalg.solve(matrix, constants)
    verbose_print("Numpy solution: ", solution)
    singles = ["{} = {}".format(var, solution[variables[var]])
               for var in sorted(variables.keys())]
    print("solution: {}".format(", ".join(singles)))
  else:
    print("solution space dimension: " + str(len(variables) - rank_coef))
#equation has no solution
else:
  print("no solution")
