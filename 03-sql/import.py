#! python3

"""
This module creates database schema and persists parsed objects
"""
import os
import sys
import argparse
import sqlite3
import scorelib

def eprint(*args, **kwargs):
  "This function prints message to error output"
  print(*args, file=sys.stderr, **kwargs)


def parse_args():
  "This function parses command-line arguments and does basic checks"
  parser = argparse.ArgumentParser()
  parser.add_argument("filename", help="source file")
  parser.add_argument("database", help="SQLite database file")

  args = parser.parse_args()

  if not os.path.isfile(args.filename):
    eprint("Filename doesn't refer to a valid file")
    exit(2)

  if os.path.isfile(args.database):
    eprint("Database file already exists, will be overwritten")
    try:
      os.remove(args.database)
    except OSError:
      pass

  return args.filename, args.database


def create_db_schema(database, script):
  "This function creates database schema from given SQL script file"

  if not os.path.isfile(script):
    eprint("Database schema not found")
    exit(2)

  with open(script, "r") as script_file:
    con = sqlite3.connect(database)
    cur = con.cursor()
    cur.executescript(script_file.read())
    con.commit()


def persist_objects(database, lst):
  "This function persists objects in the given list"

  con = sqlite3.connect(database)
  con.row_factory = sqlite3.Row
  cur = con.cursor()

  for obj in lst:
    obj.persist(cur)
    con.commit()

  con.close()


#script body
DB_SCHEMA_SCRIPT = "./scorelib.sql"

#parse arguments
FILENAME, DB = parse_args()
#create db schema
create_db_schema(DB, DB_SCHEMA_SCRIPT)
#load print objects from text file
PRINT_LIST = scorelib.load(FILENAME)
#persist objects
persist_objects(DB, PRINT_LIST)
