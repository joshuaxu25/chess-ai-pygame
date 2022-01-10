

class GameState:
    def __init__(self):
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]]
        self.moveFunctions = {'P': self.getPawnMoves, 'R': self.getRookMoves, 'N': self.getKnightMoves,
                              'B': self.getBishopMoves, 'Q': self.getQueenMoves, 'K': self.getKingMoves}

        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.checkmate = False
        self.statemate = False
        self.castlingPossible = Castling(True, True, True, True)
        self.castlingLog = [Castling(self.castlingPossible.wks, self.castlingPossible.wqs,
                                     self.castlingPossible.bks, self.castlingPossible.bqs)]

        self.checked = False
        self.pins = []
        self.checks = []

    def makeMove(self, move):
        if move.enPassantPossible:
            self.board[move.startRow][move.startCol] = "--"
            self.board[move.endRow][move.endCol] = move.pieceMoved
            self.board[move.startRow][move.endCol] = "--"

        else:
            self.board[move.startRow][move.startCol] = "--"
            self.board[move.endRow][move.endCol] = move.pieceMoved

        if move.pieceMoved[1] == "K":
            if self.whiteToMove:
                self.whiteKingLocation = (move.endRow, move.endCol)
            else:
                self.blackKingLocation = (move.endRow, move.endCol)

        # NEED TO CHANGE THE PAWN PROMOTION TO ANY PIECE THEY WANT
        if move.promotePawn:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + "Q"

        if move.isCastleMove:
            if move.endCol - move.startCol == 2:  # King Side Castle
                self.board[move.endRow][move.endCol - 1] = self.board[move.endRow][move.endCol + 1]
                self.board[move.endRow][move.endCol + 1] = "--"
            elif move.endCol - move.startCol == -2:  # Queen Side Castle
                self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 2]
                self.board[move.endRow][move.endCol - 2] = "--"

        self.updateCastleRights(move)  # PROBLEM HERE
        self.castlingLog.append(Castling(self.castlingPossible.wks, self.castlingPossible.wqs,
                                     self.castlingPossible.bks, self.castlingPossible.bqs))

        self.moveLog.append(move)
        self.whiteToMove = not self.whiteToMove

    def undoMove(self):
        if len(self.moveLog) != 0:
            lastMove = self.moveLog.pop()
            if lastMove.enPassantPossible:
                if self.whiteToMove:
                    self.board[lastMove.endRow - 1][lastMove.endCol] = "wP"
                else:
                    self.board[lastMove.endRow + 1][lastMove.endCol] = "bP"
                self.enPassantLastMove = False

            self.board[lastMove.startRow][lastMove.startCol] = lastMove.pieceMoved
            self.board[lastMove.endRow][lastMove.endCol] = lastMove.pieceCaptured
            self.whiteToMove = not self.whiteToMove

            if lastMove.pieceMoved[1] == "K":
                if self.whiteToMove:
                    self.whiteKingLocation = (lastMove.startRow, lastMove.startCol)
                else:
                    self.blackKingLocation = (lastMove.startRow, lastMove.startCol)

            self.castlingLog.pop()
            # PROBLEM WITH CASTLING WAS HERE. INSTEAD OF CALLING THE VARIABLE, I HAD TO CALL ITS INSTANCES.
            self.castlingPossible.wks = self.castlingLog[-1].wks
            self.castlingPossible.wqs = self.castlingLog[-1].wqs
            self.castlingPossible.bks = self.castlingLog[-1].bks
            self.castlingPossible.bqs = self.castlingLog[-1].bqs

            if lastMove.isCastleMove:
                if lastMove.endCol - lastMove.startCol == 2:
                    self.board[lastMove.endRow][lastMove.endCol + 1] = self.board[lastMove.endRow][lastMove.endCol - 1]
                    self.board[lastMove.endRow][lastMove.endCol - 1] = "--"
                elif lastMove.endCol - lastMove.startCol == -2:
                    self.board[lastMove.endRow][lastMove.endCol - 2] = self.board[lastMove.endRow][lastMove.endCol + 1]
                    self.board[lastMove.endRow][lastMove.endCol + 1] = "--"

    def updateCastleRights(self, move):
        if move.pieceMoved == "wK":
            self.castlingPossible.wqs = False
            self.castlingPossible.wks = False
        elif move.pieceMoved == "bK":
            self.castlingPossible.bqs = False
            self.castlingPossible.bks = False

        elif move.pieceMoved == "wR":
            if move.startRow == 7:
                if move.startCol == 7:
                    self.castlingPossible.wks = False
                elif move.startCol == 0:
                    self.castlingPossible.wqs = False
        elif move.pieceMoved == "bR":
            if move.startRow == 0:
                if move.startCol == 7:
                    self.castlingPossible.bks = False
                elif move.startCol == 0:
                    self.castlingPossible.bqs = False

    def getAllValidMoves(self):
        self.pins, self.checks, self.checked = self.checkForPinsAndChecks()
        possibleMoves = []

        if self.whiteToMove:
            myKingRow = self.whiteKingLocation[0]
            myKingCol = self.whiteKingLocation[1]
        else:
            myKingRow = self.blackKingLocation[0]
            myKingCol = self.blackKingLocation[1]

        if self.checked:
            if len(self.checks) == 1:
                # The following are possible moves when checked
                # 1) Capture the atk piece
                # 2) Move the king
                # 3) Move one of your piece in-between the king and the atk piece (CANNOT IF ATK PIECE IS A KNIGHT)
                check = self.checks[0]

                atkPieceRow = check[0]
                atkPieceCol = check[1]
                atkPiece = self.board[atkPieceRow][atkPieceCol]
                possibleMoves = self.getAllPossibleMoves()  # NEED TO PUT THIS BELOW THE "check" because otherwise the self.checks variable gets changed
                validSquares = []  # Valid squares that a piece can be moved to

                if atkPiece[1] == "N":
                    validSquares.append((atkPieceRow, atkPieceCol))  # Position of the atk piece is a valid square

                # Note : Any square that is in-between the king and the atk piece is a valid square
                else:
                    for i in range(1, 8):
                        validSquare = (myKingRow + check[2] * i, myKingCol + check[3] * i)
                        validSquares.append(validSquare)  # Square is valid until we hit the atk piece included
                        if validSquare == (atkPieceRow, atkPieceCol):
                            break

                for i in range(len(possibleMoves) - 1, -1, -1):
                    if possibleMoves[i].pieceMoved[1] != "K":
                        if not (possibleMoves[i].endRow, possibleMoves[i].endCol) in validSquares:
                            possibleMoves.remove(possibleMoves[i])

            else:  # If there is more than 1 check, need to move the king:
                self.getKingMoves(myKingRow, myKingCol, possibleMoves)

        else:  # No checks so all possible moves are valid
            possibleMoves = self.getAllPossibleMoves()

        if len(possibleMoves) == 0:
            if self.checked:
                self.checkmate = True

            else:
                self.stalemate = True

        else:
            self.checkmate = False
            self.stalemate = False

        return possibleMoves

    def checkForPinsAndChecks(self):
        pins = []
        checks = []
        checked = False

        if self.whiteToMove:
            enemyColor = "b"
            myColor = "w"
            startRow = self.whiteKingLocation[0]
            startCol = self.whiteKingLocation[1]
        else:
            enemyColor = "w"
            myColor = "b"
            startRow = self.blackKingLocation[0]
            startCol = self.blackKingLocation[1]
        directions = ((-1, 0), (1, 0), (0, -1), (0, 1), (1, 1), (1, -1), (-1, -1), (-1, 1))
        for d in directions:  # Look for checks in all directions starting from the king's position
            possiblePin = ()  # has the format (PinRow, PinCol, DirectionRow, DirectionCol)
            index = directions.index(d)
            for i in range(1, 8):
                endRow = startRow + d[0] * i
                endCol = startCol + d[1] * i
                if 0 <= endRow <= 7 and 0 <= endCol <= 7:
                    piece = self.board[endRow][endCol]
                    if piece[0] == myColor and piece[1] != 'K':
                        if possiblePin == ():  # If 1st ally piece encountered, then it is a possible pin
                            possiblePin = (endRow, endCol, d[0], d[1])
                        else:
                            break
                    elif piece[0] == enemyColor:  # Possible pins and checks
                        # Check for different type of pieces
                        type = piece[1]
                        if (type == "R" and 0 <= index <= 3) or (type == "B" and 4 <= index <= 7) \
                            or (type == "Q") or (type == "K" and i == 1)  \
                            or (type == "P" and i == 1 and ((myColor == "b" and 4 <= index <= 5)
                            or (myColor == "w" and 6 <= index <= 7))):
                                if possiblePin == ():  # If no pins, then it is a check
                                    checked = True
                                    checks.append((endRow, endCol, d[0], d[1]))
                                    break
                                else:  # If there is an ally piece in between ---> There is a pin
                                    pins.append((possiblePin[0], possiblePin[1], d[0], d[1]))
                                    break
                        else:
                            break
                else:
                    break

        #  Look for knight checks
        knightDirections = ((-1, 2), (1, 2), (-1, -2), (1, -2), (2, -1), (2, 1), (-2, 1), (-2, -1))
        for k in knightDirections:
            endRow = startRow + k[0]
            endCol = startCol + k[1]
            if 0 <= endRow <= 7 and 0 <= endCol <= 7:
                piece = self.board[endRow][endCol]
                if piece[0] == enemyColor and piece[1] == "N":
                    checked = True
                    checks.append((endRow, endCol, k[0], k[1]))

        return pins, checks, checked

    def getAllPossibleMoves(self):
        possibleMoves = []
        for row in range(len(self.board)):
            for column in range(len(self.board[row])):
                turn = self.board[row][column][0]
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[row][column][1]
                    self.moveFunctions[piece](row, column, possibleMoves)
        return possibleMoves

    def getPawnMoves(self, r, c, moves):
        if self.whiteToMove:
            kingRow, kingCol = self.whiteKingLocation
        else:
            kingRow, kingCol = self.blackKingLocation

        pinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                pinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        if self.whiteToMove:
            if self.board[r - 1][c] == "--":  # If no piece in front of white pawn
                if not pinned or pinDirection == (-1, 0): # Pawn can move in the direction of the pin
                    moves.append(Move((r, c), (r - 1, c), self.board, enPassant=False))
                    if r == 6:
                        if self.board[r - 2][c] == "--":  # If white pawn is in starting position
                            moves.append(Move((r, c), (r - 2, c), self.board, enPassant=False))
            if c - 1 >= 0:  # Capturing to the left
                if not pinned or pinDirection == (-1, -1):
                    if self.board[r - 1][c - 1][0] == "b":
                        moves.append(Move((r, c), (r - 1, c - 1), self.board, enPassant=False))
            if c + 1 <= 7:  # Capturing to the right
                if not pinned or pinDirection == (-1, 1):
                    if self.board[r - 1][c + 1][0] == "b":
                        moves.append(Move((r, c), (r - 1, c + 1), self.board, enPassant=False))

            # En Passant Rule White Pawn
            if r == 3:
                adjacentDirections = ((0, 1), (0, -1))
                lastMove = self.moveLog[-1]
                for d in adjacentDirections:
                    endCol = c + d[1]
                    if 0 <= endCol <= 7 and self.board[r][endCol][1] == "P":
                        if not pinned or (d == adjacentDirections[0] and pinDirection == (-1, 1)) or \
                                (d == adjacentDirections[1] and pinDirection == (-1, -1)):
                            if lastMove.pieceMoved == "bP" and lastMove.startCol == endCol and lastMove.startRow == 1:
                                if kingRow == r:
                                    attackingPiece = False
                                    blockingPiece = False
                                    if kingCol < c:  # King is to the left of the pawn.
                                        insideRange = range(kingCol + 1, endCol)  # Need to check for a piece in between.
                                        outsideRange = range(endCol + 1, 8)  # Need to check for a piece to the left.
                                    elif kingCol > c:
                                        insideRange = range(endCol + 1, kingCol, -1)  # Need to check for a piece in between.
                                        outsideRange = range(0, endCol, -1)  # Need to check for a piece to the right.
                                    for i in insideRange:
                                        if self.board[r][i] != '--':
                                            blockingPiece = True
                                            break
                                    for i in outsideRange:
                                        if self.board[r][i][0] == 'b' and (self.board[r][i][1] == 'R' or self.board[r][i][1] == 'Q'):
                                            attackingPiece = True
                                            break
                                        elif self.board[r][i] != '--':
                                            blockingPiece = True
                                            break
                                    if blockingPiece or not attackingPiece:
                                        print(blockingPiece)
                                        print(attackingPiece)
                                        moves.append(Move((r, c), (r - 1, endCol), self.board, enPassant=True))

        else:
            if self.board[r + 1][c] == "--":  # If no piece in front of black pawn
                if not pinned or pinDirection == (1, 0): # Pawn can move in the direction of the pin
                    moves.append(Move((r, c), (r + 1, c), self.board, enPassant=False))
                    if r == 1:
                        if self.board[r + 2][c] == "--":  # If black pawn is in starting position
                            moves.append(Move((r, c), (r + 2, c), self.board, enPassant=False))
            if c - 1 >= 0:  # Capturing to the left
                if not pinned or pinDirection == (1, -1):
                    if self.board[r + 1][c - 1][0] == "w":
                        moves.append(Move((r, c), (r + 1, c - 1), self.board, enPassant=False))
            if c + 1 <= 7:  # Capturing to the right
                if not pinned or pinDirection == (1, 1):
                    if self.board[r + 1][c + 1][0] == "w":
                        moves.append(Move((r, c), (r + 1, c + 1), self.board, enPassant=False))

            # En Passant Rule Black Pawn
            if r == 4:
                adjacentDirections = ((0, 1), (0, -1))
                lastMove = self.moveLog[-1]
                for d in adjacentDirections:
                    endCol = c + d[1]
                    if 0 <= endCol <= 7 and self.board[r][endCol][1] == "P":
                        if not pinned or (d == adjacentDirections[0] and pinDirection == (1, 1)) or \
                                (d == adjacentDirections[1] and pinDirection == (1, -1)):
                            if lastMove.pieceMoved == "wP" and lastMove.startCol == endCol and lastMove.startRow == 6:
                                if kingRow == r:
                                    attackingPiece = False
                                    blockingPiece = False
                                    if kingCol < c: # King is to the left of the pawn.
                                        insideRange = range(kingCol + 1, endCol)  # Need to check for a piece in between.
                                        outsideRange = range(endCol + 1, 8)  # Need to check for a piece to the right.
                                    elif kingCol > c:
                                        insideRange = range(endCol + 1, kingCol, -1)  # Need to check for a piece in between.
                                        outsideRange = range(0, endCol, -1)  # Need to check for a piece to the left.
                                    for i in insideRange:
                                        if self.board[r][i] != '--':
                                            blockingPiece = True
                                    for i in outsideRange:
                                        if self.board[r][i][0] == 'b':
                                            blockingPiece = True
                                            break
                                        elif self.board[r][i][0] == 'w' and (self.board[r][i][1] == 'R' or self.board[r][i][1] == 'Q'):
                                            attackingPiece = True
                                            break
                                    if blockingPiece:
                                        moves.append(Move((r, c), (r + 1, endCol), self.board, enPassant=True))
                                    else:
                                        if not attackingPiece:
                                            moves.append(Move((r, c), (r + 1, endCol), self.board, enPassant=True))


    def getRookMoves(self, r, c, moves):
        pinned = False
        pinDirection = ()


        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                pinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                if self.board[self.pins[i][0]][self.pins[i][1]][1] != "Q":
                    # Since we are calling the rook function first in the queen function, we only want to remove the
                    # queen pin after calling the bishop function.

                    self.pins.remove(self.pins[i])
                break

        directions = ((-1, 0), (0, 1), (1, 0), (0, -1))
        enemyColor = "b" if self.whiteToMove else "w"

        for d in directions:
            if not pinned or pinDirection == (d[0], d[1]) or pinDirection == (-d[0], -d[1]):
                for i in range(1, 8):
                    endR = r + (d[0] * i)
                    endC = c + (d[1] * i)
                    if 0 <= endR <= 7 and 0 <= endC <= 7:
                        enemyPiece = self.board[endR][endC]
                        if enemyPiece == "--":
                            moves.append(Move((r, c), (endR, endC), self.board))
                        elif enemyPiece[0] == enemyColor:
                            moves.append(Move((r, c), (endR, endC), self.board))
                            break
                        else:
                            break
                    else:
                        break

    def getKnightMoves(self, r, c, moves):
        pinned = False
        pinDirection = ()

        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                pinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        directions = ((-2, 1), (-2, -1), (2, -1), (2, 1), (1, 2), (-1, 2), (1, -2), (-1, -2))
        myColor = "w" if self.whiteToMove else "b"

        for d in directions:
            endR = r + d[0]
            endC = c + d[1]
            if 0 <= endR <= 7 and 0 <= endC <= 7:
                if not pinned:
                    enemyPiece = self.board[endR][endC]
                    if enemyPiece[0] != myColor:
                        moves.append(Move((r, c), (endR, endC), self.board))

    def getBishopMoves(self, r, c, moves):
        pinned = False
        pinDirection = ()

        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                pinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        directions = ((-1, 1), (1, 1), (1, -1), (-1, -1))
        enemyColor = "b" if self.whiteToMove else "w"

        for d in directions:
            if not pinned or pinDirection == (d[0], d[1]) or pinDirection == (-d[0], -d[1]):
                for i in range(1, 8):
                    endR = r + (d[0] * i)
                    endC = c + (d[1] * i)
                    if 0 <= endR <= 7 and 0 <= endC <= 7:
                        enemyPiece = self.board[endR][endC]
                        if enemyPiece == "--":
                            moves.append(Move((r, c), (endR, endC), self.board))
                        elif enemyPiece[0] == enemyColor:
                            moves.append(Move((r, c), (endR, endC), self.board))
                            break
                        else:
                            break
                    else:
                        break

    def getQueenMoves(self, r, c, moves):
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)

    def getKingMoves(self, r, c, moves):
        directions = ((-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1))
        myColor = "w" if self.whiteToMove else "b"

        for d in directions:
            endR = r + d[0]
            endC = c + d[1]
            if 0 <= endR <= 7 and 0 <= endC <= 7:
                enemyPiece = self.board[endR][endC]
                if enemyPiece[0] != myColor:
                    if self.whiteToMove:  # Make the move and see if it gets checked
                        self.whiteKingLocation = (endR, endC)
                    else:
                        self.blackKingLocation = (endR, endC)

                    pins, checks, checked = self.checkForPinsAndChecks()
                    if not checked:
                        moves.append(Move((r, c), (endR, endC), self.board))

                    if self.whiteToMove:
                        self.whiteKingLocation = (r, c)
                    else:
                        self.blackKingLocation = (r, c)

        self.getCastleMoves(r, c, moves, myColor)

    def getCastleMoves(self, r, c, moves, allyColor):
        pins, checks, checked = self.checkForPinsAndChecks()

        if checked:
            return
        else:
            self.getKingSideCastle(r, c, moves, allyColor)
            self.getQueenSideCastle(r, c, moves, allyColor)

    def getKingSideCastle(self, r, c, moves, allyColor):
        # Check for squares on Col(5, 6)
        kingsidePossible = True

        if allyColor == "w":
            if self.castlingPossible.wks:
                for i in range(1, 3):
                    endCol = c + i
                    if 5 <= endCol <= 6:
                        self.whiteKingLocation = (r, endCol)
                        pins, checks, checked = self.checkForPinsAndChecks()
                        self.whiteKingLocation = (r, c)
                        if self.board[r][endCol] != "--" or checked:
                            kingsidePossible = False
                            break
                if kingsidePossible:
                    moves.append(Move((r, c), (r, c + 2), self.board, isCastleMove=True))
        elif allyColor == "b":
            if self.castlingPossible.bks:
                for i in range(1, 3):
                    endCol = c + i
                    if 5 <= endCol <= 6:
                        self.blackKingLocation = (r, endCol)
                        pins, checks, checked = self.checkForPinsAndChecks()
                        self.blackKingLocation = (r, c)
                        if self.board[r][endCol] != "--" or checked:
                            kingsidePossible = False
                            break
                if kingsidePossible:
                    moves.append(Move((r, c), (r, c + 2), self.board, isCastleMove=True))

    def getQueenSideCastle(self, r, c, moves, allyColor):
        # Check for squares on Col (1, 2, 3)
        queensidePossible = True

        if allyColor == "w":
            if self.castlingPossible.wqs:
                for i in range(1, 4):
                    endCol = c - i
                    if 1 <= endCol <= 3:
                        self.whiteKingLocation = (r, endCol)
                        pins, checks, checked = self.checkForPinsAndChecks()
                        self.whiteKingLocation = (r, c)
                        if self.board[r][endCol] != "--" or (checked and 1 <= i <= 2):
                            queensidePossible = False
                            break
                if queensidePossible:
                    moves.append(Move((r, c), (r, c - 2), self.board, isCastleMove=True))
        elif allyColor == "b":
            if self.castlingPossible.bqs:
                for i in range(1, 4):
                    endCol = c - i
                    if 1 <= endCol <= 3:
                        self.blackKingLocation = (r, endCol)
                        pins, checks, checked = self.checkForPinsAndChecks()
                        self.blackKingLocation = (r, c)
                        if self.board[r][endCol] != "--" or (checked and 1 <= i <= 2):
                            queensidePossible = False
                            break
                if queensidePossible:
                    moves.append(Move((r, c), (r, c - 2), self.board, isCastleMove=True))

