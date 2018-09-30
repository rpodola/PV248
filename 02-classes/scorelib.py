#!/usr/bin/python3
import sys
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
    self.print_id = record.get('print_id')
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
          "".format(self.print_id or '',
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
    self.born = born
    self.died = died


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
    self.year = year
    self.voices = voices
    self.authors = authors


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


def read_in_records(filename):
  """
  Lazy function (generator) to read a file record by record.

  Records are separated by empty line.

  Parameters: 
    filename (str): The filename of source file.

	Returns:
		dict representing parsed record
  """
  def parse_partiture(data):
    if re.search(r'yes|true|True|Yes', data):
      return True
    return False

  def parse_partiture(data):
    if re.search(r'yes|true|True|Yes', data):
      return True
    return False

  record = {}
  with open(filename, 'r', encoding="utf-8") as file:
    for line in file:
      if line == "\n":
        yield record
        record = {}

      pritnNr = re.match(r'^Print Number:[^\d]*(\d+).*', line)
      if pritnNr:
        record["print_id"] = pritnNr.group(1)

      partiture = re.match(r'^Partiture:(.*)', line)
      if partiture:
        record["partiture"] = parse_partiture(partiture.group(1))

      title = re.match(r'^Title:(.*)', line)
      if title:
        record["title"] = title.group(1).strip()

      incipit = re.match(r'^Incipit:(.*)', line)
      if incipit:
        record["incipit"] = incipit.group(1).strip()

      key = re.match(r'^Key:(.*)', line)
      if key:
        record["key"] = key.group(1).strip()

      genre = re.match(r'^Genre:(.*)', line)
      if genre:
        record["genre"] = genre.group(1).strip()

      compositionYear = re.match(r'^Composition Year:.*(\d{4}).*', line)
      if compositionYear:
        record["composition_year"] = compositionYear.group(1)

      edition = re.match(r'^Edition:(.*)', line)
      if edition:
        record["edition_name"] = edition.group(1).strip()

      editors= re.match(r'^Editor:(.*)', line)
      if editors:
        record["editors"] = []

      composers= re.match(r'^Composer:(.*)', line)
      if editors:
        record["composers"] = []

      voices= re.match(r'^Voice \d+:(.*)', line)
      if voices:
        record["voices"] = []

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
    records.append(Print(record))

  return records
