#! python3
import sys
import argparse
import os
import scorelib
import sqlite3

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
    eprint("Database file already exists")
    try:
      os.remove(args.database)
    except OSError:
      pass

  return args.filename, args.database


def create_db_schema(db, script):
  "This function creates database schema from given SQL script file"

  if not os.path.isfile(script):
    eprint("Database schema not found")
    exit(2)

  with open(script, "r") as script_file:
    con = sqlite3.connect(db)
    cur = con.cursor()
    cur.executescript(script_file.read())
    con.commit()


def persist_objects(db, list):
  "This function persists objects in the given list"

  con = sqlite3.connect(db)
  con.row_factory = sqlite3.Row
  cur = con.cursor()

  for obj in list:
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
print_list = scorelib.load(FILENAME)
#persist objects
persist_objects(DB, print_list[:5])
