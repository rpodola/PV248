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

    print("Print Number: {}\n"
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


  def _find(self, cursor):
    SQL = "SELECT * FROM print WHERE id = ?"
    cursor.execute(SQL, (self.print_id,))
    row = cursor.fetchone()

    if row is not None:
      return dict_from_row(row)

    return None


  def persist(self, cursor):
    SQL = "INSERT INTO print (id, partiture, edition) VALUES (?,?,?)"

    res = self._find(cursor)
    if res is not None:
      return res["id"]

    edition_id = self.edition.persist(cursor)
    cursor.execute(SQL, (self.print_id, "Y" if self.partiture else "N", edition_id))

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


  def _get_by_name(self, cursor):
    SQL = "SELECT * FROM person WHERE name = ?"
    cursor.execute(SQL, (self.name,))
    row = cursor.fetchone()

    if row is not None:
      return dict_from_row(row)

    return None


  def persist(self, cursor):
    SQL = "INSERT INTO person (born, died, name) VALUES (?,?,?)"
    SQL_UPDATE = "UPDATE person SET born = ?, died = ? WHERE id = ?"

    res = self._get_by_name(cursor)
    if res is None:
      cursor.execute(SQL, (self.born, self.died, self.name))
    elif res["born"] != self.born or res["died"] != self.died:
      cursor.execute(SQL_UPDATE, (self.born, self.died, res["id"]))
      return res["id"]
    else:
      return res["id"]

    return cursor.lastrowid


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
    SQL = "INSERT INTO voice (number, score, range, name) VALUES (?,?,?,?)"

    cursor.execute(SQL, (number, score, self.range, self.name))

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


  def _find(self, cursor):
    return None
    SQL = "SELECT * FROM voice WHERE name = ? and range = ?"
    cursor.execute(SQL, (self.name, self.range))
    row = cursor.fetchone()

    if row is not None:
      return dict_from_row(row)

    return None


  def persist(self, cursor):
    SQL = "INSERT INTO score (name, genre, key, incipit, year) VALUES (?,?,?,?,?)"
    SQL_AUTHORS = "INSERT INTO score_author (score, composer) VALUES (?,?)"

    if self._find(cursor) is not None:
      return cursor.lastrowid

    #persist score
    cursor.execute(SQL, (self.name, self.genre, self.key, self.incipit, self.year))
    score_id = cursor.lastrowid

    #persist score-author relationships
    for auth in self.authors:
      person_id = auth.persist(cursor)
      cursor.execute(SQL_AUTHORS, (score_id, person_id))

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


  def _find(self, cursor):
    return None
    SQL = "SELECT * FROM voice WHERE name = ? and range = ?"
    cursor.execute(SQL, (self.name, self.range))
    row = cursor.fetchone()

    if row is not None:
      return dict_from_row(row)

    return None


  def persist(self, cursor):
    SQL = "INSERT INTO edition (score, name, year) VALUES (?,?,null)"
    SQL_EDITORS = "INSERT INTO edition_author (edition, editor) VALUES (?,?)"

    if self._find(cursor) is not None:
      return cursor.lastrowid

    #persist composition
    score_id = self.composition.persist(cursor)

    #persist edition
    cursor.execute(SQL, (score_id, self.name))
    edition_id = cursor.lastrowid

    #persist edition-author relationships
    for auth in self.authors:
      person_id = auth.persist(cursor)
      cursor.execute(SQL_EDITORS, (edition_id, person_id))

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
  return dict(zip(row.keys(), row))
