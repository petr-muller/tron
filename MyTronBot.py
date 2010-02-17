#!/usr/bin/python

"""Template for your tron bot"""

import tron
import random
import copy
import math

class Coords:
  def __init__(self, x, y):
    self.x = x
    self.y = y

  def neigh(self, direction):
    if direction in ('N', 1):
      return Coords(self.x - 1, self.y)
    elif direction in ('S', 3):
      return Coords(self.x + 1, self.y)
    elif direction in ('W', 4):
      return Coords(self.x, self.y - 1)
    elif direction in ("E",2):
      return Coords(self.x, self.y + 1)

  def __str__(self):
    return "[%s,%s]" % (self.x,self.y)

  def distance(self, other):
    xes = self.x - other.x
    yes = self.y - other.y
    xes *= xes
    yes *= yes
    total = float(xes+yes)
    return math.sqrt(total)

class Map:
  def __init__(self, board):
    self.map = []
    for x in xrange(board.height):
      line = []
      for y in xrange(board.width):
        if board.passable((x,y)):
          line.append(' ')
        else:
          line.append('X')
      self.map.append(line)

  def __str__(self):
    return "\n".join(["".join(x) for x in self.map])


class Filler:
  def __init__(self, themap):
    self.map = copy.deepcopy(themap)
    self.myMain   = []
    self.hisMain  = []
    self.myControl = 0
    self.hisControl = 0

  def start(self, my, his):
    self.myMain.append(my)
    self.hisMain.append(his)

  def iterate(self):
    self.myControl += len(self.myMain)
    self.hisControl += len(self.hisMain)

    myAux  = []
    hisAux = []

    for my in self.myMain:
      self.map.map[my.x][my.y] = 'X'
      for candidate in [ my.neigh(x) for x in ('N','S','W','E') ]:
        if self.map.map[candidate.x][candidate.y] == ' ':
          self.map.map[candidate.x][candidate.y] = 'C'
          myAux.append(Coords(candidate.x, candidate.y))


    for his in self.hisMain:
      self.map.map[his.x][his.y] = 'X'
      for candidate in [ his.neigh(x) for x in ('N','S','W','E') ]:
        if self.map.map[candidate.x][candidate.y] == ' ':
          self.map.map[candidate.x][candidate.y] = 'X'
          hisAux.append(Coords(candidate.x, candidate.y))
        elif self.map.map[candidate.x][candidate.y] == 'C':
          self.map.map[candidate.x][candidate.y] = 'X'

    self.hisMain = hisAux;
    self.myMain = []

    for cand in myAux:
      if self.map.map[cand.x][cand.y] == 'C':
        self.map.map[cand.x][cand.y] = 'X'
        self.myMain.append(cand)

  def __str__(self):
    return str(self.map)

class Move:
  def __init__(self, direction):
    self.direction = direction
    self.distances = {}
    self.controls  = {}
    self.draw      = {}

def which_move_new(board):
  mymap = Map(board)

  myMoves = board.moves()
  hisPossible = dict((dir, board.rel(dir, board.them())) for dir in tron.DIRECTIONS)
  hisMoves = [ dir for dir in hisPossible if board.passable(hisPossible[dir])]

  me = board.me()
  he = board.them()
  myCoords = Coords(me[0], me[1])
  hisCoords = Coords(he[0], he[1])

  moveInstances = []

  for myMove in myMoves:
    startCoordsMy  = myCoords.neigh(myMove)

    move = Move(myMove)
    move.setDistance(startCoordsMy.distance(hisCoords), "start")

    for hisMove in hisMoves:
      startCoordsHis = hisCoords.neigh(hisMove)
      move.setDistance(startCoordsHis.distance(startCoordsMy), hisMove)
      filler.start(startCoordsMy, startCoordsHis)


def which_move(board):
    myMap = Map(board)

    myMoves = board.moves()
    hisPossible = dict((dir, board.rel(dir, board.them())) for dir in tron.DIRECTIONS)
    hisMoves = [ dir for dir in hisPossible if board.passable(hisPossible[dir])]

    me = board.me()
    he = board.them()
    myCoords = Coords(me[0], me[1])
    hisCoords = Coords(he[0], he[1])
    distances = {}
    for move in myMoves:
      distances[move] = hisCoords.distance(myCoords.neigh(move))

    distance = myCoords.distance(hisCoords)

    scoreBoard = {}

    for move in myMoves:
      scoreBoard[move] = 9999

    for myMove in myMoves:
      for hisMove in hisMoves:
        startCoordsMy  = myCoords.neigh(myMove)
        startCoordsHis = hisCoords.neigh(hisMove)

        filler = Filler(myMap)
        filler.start(startCoordsMy, startCoordsHis)
        myOld = hisOld = -1
        myNew = filler.myControl
        hisNew = filler.hisControl

        while (myOld != myNew) or (hisOld != hisNew):
          myOld = myNew
          hisOld = hisNew
          filler.iterate()
          myNew = filler.myControl
          hisNew = filler.hisControl

        score = myNew - hisNew
        scoreBoard[myMove] = min(scoreBoard[myMove], score)

    maxScore = max(scoreBoard.values())
    choices = []
    for choice in scoreBoard:
      if scoreBoard[choice] == maxScore:
        choices.append(choice)

    minimal = 9999
    to_return = None
    for choice in choices:
      if distances[choice] < minimal:
        minimal = distances[choice]
        to_return = choice

    return to_return

# you do not need to modify this part
for board in tron.Board.generate():
    tron.move(which_move(board))
