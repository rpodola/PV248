#!/usr/bin/python3
import re


class Print:
  """
  This is a class representing Print.

  Attributes:
    print_id (str): Print number.
    edition (Edition): Instance of Edition class.
    partiture (boolean): Partiture flag.
  """
  def __init__(self, record):
    """
    The constructor for Print class.

    Constructs Print object from parsed record.

    Parameters:
	    record (dict): Parsed record of print element.
    """
    try:
      self.print_id = int(record.get('print_id'))
    except TypeError:
      self.print_id = None

    self.partiture = bool(record.get('partiture', False))

    authors = []
    for c in record.get('composers', []):
      authors.append(Person(c.get('name'), c.get('birth'), c.get('death')))

    voices = []
    for v in record.get('voices', []):
      voices.append(Voice(v.get('name'), v.get('range')))

    editors = []
    for e in record.get('editors', []):
      editors.append(Person(e.get('name'), e.get('birth'), e.get('death')))

    composition = Composition(name=record.get('title'),
                              incipit=record.get('incipit'),
                              key=record.get('key'),
                              genre=record.get('genre'),
                              year=record.get('composition_year'),
                              voices=voices, authors=authors)

    self.edition = Edition(composition, editors, record.get('edition_name'))


  def composition(self):
    return self.edition.composition


  def format(self):
    """
  	Reconstructs and prints the original stanza
    """
    composers = []
    for author in self.composition().authors:
      composer = author.name
      if author.born or author.died:
        composer += " ({}--{})".format(author.born or '', author.died or '')
      composers.append(composer)

    editors = [editor.name for editor in self.edition.authors]

    voices = []
    for i, v in enumerate(self.composition().voices, 1):
      voice = "Voice {}: ".format(i)
      voice += v.range or ''
      if v.range and v.name:
        voice += ", "
      voice += v.name or ''
      voices.append(voice)

    return ("Print Number: {}\n"
          "Composer: {}\n"
          "Title: {}\n"
          "Genre: {}\n"
          "Key: {}\n"
          "Composition Year: {}\n"
          "Edition: {}\n"
          "Editor: {}\n"
          "{}\n"
          "Partiture: {}\n"
          "Incipit: {}\n"
          "".format(self.print_id if self.print_id is not None else '',
                    "; ".join(composers),
                    self.composition().name or '',
                    self.composition().genre or '',
                    self.composition().key or '',
                    self.composition().year or '',
                    self.edition.name or '',
                    ", ".join(editors),
                    "\n".join(voices) or 'Voice 1: ',
                    self.partiture,
                    self.composition().incipit or ''))


  def find(self, cursor):
    """
    Internal method that try to find equal print record in database.

    Equality of print records depends on ID (Print number).
    """
    sql = "SELECT * FROM print WHERE id = ?"
    cursor.execute(sql, (self.print_id,))
    row = cursor.fetchone()

    if row is not None:
      return dict_from_row(row)

    return None


  def persist(self, cursor):
    sql = "INSERT INTO print (id, partiture, edition) VALUES (?,?,?)"

    res = self.find(cursor)
    if res is not None:
      return res["id"]

    edition_id = self.edition.persist(cursor)
    cursor.execute(sql, (self.print_id, "Y" if self.partiture else "N", edition_id))

    return cursor.lastrowid


class Person:
  """
  This is a class representing Person.

  Attributes:
    name (str): Name of the person.
    born (int): Year of birth or None.
    died (int): Year of death or None.
  """
  def __init__(self, name, born, died):
    """
    The constructor for Person class.

    Parameters:
	    name (str): Name of the person.
	    born (int): Year of birth or None.
	    died (int): Year of death or None.
    """
    self.name = name
    try:
      self.born = int(born)
    except:
      self.born = None

    try:
      self.died = int(died)
    except:
      self.died = None


  def get_by_name(self, cursor):
    """
    Internal method that try to find equal person record in database.

    Equality of person records depends on name.
    """
    sql = "SELECT * FROM person WHERE name = ?"
    cursor.execute(sql, (self.name,))
    row = cursor.fetchone()

    if row is not None:
      return dict_from_row(row)

    return None


  def persist(self, cursor):
    sql = "INSERT INTO person (born, died, name) VALUES (?,?,?)"
    sql_update_born = "UPDATE person SET born = ? WHERE id = ?"
    sql_update_died = "UPDATE person SET died = ? WHERE id = ?"

    res = self.get_by_name(cursor)
    if res is None:
      cursor.execute(sql, (self.born, self.died, self.name))
      return cursor.lastrowid
    else:
      if res["born"] != self.born and self.born is not None:
        cursor.execute(sql_update_born, (self.born, res["id"]))
      if res["died"] != self.died and self.died is not None:
        cursor.execute(sql_update_died, (self.died, res["id"]))
      return res["id"]



