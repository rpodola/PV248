#! python3
import sys
import argparse
from os import path
from scorelib import load, Print

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

exit()
d = {"print_id": 55,
"title": "Titleee",
"genre": "rock",
"partiture": False,
"incipit": "adsasdasd",
"key": "keyyyy",
"composition_year": 1897,
"edition_name": "fakin edition",
"editors":[ {"name": "Bach", "birth":1872, "death":1878}, {"name": "AAAk"}],
"voices":[ {"name": "violin", "range": 'asdsa--444'}, {"name": "violin"}, {"range": "g-d3"}, {}],
"composers":[ {"name": "Bach", "birth":1872, "death":1878}, {"name": "Kock", "death":1802}, {"name": "AAAk"}]
}
Print(d).format()
exit()