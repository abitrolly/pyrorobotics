"""
This module contains a class of a random Konane Player.
Parts are missing, and left as exercises for the reader.
"""

from pyro.brain import Brain
import time, random

class KonanePlayer(Brain):
    """
    A simple Random Konane Player. Note that the rep of board is
    zero-based, but all other places is one's based.
    For use with SymbolicSimulator and KonaneWorld.py and
    SymbolicPlayer.py

    Missing: it doesn't handle multiple jumps, and doesn't find them.
    """
    def setup(self):
        if self.robot.id == 0:
            self.myPiece = "O"
        else:
            self.myPiece = "X"
        self.firstMove = 1
        print "Welcome to Konane, Hawaiian Checkers!"
        print "Red indicates that it is that shapes move."
        print "Jumps must occur in a straight line."
        print "A human can play, or start two Pyro's up,"
        print "and connect onto two different ports using"
        print "SymbolicPlayer1 and SymbolicPlayer2."

    def step(self):
        if self.robot.whosMove != self.robot.id:
            time.sleep(1)
            return
        board = self.robot.getItem("board")
        moves = self.moveGenerator(board, self.myPiece, self.firstMove)
        self.firstMove = 0
        if len(moves) > 0:
            # Here is where you would go through the possible
            # moves and pick the best one.
            # I'm just going to pick a random one:
            move = moves[int(len(moves) * random.random())]
            if len(move) == 2: # remove the piece
                self.robot.play("remove(%d,%d)" % move)
                print "remove(%d,%d)" % move
                self.robot.play("done")
            elif len(move) == 4: # a single jump
                self.robot.play("jump(%d,%d,%d,%d)" % move)
                print "jump(%d,%d,%d,%d)" % move
                self.robot.play("done")
            else:
                pass # multi-jump handler; left to reader
        else:
            print "You win!"
            self.pleaseStop() # request to stop running brain

    def otherPiece(self, piece):
        """ What is the opponent's shape? """
        if piece == 'O': return 'X'
        else: return 'O'

    def getEmpties(self, board):
        """ Returns all of the empty positions on board. """
        retval = []
        for i in range(8):
            for j in range(8):
                if board[i][j] == '':
                    retval.append( (i+1, j+1) )
        return retval

    def add(self, pos, offset):
        """ Adds two board positions together """
        return (pos[0] + offset[0], pos[1] + offset[1])

    def validPos(self, pos, offset = (0,0)):
        """ Is this position + offset a valid board position?"""
        newx, newy = self.add(pos, offset)
        return (newx >= 1 and newx <= 8 and newy >= 1 and newy <= 8)

    def moveGenerator(self, board, myPiece, firstMove):
        """Generates legal board moves. Doesn't find multiple-jumps. """
        retval = []
        empties = self.getEmpties(board)
        if firstMove:
            if len(empties) == 0: # I'm first!
                if myPiece == "O":
                    retval.extend( [(4,4), (5,5), (1,1), (8,8)] )
                else:
                    retval.extend( [(5,4), (4,5), (1,8), (8,1)] )
            else: # I'm second
                # get one of the 4 (or less) surrounding pieces
                openPos = empties[0] # better be just one
                for i,j in [(-1,0), (+1,0), (0, -1), (0, +1)]:
                    if self.validPos(openPos, (i,j)):
                        retval.append( self.add(openPos, (i,j)) )
        else:
            # find all moves, and add them to list
            for i in range(1,9):
                for j in range(1,9):
                    if board[i-1][j-1] == myPiece:
                        for a,b in [(0, -2),(+2,-2), (+2, 0),(+2, +2),
                                    (0, +2),(-2, +2),(-2, 0),(-2, -2)]:
                            if self.validPos((i,j), (a,b)):
                                x,y = self.add((i,j),(a,b))
                                if board[x-1][y-1] == '':
                                    bx, by = self.add( (i,j), (x,y) )
                                    bx, by = bx/2, by/2
                                    if board[bx-1][by-1] == self.otherPiece(myPiece):
                                        retval.append( (i,j,x,y) )
                                        # jump some more? left to the reader
        return retval

def INIT(engine):
    return KonanePlayer("Random Konane Player", engine)