class Voice:
  """
  This is a class representing Voice.

  Attributes:
    name (str): Name of the voice or None.
    range (str): Range of the voice or None.
  """
  def __init__(self, name, range):
    """
    The constructor for Voice class.

    Parameters:
	    name (str): Name of the voice or None.
	    range (str): Range of the voice or None.
    """
    self.name = name
    self.range = range


  def persist(self, cursor, number, score):
    sql = "INSERT INTO voice (number, score, range, name) VALUES (?,?,?,?)"

    cursor.execute(sql, (number, score, self.range, self.name))

    return cursor.lastrowid


class Composition:
  """
  This is a class representing Composition.

  Attributes:
    name (str): Name of the composition or None.
    incipit (str): Incipit of the composition or None.
    key (str): The composition key or None.
    genre (str): The composition genre or None.
    year (int): An integral year or None.
    voices (list of Voice): The voices in this composition.
    authors (list of Person): The authors of this composition.
  """
  def __init__(self, name, incipit, key, genre, year, voices, authors):
    """
    The constructor for Composition class.

    Parameters:
	    name (str): Name of the composition or None.
	    incipit (str): The incipit of the composition or None.
	    key (str): The composition key or None.
	    genre (str): The composition genre or None.
	    year (int): An integral year or None.
	    voices (list of Voice): The voices in this composition.
	    authors (list of Person): The authors of this composition.
    """
    self.name = name
    self.incipit = incipit
    self.key = key
    self.genre = genre
    try:
      self.year = int(year)
    except:
      self.year = None
    self.voices = voices
    self.authors = authors


  def find(self, cursor):
    """
    Internal method that try to find equal score record in database.

    Equality depends on real entities relations.
    Equality of score records depends on attributes, voices and composers.
    """
    sql = ("SELECT * FROM score WHERE name = ? and incipit = ? and key = ? "
          "and genre = ? and year = ?")
    cursor.execute(sql, (self.name, self.incipit, self.key, self.genre, self.year))
    score = cursor.fetchone()

    if score is None:
      return None
    score = dict_from_row(score)

    #check for the same voices
    sql_voice = "SELECT * FROM voice WHERE score = ? ORDER BY number"
    cursor.execute(sql_voice, (score["id"],))
    voices = cursor.fetchall()
    if len(self.voices) != len(voices):
      return None
    for idx, v in enumerate([dict_from_row(voice) for voice in voices]):
      if v["range"] != self.voices[idx].range:
        return None
      if v["name"] != self.voices[idx].name:
        return None

    #check for the same authors
    sql_voice = ("SELECT p.name FROM score_author sa join person p on (sa.composer = p.id) "
                 "WHERE sa.score = ?")
    cursor.execute(sql_voice, (score["id"],))
    author_names = [dict_from_row(a)["name"] for a in cursor.fetchall()]
    if len(self.authors) != len(author_names):
      return None
    if len(author_names) > 0:
      for auth in self.authors:
        if auth.name not in author_names:
          return None

    return score


  def persist(self, cursor):
    sql = "INSERT INTO score (name, genre, key, incipit, year) VALUES (?,?,?,?,?)"
    sql_authors = "INSERT INTO score_author (score, composer) VALUES (?,?)"

    res = self.find(cursor)
    if res is not None:
      return res["id"]

    #persist score
    cursor.execute(sql, (self.name, self.genre, self.key, self.incipit, self.year))
    score_id = cursor.lastrowid

    #persist score-author relationships
    for auth in self.authors:
      person_id = auth.persist(cursor)
      cursor.execute(sql_authors, (score_id, person_id))

    #persist voices
    for idx, voice in enumerate(self.voices):
      person_id = voice.persist(cursor, idx + 1, score_id)

    return score_id


class Edition:
  """
  This is a class representing Edition.

  Attributes:
    composition (Composition): The composition of which the edition is.
    authors (list of Person): The authors of the edition.
    name (str): Name of the edition or None.
  """

  def __init__(self, composition, authors, name):
    """
    The constructor for Edition class.

    Parameters:
      composition (Composition): The composition of which the edition is.
      authors (list of Person): The authors of the edition.
      name (str): Name of the edition or None.
    """
    self.composition = composition
    self.authors = authors
    self.name = name


  def find(self, cursor):
    """
    Internal method that try to find equal edition record in database.

    Equality depends on real entities relations.
    Equality of edition records depends on name, score and editors.
    """
    sql = "SELECT * FROM edition WHERE name = ?"
    cursor.execute(sql, (self.name,))
    edition = cursor.fetchone()

    if edition is None:
      return None
    edition = dict_from_row(edition)

    #check for the same authors
    sql_voice = ("SELECT p.name FROM edition_author sa join person p on (sa.editor = p.id) "
                 "WHERE sa.edition = ?")
    cursor.execute(sql_voice, (edition["id"],))
    author_names = [dict_from_row(a)["name"] for a in cursor.fetchall()]
    if len(self.authors) != len(author_names):
      return None
    if len(author_names) > 0:
      for auth in self.authors:
        if auth.name not in author_names:
          return None

    if self.composition.find(cursor) is None:
      return None

    return edition


  def persist(self, cursor):
    sql = "INSERT INTO edition (score, name, year) VALUES (?,?,null)"
    sql_editors = "INSERT INTO edition_author (edition, editor) VALUES (?,?)"

    res = self.find(cursor)
    if res is not None:
      return res["id"]

    #persist composition
    score_id = self.composition.persist(cursor)

    #persist edition
    cursor.execute(sql, (score_id, self.name))
    edition_id = cursor.lastrowid

    #persist edition-author relationships
    for auth in self.authors:
      person_id = auth.persist(cursor)
      cursor.execute(sql_editors, (edition_id, person_id))

    return edition_id