class Castling:
    def __init__(self, wks, wqs, bks, bqs):
        self.wks = wks
        self.wqs = wqs
        self.bks = bks
        self.bqs = bqs


class Move:
    # Maps from keys to values
    # Keys : Values

    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4,
                   "5": 3, "6": 2, "7": 1, "8": 0}

    rowToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"A": 0, "B": 1, "C": 2, "D": 3,
                   "E": 4, "F": 5, "G": 6, "H": 7}

    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSquare, endSquare, board, enPassant=False, isCastleMove=False):
        self.startRow = startSquare[0]
        self.startCol = startSquare[1]
        self.endRow = endSquare[0]
        self.endCol = endSquare[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.moveID = (self.startRow * 1000) + (self.startCol * 100) + (self.endRow * 10) + self.endCol
        self.promotePawn = (self.pieceMoved == "wP" and self.endRow == 0) or (self.pieceMoved == "bP" and self.endRow == 7)
        self.enPassantPossible = enPassant
        self.isCastleMove = isCastleMove


    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        else:
            return False


    def getChessNotation(self):
        if self.isCastleMove:
            return "O-O" if self.endCol == 6 else "O-O-O"
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)


    def getRankFile(self, row, col):
        return self.colsToFiles[col] + self.rowToRanks[row]

