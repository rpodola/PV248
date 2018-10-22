#! python3

"""
This script search for Print records where the given Composer participates
Each record is printed as JSON structure
Composer is given as his name subtring
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
  parser.add_argument("composer", help="Composer's name substring")

  args = parser.parse_args()

  return args.composer


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


def get_composers_id(cursor, composer):
  """
  This funtion finds and return composers matching given name substring

  Returns:
    list of composers 
  """
  sql_composer_match = ("select p.id, p.name from person p "
                        "join score_author s on s.composer = p.id "
                        "where p.name like ?")
  
  cursor.execute(sql_composer_match, ('%'+composer+'%',))
  return [dict_from_row(row) for row in cursor.fetchall()]


def get_print_by_composer(cursor, composer_id):
  """Return list of Prints where composer participates"""

  sql = ("select pr.id as 'Print Number',"
         "pr.partiture as Partiture,"
         "s.name as Title,"
         "s.genre as Genre,"
         "s.key as Key,"
         "s.incipit as Incipit,"
         "s.year as 'Composition Year',"
         "e.name as 'Edition',"
         "s.id as score_id,"
         "e.id as edition_id "
         "from print pr "
         "join edition e on pr.edition = e.id "
         "join score s on e.score = s.id "
         "join score_author sa on sa.score = s.id "
         "where sa.composer = ?")

  sql_voices = ("select name, range "
                "from voice "
                "where score = ? "
                "order by number")

  sql_composer = ("select p.name, p.born, p.died "
                 "from person p "
                 "join score_author s on p.id = s.composer "
                 "where s.score = ?")

  sql_editor = ("select p.name, p.born, p.died "
                "from person p "
                "join edition_author e on p.id = e.editor "
                "where e.edition = ?")

  cursor.execute(sql, (composer_id,))
  prints = [dict_from_row(row) for row in cursor.fetchall()]

  for p in prints:
    for k in p.keys():
      if p[k] == "":
        p[k] = None

    p["Partiture"] = p["Partiture"] == "Y"

    cursor.execute(sql_voices, (p["score_id"],))
    p["Voices"] = [dict_from_row(row) for row in cursor.fetchall()]

    cursor.execute(sql_composer, (p["score_id"],))
    p["Composer"] = [dict_from_row(row) for row in cursor.fetchall()]

    cursor.execute(sql_editor, (p["edition_id"],))
    p["Editor"] = [dict_from_row(row) for row in cursor.fetchall()]

    del p["score_id"]
    del p["edition_id"]

  return prints


#script body
DB_FILE = "./scorelib.dat"

#parse arguments
composer = parse_args()

con = sqlite3.connect(DB_FILE)
con.row_factory = sqlite3.Row
cur = con.cursor()

prints = {}
#get id of composers matching given name substring
composer_list = get_composers_id(cur, composer)
for c in composer_list:
  prints[c["name"]] = get_print_by_composer(cur, c["id"])

con.close()

print(json.dumps(prints, indent=2, ensure_ascii=False))
