#!/usr/bin/python3
import sys
import re


class Print:
  """ 
  This is a class representing Print. 
    
  Attributes: 
    print_id (str): Print number.
    edition (Edition): Instance of Edition class.
    partiture (boolean): Year of death or None.
  """
  def __init__(self, record):
    """ 
    The constructor for Print class.

    Constructs Print object from parsed record.

    Parameters: 
	    record (dict): Parsed record of print element.
    """
    self.print_id = record.get('print_id')
    self.partiture = record.get('partiture')
    self.edition = Edition(None, None, None)


  def composition(self):
  	return self.edition.composition


  def format(self):
    """ 
  	Reconstructs and prints the original stanza
    """
    print("Print Number: {0}\n"
          "Partiture: {1}".format(self.print_id, self.partiture))


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
  def __init__(self, incipit, key, genre, year, voices, authors):
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
    composition (Composition): The composition of which this edition is.
    authors (list of Person): The authors is this edition.
    name (str): Name of the edition or None.
  """

  def __init__(self, composition, authors, name):
    """ 
    The constructor for Edition class. 

    Parameters: 
      composition (Composition): The composition of which this edition is.
      authors (list of Person): The authors is this edition.
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
  record = {}
  with open(filename, 'r', encoding="utf-8") as file:
    for line in file:
      if line == "\n":
        yield record
        record = {}

      pritnNr = re.match(r'^Print Number: (.*)', line)
      if pritnNr:
        record["print_id"] = pritnNr.group(1)

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
