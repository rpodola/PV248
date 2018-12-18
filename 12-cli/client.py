#! python3

"""
This script represents game client for game Tic-Tac-Toe
"""
import sys
import argparse
import json
import http.client
import time
import re


def eprint(*args, **kwargs):
  "This function prints message to error output"
  print(*args, file=sys.stderr, **kwargs)


def verbose_print(*args, **kwargs):
  "This function prints message in verbose mode"
  if VERBOSE:
    print(*args, file=sys.stderr, **kwargs)


def parse_args():
  "This function parses command-line arguments and does basic checks"
  parser = argparse.ArgumentParser()
  parser.add_argument("host", help="Game server address")
  parser.add_argument("port", type=int, help="Game server port")
  parser.add_argument("-v", action='store_true', help="Activation of verbose mode")

  args = parser.parse_args()

  return args.host, args.port, args.v


class TTTClientException(Exception):
  pass


class TTTClient():
  def __init__(self, ip, port):
    self._ip = ip
    self._port = port
    self._games = self._http_req("list")
    self._player = None
    self._game_id = None
    self._game_state = None


  def _http_req(self, req, args={}):
    def serialize_args():
      if( not args ):
        return ''
      args_list = ["{}={}".format(k, v) for k, v in args.items()]
      return '?' + '&'.join(args_list)


    try:
      conn = http.client.HTTPConnection(self._ip, self._port)
      conn.request("GET", '/'+req+serialize_args())

      resp = conn.getresponse()
      data = resp.read().decode('utf-8')

      verbose_print(data)
      if( resp.status == http.client.OK ):
        return json.loads(data)

    except Exception:
      raise
    finally:
      conn.close()

    raise TTTClientException("Communication with game server failed with code: {}".format(resp.status))


  def select_game(self):
    for game in self._games:
      print("{} {}".format(game["id"], game["name"]))

    while True:
      if( self._validate_game_id(input('Choose game ID or new game: ')) ):
        return
      else:
        print('Option not valid!')


  def _validate_game_id(self, game_id):
    res = re.search(r'^new\s*(?P<name>\w*)', game_id.strip())
    if( res ):
      if( res.group("name") ):
        self._start_new_game(res.group("name").strip())
      else:
        self._start_new_game()
      self._player = 1
      return True
    else:
      self._player = 2
      try:
        game_id = int(game_id)
      except ValueError:
        return False

      if( any(game_id == game["id"] for game in self._games) ):
        self._game_id = game_id
        return True


  def play_game(self):
    print_state = True
    while True:
      self._refresh_status()

      if( self._game_state.get("next") == self._player ):
        self._print_board()
        self._play_prompt()
        print_state = True
        continue

      if( print_state ):
        self._print_board()
        print("waiting for the other player")
        print_state = False
      time.sleep(1)


  def _play_prompt(self):
    while True:
      try:
        coords = input('your turn ({}): '.format('x' if self._player == 1 else 'o'))
        res = re.search(r'(?P<x>\d+)\s+(?P<y>\d+)', coords.strip())
        if( not res ):
          raise TTTClientException("Invalid coordinates input")
        verbose_print(res.groups())
        self._make_move(res.group("x"), res.group("y"))
      except TTTClientException as e:
        print("invalid input")
        verbose_print(e)
        continue

      return


  def _make_move(self, x, y):
    resp = self._http_req("play", {"game": self._game_id,
                                   "player": self._player,
                                   "x": y, "y": x})
    if( resp.get("status") == "bad" ):
      raise TTTClientException("Moved failed: "+resp.get("message", ''))


  def _start_new_game(self, name=''):
    if( name == ''):
      name = "game"+str(len(self._games))
    resp = self._http_req("start", {"name": name})
    self._game_id = resp["id"]


  def _refresh_status(self, print_board=True):
    self._game_state = self._http_req("status", {"game": self._game_id})
    verbose_print(self._game_state)

    if( self._game_state.get("winner") is not None ):
      self._print_results(self._game_state.get("winner"))
      exit()


  def _print_results(self, winner):
    if( winner == 0):
      print("draw")
    elif ( winner == self._player ):
      print("you win")
    else:
      print("you lose")


  def _print_board(self):
    if( self._game_state.get("board") is None ):
      return
    for row in self._game_state.get("board"):
      for field in row:
        if( field == 1 ):
          print('x', end='')
        elif( field == 2 ):
          print('o', end='')
        else:
          print('_', end='')
      print()



if __name__ == "__main__":
  HOST, PORT, VERBOSE = parse_args()
  client = TTTClient(HOST, PORT)
  client.select_game()
  client.play_game()