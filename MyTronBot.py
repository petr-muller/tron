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

  def __eq__(self, other):
    return (self.x == other.x) and (self.y == other.y)

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

  def fill(self):
    firOld = -1
    secOld = -1

    firNew = 0
    secNew = 0

    while (firOld != firNew) or (secOld != secNew):
      firOld = firNew
      secOld = secNew
      self.iterate()
      firNew = self.myControl
      secNew = self.hisControl

  def __str__(self):
    return str(self.map)

  def getMyControl(self):
    return self.myControl

  def getHisControl(self):
    return self.hisControl

  def getIsolated(self):
    return False

  def getDraw(self):
    return False

class Move:
  def __init__(self, direction):
    self.direction  = direction
    self.hismoves   = []
    self.distances  = {}
    self.controlmy  = {}
    self.controlhis = {}
    self.draw       = {}
    self.isolated   = {}
    self.clashes    = {}
    self.scores     = None

  def __str__(self):
    to_return  = "Direction:      %s" % self.direction
    to_return += "\nDistances:      %s" % " ".join([ "%s=%s" % (key, self.distances[key]) for key in self.distances])
    to_return += "\nMy control:     %s" % " ".join([ "%s=%s" % (key, self.controlmy[key]) for key in self.controlmy])
    to_return += "\nHis control:    %s" % " ".join([ "%s=%s" % (key, self.controlhis[key]) for key in self.controlhis])
    to_return += "\nDraws:          %s" % " ".join([ "%s=%s" % (key, self.draw[key]) for key in self.draw])
    to_return += "\nIsolated:       %s" % " ".join([ "%s=%s" % (key, self.isolated[key]) for key in self.isolated])
    to_return += "\nClashes:        %s" % " ".join([ "%s=%s" % (key, self.clashes[key]) for key in self.clashes])

    return to_return

  def setDistance(self, distance, oppmove):
    self.distances[oppmove] = distance

  def setMyControl(self, control, oppmove):
    self.controlmy[oppmove] = control

  def setHisControl(self, control, oppmove):
    self.controlhis[oppmove] = control

  def setIsolated(self, value, oppmove):
    self.isolated[oppmove] = value

  def setDraw(self, value, oppmove):
    self.draw[oppmove] = value

  def addHisMove(self, move):
    self.hismoves.append(move)

  def getMinimumScore(self):
    if self.scores is None:
      self.scores = [ self.controlmy[key] - self.controlhis[key] for key in self.hismoves ]
    return min(self.scores)

  def getMaximumScore(self):
    scores = [ self.controlmy[key] - self.controlhis[key] for key in self.hismoves ]
    return max(self.scores)

  def getMaximumDistance(self):
    return max([ self.distances[key] for key in self.hismoves ])

  def getMinimumDistance(self):
    return min([ self.distances[key] for key in self.hismoves ])

  def getAverageScore(self):
    if self.scores is None:
      self.scores = [ self.controlmy[key] - self.controlhis[key] for key in self.hismoves ]
    return   float(sum(self.scores)) / len(self.scores)

class movList:
  def __init__(self):
    self.moves = {}

  def heLost(self):
    return (True in [ len(self.moves[move].hismoves) == 0 for move in self.moves ])

  def addMove(self, move):
    self.moves[move.direction] = move

  def getMinimums(self):
    to_return = {}
    for move in self.moves:
      to_return[move] = self.moves[move].getMinimumScore()

    return to_return

  def getMaximums(self):
    to_return = {}
    for move in self.moves:
      to_return[move] = self.moves[move].getMaximumScore()

    return to_return

  def pruneMax(self, criteria):
    histoGram = {}
    for move in self.moves:
      if    criteria == "max":
        value = self.moves[move].getMaximumScore()
      elif  criteria == "dis":
        value = self.moves[move].getMaximumDistance()
      elif  criteria == "avg":
        value = self.moves[move].getAverageScore()
      elif  criteria == "min":
        value = self.moves[move].getMinimumScore()

      if not histoGram.has_key(value):
        histoGram[value] = {}

      histoGram[value][move] = self.moves[move]

    self.moves = histoGram[max(histoGram)]

  def randomChoice(self):
    choice = random.choice(self.moves.keys())
    return self.moves[choice]

  def pruneMin(self, criteria):
    histoGram = {}
    for move in self.moves:
      if    criteria == "max":
        value = self.moves[move].getMaximumScore()
      elif  criteria == "dis":
        value = self.moves[move].getMinimumDistance()
      elif  criteria == "avg":
        value = self.moves[move].getAverageScore()
      elif  criteria == "min":
        value = self.moves[move].getMinimumScore()

      if not histoGram.has_key(value):
        histoGram[value] = {}

      histoGram[value][move] = self.moves[move]

    self.moves = histoGram[min(histoGram)]

def decision(movList):
  if not movList.heLost():
    minimums = movList.getMinimums()
    maximin = max(minimums.values())

    if maximin < 0: # we are losing
      movList.pruneMax("max")
      movList.pruneMin("dis")
      movList.pruneMax("avg")
      movList.pruneMax("max")
    else: # we are drawing or winning
      movList.pruneMax("min")
      movList.pruneMin("dis")
      movList.pruneMax("avg")
      movList.pruneMax("max")

  return movList.randomChoice().direction


def which_move_new(board):
  myMap = Map(board)

  myMoves = board.moves()
  hisPossible = dict((dir, board.rel(dir, board.them())) for dir in tron.DIRECTIONS)
  hisMoves = [ dir for dir in hisPossible if board.passable(hisPossible[dir])]

  me = board.me()
  he = board.them()
  myCoords = Coords(me[0], me[1])
  hisCoords = Coords(he[0], he[1])

  moveInstances = movList()

  for myMove in myMoves:
    startCoordsMy  = myCoords.neigh(myMove)

    move = Move(myMove)
    move.setDistance(startCoordsMy.distance(hisCoords), "start")

    for hisMove in hisMoves:
      startCoordsHis = hisCoords.neigh(hisMove)
      move.setDistance(startCoordsHis.distance(startCoordsMy), hisMove)
      move.addHisMove(hisMove)

      filler = Filler(myMap)
      filler.start(startCoordsMy, startCoordsHis)
      filler.fill()
      move.setMyControl(filler.getMyControl(), hisMove)
      move.setHisControl(filler.getHisControl(), hisMove)
      move.setIsolated(filler.getIsolated(), hisMove)
      move.setDraw(startCoordsHis == startCoordsMy, hisMove)

    moveInstances.addMove(move)

#  for move in moveInstances.moves.values():
#    print move
#    print "=" * 80

  return decision(moveInstances)


#def which_move(board):

#        while (myOld != myNew) or (hisOld != hisNew):
#          myOld = myNew
#          hisOld = hisNew
#          filler.iterate()
#          myNew = filler.myControl
#          hisNew = filler.hisControl

#        score = myNew - hisNew
#        scoreBoard[myMove] = min(scoreBoard[myMove], score)

#    maxScore = max(scoreBoard.values())
#    choices = []
#    for choice in scoreBoard:
#      if scoreBoard[choice] == maxScore:
#        choices.append(choice)
#
#    minimal = 9999
#    to_return = None
#    for choice in choices:
#      if distances[choice] < minimal:
#        minimal = distances[choice]
#        to_return = choice
#
#    return to_return

# you do not need to modify this part
for board in tron.Board.generate():
  tron.move(which_move_new(board))
