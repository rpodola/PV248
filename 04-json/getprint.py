#! python3

"""
This script prints composers of given Print ID
"""
import sys
import argparse
import sqlite3
import json


def eprint(*args, **kwargs):
  "This function prints message to error output"
  print(*args, file=sys.stderr, **kwargs)


def parse_args():
  "This function parses command-line arguments and does basic checks"
  parser = argparse.ArgumentParser()
  parser.add_argument("print_id", help="Print ID")

  args = parser.parse_args()

  return args.print_id


def dict_from_row(row):
  """
  Helper function to create dictionary from row returned from database.

  Keys for values are equal to column names in database table.

  Parameters:
    row (object): The sqlite3 row object.

  Returns:
    dict representing row
  """
  return dict(zip(row.keys(), row))


def get_print_authors(database, print_id):
  sql = ("select p.* from print pr "
         "join edition e on pr.edition = e.id "
         "join score s on e.score = s.id "
         "join score_author sa on sa.score = s.id "
         "join person p on sa.composer = p.id "
         "where pr.id = ?")

  con = sqlite3.connect(database)
  con.row_factory = sqlite3.Row
  cur = con.cursor()

  cur.execute(sql, (print_id,))
  authors = [dict_from_row(row) for row in cur.fetchall()]

  con.close()
  return authors


def nice_print(authors):
  for a in authors:
    a.pop('id', None)
    if a["born"] is None:
      a.pop('born', None)
    if a["died"] is None:
      a.pop('died', None)

  print(json.dumps(authors, indent=2, ensure_ascii=False))


#script body
DB_FILE = "./scorelib.dat"

#parse arguments
print_id = parse_args()
#load author objects from database
author_list = get_print_authors(DB_FILE, print_id)
#print authors nicely
nice_print(author_list)
