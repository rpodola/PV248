#! python3
import sys
import re
import collections
import argparse
from os import path


PARSER_FUNC_PREFIX = 'parse_line_'
PRINTER_FUNC_PREFIX = 'print_stats_'
COMPOSER_MODE = 'composer'
CENTURY_MODE = 'century'


def eprint(*args, **kwargs):
  "This function prints message to error output"
  print(*args, file=sys.stderr, **kwargs)


def parse_args():
  "This function parses command-line arguments and does basic checks"
  parser = argparse.ArgumentParser()
  parser.add_argument("filename", help="source file")
  parser.add_argument("mode", help="statistics mode of aggregation "
                                   "(supported modes: composer, century)")
  args = parser.parse_args()

  if not path.isfile(args.filename):
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
  composerLine = re.match(r'^Composer: (.*)', line)
  if composerLine:
    names = re.split(";", composerLine.group(1))
    for name in names:
      name = re.sub(r'[(].*[)]', '', name).strip()
      if name:
        stats[name] += 1


def parse_line_century(line, stats):
  "This function parses line and alter century statistic data"
  def century_from_year(year):
    return (year - 1) // 100 + 1

  centuryLine = re.match(r'^Composition Year:(.*)', line)
  if centuryLine:
    parsedYear = centuryLine.group(1).strip()
    if parsedYear:
      res = re.search(r".*(\d{4}).*", parsedYear)
      if res:
        year = res.group(1)
      else:
        res = re.search(r".*(\d{2}).*century", parsedYear)
        if res:
          year = res.group(1) + "00"
        else:
          year = None

      if year:
        stats[century_from_year(int(year))] += 1


def print_stats(mode, stats):
  "This function prints statistics"
  globals()[PRINTER_FUNC_PREFIX + mode](stats[mode])


def print_stats_composer(stats):
  "This function prints composer mode statistics"
  ordered = collections.OrderedDict(sorted(stats.items()))
  for key, value in ordered.items():
    print("{0}: {1}".format(key.encode(sys.stdout.encoding, errors='replace'), value))


def print_stats_century(stats):
  "This function prints century mode statistics"
  def get_century_suffix(century):
    if century == 1:
      return "st"
    if century == 2:
      return "nd"
    if century == 3:
      return "rd"
    return "th"

  ordered = collections.OrderedDict(sorted(stats.items()))
  for key, value in ordered.items():
    print("{0}{1} century: {2}".format(key, get_century_suffix(key), value))


if __name__ == "__main__":
  stats = {}
  file, mode = parse_args()
  parse_file(file, mode, stats)
  print_stats(mode, stats)
