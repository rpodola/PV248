#! python3

"""
This script creates http server running on localhost on given port that forwards requests to upstream
"""
import sys
import argparse
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
import http.client
import time

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
  parser.add_argument("port", type=int, help="Server port")
  parser.add_argument("-v", action='store_true', help="Activation of verbose mode")

  args = parser.parse_args()

  return args.port, args.v


class TTTHandler(BaseHTTPRequestHandler):
  _games_manager = None
  _game_args = {}

  def do_GET(self):
    self._parse_req()

    if(self._command == "start"):
      self._start_req()
    elif(self._command == "status"):
      self._status_req()
    elif(self._command == "play"):
      self._play_req()
    else:
      self.send_error(http.client.NOT_FOUND, explain='request {} is not supported'.format(self.path))


  def _parse_req(self):
    game_command, _, game_args = self.path.partition('?')
    self._command = game_command.replace('/', '')

    try:
      self._game_args = dict(arg.split('=') for arg in game_args.split('&'))
    except ValueError:
      self._game_args = {}

    verbose_print("Game command: " + self._command)
    verbose_print("Game arguments: " + str(self._game_args))


  def _start_req(self):
    game_id = self._games_manager.create_game(self._game_args.get("name", ''))
    reply_body = {"id": int(game_id)}
    self._response_ok(reply_body)


  def _status_req(self):
    try:
      game = self._games_manager.get_game(int(self._game_args["game"]))
    except ValueError as e:
      verbose_print(e)
      self.send_error(http.client.FORBIDDEN, explain='Game ID must be numeric')
      return
    except KeyError as e:
      verbose_print(e)
      self.send_error(http.client.NOT_FOUND, explain='Invalid or missing game ID')
      return

    if(game.active):
      reply_body = {"board": game.board,
                    "next": game.next_player}
    else:
      reply_body = {"winner": game.winner}

    self._response_ok(reply_body)


  def _play_req(self):
    try:
      game = self._games_manager.get_game(int(self._game_args["game"]))
    except ValueError as e:
      verbose_print(e)
      self.send_error(http.client.FORBIDDEN, explain='Game ID must be numeric')
      return
    except KeyError as e:
      verbose_print(e)
      self.send_error(http.client.NOT_FOUND, explain='Invalid or missing game ID')
      return

    try:
      player = int(self._game_args["player"])
      if(player not in (1, 2)):
        raise ValueError
    except ValueError as e:
      verbose_print(e)
      self.send_error(http.client.FORBIDDEN, explain='Player number must be in range (1, 2)')
      return
    except KeyError as e:
      verbose_print(e)
      self.send_error(http.client.NOT_FOUND, explain='Missing player number')
      return

    try:
      x_cord = int(self._game_args["x"])
      y_cord = int(self._game_args["y"])
    except ValueError as e:
      verbose_print(e)
      self.send_error(http.client.FORBIDDEN, explain='Coordinates must be numeric')
      return
    except KeyError as e:
      verbose_print(e)
      self.send_error(http.client.NOT_FOUND, explain='Coordinates missing')
      return

    result = game.play(player, x_cord, y_cord)
    if(not isinstance(result, tuple)):
      reply_body = {"status": "ok"}
    else:
      reply_body = {"status": "bad",
                    "message": result[1]}

    self._response_ok(reply_body)

    verbose_print(game.dump_board())


  def _response_ok(self, body=None):
    self.send_response(http.client.OK)
    self.send_header("Content-Type", 'application/json')
    self.end_headers()
    if(body):
      self.wfile.write(bytes(json.dumps(body), "utf8"))


class GamesManager:
  def __init__(self):
    self._games = {}


  def create_game(self, name):
    game_id = len(self._games)
    self._games[str(game_id)] = Game(name)

    return game_id

  def get_game(self, game_id):
    return self._games[str(game_id)]


class Game:
  def __init__(self, name, size=3):
    #game starts with empoty board
    self._board = [[0] * size for i in range(size)]
    #player 1 starts
    self._next_player = 1
    #initial status is active
    self._active = True
    #initial winner is nobody
    self._winner = None
    self._name = name

  @property
  def board(self):
    return self._board

  @property
  def next_player(self):
    return self._next_player

  @property
  def active(self):
    return self._active

  @property
  def winner(self):
    return self._winner

  @property
  def name(self):
    return self._name

  def play(self, player, x, y):
    if(not self._active):
      return False, "Game is no longer active"

    if(player != self._next_player):
      return False, "Player {} is not on the move".format(player)

    try:
      self._move(x, y)
      self._next_player = (self._next_player % 2) + 1
    except ValueError as e:
      return False, str(e)

    if(self._check_for_winner(player)):
      self._active = False
      self._winner = player
    elif(self._check_for_tie()):
      self._active = False
      self._winner = 0

    return True

  def _move(self, x, y):
    if(x not in range(len(self._board))):
      raise ValueError("X coordinate out of range")

    if(y not in range(len(self._board))):
      raise ValueError("Y coordinate out of range")

    if(self._board[x][y] != 0):
      raise ValueError("Field [{}][{}] is not empty".format(x, y))

    self._board[x][y] = self._next_player

  def _check_for_winner(self, player):
    #diagonal check
    b = self._board
    if(b[0][0] == b[1][1] == b[2][2] == player or 
       b[2][0] == b[1][1] == b[0][2] == player):
      return True

    #horizontal or vertical check
    for x in range(3):
      if(b[x][0] == b[x][1] == b[x][2] == player or 
         b[0][x] == b[1][x] == b[2][x] == player):
        return True

    return False

  def _check_for_tie(self):
    if not any(0 in row for row in self._board):
      return True
    return False

  def dump_board(self):
    board_str = ""
    for row in self._board:
      for cel in row:
        board_str += str(cel) + " "
      board_str += "\n"

    return board_str


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
  """Handle requests in a separate thread."""


def run_server(port):
  TTTHandler._games_manager = GamesManager()
  server = ThreadedHTTPServer(('localhost', port), TTTHandler)
  server.serve_forever()


if __name__ == "__main__":
  PORT, VERBOSE = parse_args()
  run_server(PORT)
