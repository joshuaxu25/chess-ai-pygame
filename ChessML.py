# 1. Send the board here.
# 2. Divide the board into its pieces such that each board is only represented by said piece. The matrix
#    will be a 14 x 8 x 8 (6 different pieces + 1 board with the attacking squares).

import numpy as np
import random


points = {
          "P": 50,
          "B": 150,
          "N": 150,
          "R": 250,
          "Q": 450,
          "K": 5000
         }

reverse = {0: 7, 1: 6, 2: 5, 3: 4, 4: 3, 5: 2, 6: 1, 7: 0}

pawnTable = [[0,  0,  0,  0,  0,  0,  0,  0],
             [50, 50, 50, 50, 50, 50, 50, 50],
             [10, 10, 20, 30, 30, 20, 10, 10],
             [5,  5, 10, 27, 27, 10,  5,  5],
             [0,  0,  0, 25, 25,  0,  0,  0],
             [5, -5,-10,  0,  0, -10, -5,  5],
             [5, 10, 10,-25,-25, 10, 10,  5],
             [0,  0,  0,  0,  0,  0,  0,  0]]

knightTable = [[-50,-40,-30,-30,-30,-30,-40,-50],
               [-40,-20,  0,  0,  0,  0,-20,-40],
               [-30,  0, 10, 15, 15, 10,  0,-30],
               [-30,  5, 15, 20, 20, 15,  5,-30],
               [-30,  0, 15, 20, 20, 15,  0,-30],
               [-30,  5, 10, 15, 15, 10,  5,-30],
               [-40,-20,  0,  5,  5,  0,-20,-40],
               [-50,-40,-20,-30,-30,-20,-40,-50]]

bishopTable = [[-20,-10,-10,-10,-10,-10,-10,-20],
               [-10,  0,  0,  0,  0,  0,  0,-10],
               [-10,  0,  5, 10, 10,  5,  0,-10],
               [-10,  5,  5, 10, 10,  5,  5,-10],
               [-10,  0, 10, 10, 10, 10,  0,-10],
               [-10, 10, 10, 10, 10, 10, 10,-10],
               [-10,  5,  0,  0,  0,  0,  5,-10],
               [-20,-10,-40,-10,-10,-40,-10,-20]]

queenTable = [[-20, -10, -10, -5, -5, -10, -10, -20],
              [-10, 0, 0, 0, 0, 0, 0, -10],
              [-10, 0, 5, 5, 5, 5, 0, -10],
              [-5, 0, 5, 5, 5, 5, 0, -5],
              [0, 0, 5, 5, 5, 5, 0, -5],
              [-10, 5, 5, 5, 5, 5, 0, -10],
              [-10, 0, 5, 0, 0, 0, 0, -10],
              [-20, -10, -10, -5, -5, -10, -10, -20]]

rookTable = [[0, 0, 0, 0, 0, 0, 0, 0],
             [5, 10, 10, 10, 10, 10, 10, 5],
             [-5, 0, 0, 0, 0, 0, 0, -5],
             [-5, 0, 0, 0, 0, 0, 0, -5],
             [-5, 0, 0, 0, 0, 0, 0, -5],
             [-5, 0, 0, 0, 0, 0, 0, -5],
             [-5, 0, 0, 0, 0, 0, 0, -5],
             [0, 0, 0, 5, 5, 0, 0, 0]]

kingTableStart = [[-30, -40, -40, -50, -50, -40, -40, -30],
              [-30, -40, -40, -50, -50, -40, -40, -30],
              [-30, -40, -40, -50, -50, -40, -40, -30],
              [-30, -40, -40, -50, -50, -40, -40, -30],
              [-20, -30, -30, -40, -40, -30, -30, -20],
              [-10, -20, -20, -20, -20, -20, -20, -10],
              [20,  20,   0,   0,   0,   0,  20,  20],
              [20,  30,  10,   0,   0,  10,  30,  20]]

kingTableEnd = [[-50,-40,-30,-20,-20,-30,-40,-50],
                [-30,-20,-10,  0,  0,-10,-20,-30],
                [-30,-10, 20, 30, 30, 20,-10,-30],
                [-30,-10, 30, 40, 40, 30,-10,-30],
                [-30,-10, 30, 40, 40, 30,-10,-30],
                [-30,-10, 20, 30, 30, 20,-10,-30],
                [-30,-30,  0,  0,  0,  0,-30,-30],
                [-50,-30,-30,-30,-30,-30,-30,-50]]

piecesScoreDict = {"P": pawnTable,
                   "N": knightTable,
                   "B": bishopTable,
                   "R": rookTable,
                   "Q": queenTable,
                   "K": kingTableStart,
                   "KE": kingTableEnd}

ENDGAMEMAXPIECE = 10
DEPTH = 2
CHECKMATE = 10000
STALEMATE = 0


def findRandomMove(validMoves):
    return validMoves[random.randint(0, len(validMoves) - 1)]


def findBestMove(gs, validMoves):
    global nextMove
    random.shuffle(validMoves)
    findMoveNegamax(gs, validMoves, DEPTH, -np.inf, np.inf,  1 if gs.whiteToMove else -1)
    return nextMove


def findMoveNegamax(gs, validMoves, depth, alpha, beta, turn):
    global nextMove
    if depth == 0:
        return turn * scoreBoard(gs)

    bestScore = -np.inf
    for move in validMoves:
        gs.makeMove(move)
        nextMoves = gs.getAllValidMoves()
        score = -findMoveNegamax(gs, nextMoves, depth - 1, -beta, -alpha, -turn)
        if score > bestScore:
            bestScore = score
            if depth == DEPTH:
                nextMove = move
        gs.undoMove()
        alpha = max(alpha, bestScore)
        if alpha >= beta:
            break
    return bestScore


def scoreBoard(gs):
    if gs.checkmate:
        if gs.whiteToMove:
            return -CHECKMATE
        else:
            return CHECKMATE
    elif gs.stalemate:
        return STALEMATE

    score = 0
    pieceCounter = 0
    for row in range(len(gs.board)):
        for col in range(len(gs.board[row])):
            if gs.board[row][col] != '--':
                pieceCounter += 1

    for row in range(len(gs.board)):
        for col in range(len(gs.board[row])):
            piece = gs.board[row][col]
            if piece != '--':
                color = piece[0]
                type = piece[1]
                if gs.whiteToMove:
                    if pieceCounter <= ENDGAMEMAXPIECE and type == "K":
                        type = "KE"
                    positionScore = piecesScoreDict[type][row][col]
                else:
                    if pieceCounter <= ENDGAMEMAXPIECE and type == "K":
                        type = "KE"
                    positionScore = piecesScoreDict[type][::-1][row][col]
                if color == "w":
                    score += points[piece[1]] + positionScore
                elif color == "b":
                    score -= points[piece[1]] + positionScore
    return score