def parse_record_line(line, record):
  """
  Parses record line to dictionary.

  Parameters:
    line (str): The record line from source file.
    record (dict): The dictionary with parsed values.
  """
  def parse_partiture(data):
    if re.search(r'yes|true|True|Yes', data):
      return True
    return False

  def parse_composers(line):
    "This function parses all composers from line"
    composers_list = []
    composers = re.split(";", line)
    for composer in composers:
      item = {}
      item["name"] = re.sub(r'[(].*[)]', '', composer).strip()

      dates = re.search(r'[(](\d{4})?-?-?(\d{4})?[)]', composer)
      if dates:
        item["birth"] = dates.group(1)
        item["death"] = dates.group(2)
      else:
        dates = re.search(r'[(]([+*])(\d{4})[)]', composer)
        if dates:
          if dates.group(1) == '*':
            item["birth"] = dates.group(2)
          else:
            item["death"] = dates.group(2)
        else:
          dates = re.search(r'[(][^-]*-?-?(\d{4})[)]', composer)
          if dates:
            item["death"] = dates.group(1)
          else:
            dates = re.search(r'[(](\d{4})-?-?.*[)]', composer)
            if dates:
              item["birth"] = dates.group(1)

      composers_list.append(item)
    return composers_list

  def parse_voices(line, record):
    "This function parses all voices from line"
    voice = {}
    res = re.search(r'(?P<range>\w+--\w+)[,;]?(?P<name>.*)', line)
    if res:
      if res.group("name"):
        voice["name"] = res.group("name").strip()
      voice["range"] = res.group("range").strip()
    else:
      voice["name"] = line.strip()

    if record.get("voices"):
      record["voices"].append(voice)
    else:
      record["voices"] = [voice]

  def parse_editors(line):
    "This function parses all editors from line"
    editors_list = []
    editors = re.findall(r'([\w.]+,?\s{1}[\w.]+)', line)
    if not editors:
      editor = re.search(r'(\w+)', line)
      if editor:
        editors_list.append({"name": editor.group(1)})
    else:
      for editor in editors:
        editors_list.append({"name": editor})

    return editors_list


  pritnNr = re.match(r'^Print Number:[^\d]*(\d+).*', line)
  if pritnNr:
    record["print_id"] = pritnNr.group(1)
    return

  partiture = re.match(r'^Partiture:(.*)', line)
  if partiture:
    record["partiture"] = parse_partiture(partiture.group(1))
    return

  title = re.match(r'^Title:(.*)', line)
  if title:
    record["title"] = title.group(1).strip()
    return

  incipit = re.match(r'^Incipit:(.*)', line)
  if incipit:
    record["incipit"] = incipit.group(1).strip()
    return

  key = re.match(r'^Key:(.*)', line)
  if key:
    record["key"] = key.group(1).strip()
    return

  genre = re.match(r'^Genre:(.*)', line)
  if genre:
    record["genre"] = genre.group(1).strip()
    return

  compositionYear = re.match(r'^Composition Year:.*(\d{4}).*', line)
  if compositionYear:
    record["composition_year"] = compositionYear.group(1)
    return

  edition = re.match(r'^Edition:(.*)', line)
  if edition:
    record["edition_name"] = edition.group(1).strip()
    return

  editors = re.match(r'^Editor:(.*)', line)
  if editors:
    record["editors"] = parse_editors(editors.group(1).strip())
    return

  composers = re.match(r'^Composer:(.*)', line)
  if composers:
    record["composers"] = parse_composers(composers.group(1).strip())
    return

  voices = re.match(r'^Voice \d+:(.*)', line)
  if voices:
    parse_voices(voices.group(1).strip(), record)
    return


def read_in_records(filename):
  """
  Lazy function (generator) to read a file record by record.

  Records are separated by empty line.

  Parameters:
    filename (str): The filename of source file.

  Returns:
    dict representing parsed record
  """
  record = {}
  with open(filename, 'r', encoding="utf-8") as file:
    for line in file:
      if line == "\n":
        yield record
        record = {}

      parse_record_line(line, record)

  yield record


def load(filename):
  """
  Reads and parses the text file and returns a list of Print instances.

  Parameters:
    filename (str): The filename of source file.

  Returns:
    list of Print instances sorted by print_id
  """
  records = []
  for record in read_in_records(filename):
    if record:
      records.append(Print(record))

  return records


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
