#! python3.7
import sys
import re
from pathlib import Path
import collections
import argparse
from dateutil.parser import parse as dateParse


PARSER_FUNC_PREFIX = 'parse_line_'
PRINTER_FUNC_PREFIX = 'print_stats_'
COMPOSER_MODE = 'composer'
CENTURY_MODE = 'century'


def eprint(*args, **kwargs):
  "This function prints message to error output"
  print(*args, file=sys.stderr, **kwargs)


def parse_args(*args,**kwargs):
  "This function parses command-line arguments and does basic checks"
  parser = argparse.ArgumentParser()
  parser.add_argument("filename", help="source file")
  parser.add_argument("mode", help="statistics mode of aggregation (supported modes: composer, century)")
  args = parser.parse_args()

  if not Path(args.filename).is_file():
    eprint("Filename doesn't refer to a valid file")
    exit(2)
  if args.mode not in (COMPOSER_MODE, CENTURY_MODE):
    eprint("Statistic mode %s is not supported" % args.mode)
    exit(2)

  return args.filename, args.mode


def parse_file(filename, mode, stats):
  "This function parses source file with data"
  stats[mode] = collections.Counter()

  with open(filename, 'r', encoding="utf-8") as file:
    for line in file:
      globals()[PARSER_FUNC_PREFIX + mode](line, stats[mode])


def parse_line_composer(line, stats):
  "This function parses line and alter composer statistic data"
  composerLine = re.match( r'^Composer: (.*)', line)
  if composerLine:
    names = re.split(";", composerLine.group(1))
    for name in names:
      name = re.sub(r'[(].*[)]', '', name).strip()
      if name:
        stats[name] += 1


def parse_line_century(line, stats):
  "This function parses line and alter century statistic data"
  def centuryFromYear(year):
    return (year - 1) // 100 + 1

  centuryLine = re.match( r'^Composition Year:(.*)', line)
  if centuryLine:
    year = centuryLine.group(1).strip()
    if year:
      try:
        year = dateParse(year).year
      except ValueError:
        res = re.search(r".*(\d{4}).*", year)
        if res:
          year = res.group(1)
        else:
          res = re.search(r".*(\d{2}).*century", year)
          if res:
            year = res.group(1) + "00"
          else:
            year = None

      if year:
        stats[centuryFromYear(int(year))] += 1


def print_stats(mode, stats):
  "This function prints statistics"
  globals()[PRINTER_FUNC_PREFIX + mode](stats[mode])


def print_stats_composer(stats):
  "This function prints composer mode statistics"
  ordered = collections.OrderedDict(sorted(stats.items()))
  for k, v in ordered.items():
    print("{0}: {1}".format(k.encode(sys.stdout.encoding, errors='replace'), v))


def print_stats_century(stats):
  "This function prints century mode statistics"
  def get_century_suffix(century):
    if century == 1:
      return "st"
    elif century == 2:
      return "nd"
    elif century == 3:
      return "rd"
    else:
      return "th"

  ordered = collections.OrderedDict(sorted(stats.items()))
  for k, v in ordered.items():
    print("{0}{1} century: {2}".format(k, get_century_suffix(k), v))


if __name__ == "__main__":
  stats = {}
  file, mode = parse_args()
  parse_file(file, mode, stats)
  print_stats(mode, stats)
