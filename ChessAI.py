import pygame as p
import ChessEngine
import ChessML

# Variables
screenWidth = screenHeight = windowHeight = 512
windowWidth = 800
dimension = 8
squareSize = screenHeight // dimension
fps = 5
images = {}
padding = 10
paddingText = 3


def loadImages():
    pieces = ["bB", "bK", "bN", "bP", "bQ", "bR", "wB", "wK", "wN", "wP", "wQ", "wR"]
    for piece in pieces:
        images[piece] = p.transform.scale(p.image.load('images/' + piece + '.png'), (squareSize, squareSize))


def main():
    p.init()  # Initializes the game
    p.display.set_caption("Chess AI")  # Set title
    screen = p.display.set_mode((windowWidth, windowHeight))  # Set screen size
    clock = p.time.Clock()  # Sets clock for the game
    screen.fill((47, 79, 79))  # Background Fill
    gs = ChessEngine.GameState()   # Access the game state
    loadImages()  # Set the images

    validMoves = gs.getAllValidMoves()  # Generates all valid moves
    moveMade = False  # Flag variable for when a valid move is made
    gameOver = False
    run = True
    squareSelected = ()
    playerClicks = []  # List of tuple
    # s of squareSelected
    clicked = False
    isBlackPlayer = False  # True if black is player. False if black is computer.
    isWhitePlayer = True  # True if white is player. False if white is computer.

    while run:
        displayMoveLog(screen, gs.moveLog)
        playerTurn = (isBlackPlayer and not gs.whiteToMove) or (isWhitePlayer and gs.whiteToMove)
        for e in p.event.get():
            if e.type == p.QUIT:
                run = False
                p.quit()
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver and playerTurn:
                    location = p.mouse.get_pos()
                    if location[0] <= screenWidth:
                        col = location[0] // squareSize
                        row = location[1] // squareSize
                        clicked = True
                        if squareSelected == (row, col):  # If player clicks the same square twice
                            squareSelected = ()
                            playerClicks = []  # Un-select the square
                            clicked = False
                        else:
                            squareSelected = (row, col)
                            playerClicks.append(squareSelected)
                        if len(playerClicks) == 2:  # Second click
                            move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)  # Create an object move
                            print(move.getChessNotation())  # Print the move
                            for i in range(len(validMoves)):
                                if move == validMoves[i]:
                                    move.enPassantPossible = validMoves[i].enPassantPossible
                                    move.isCastleMove = validMoves[i].isCastleMove
                                    """if move.promotePawn:
                                        not_promoted = True
                                        while not_promoted:
                                            p.draw.rect(screen, "red", p.Rect(50, 50, 50, 50))
                                            for f in p.event.get():
                                                if f.type == p.KEYDOWN:
                                                    if f.key == p.K_b:
                                                        not_promoted = False
                                            p.display.flip()
                                        gs.makeMove(move, "N")
                                    else:"""
                                    animate = True
                                    gs.makeMove(move)  # Make the move
                                    moveMade = True  # Move has been made
                                    squareSelected = ()  # Reset for the next move
                                    playerClicks = []  # Reset for the next move
                                    clicked = False
                            if not moveMade:
                                playerClicks = [squareSelected]
                    p.display.flip()
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:
                    gs.undoMove()
                    animate = False
                    moveMade = True
                    gameOver = False
        # AI Moves
        if not gameOver and not playerTurn:
            computerMove = ChessML.findBestMove(gs, validMoves)
            gs.makeMove(computerMove)
            moveMade = True
            animate = True

        if moveMade:
            if animate:
                animate_moves(screen, gs.board, gs.moveLog[-1], clock)
            validMoves = gs.getAllValidMoves()  # Generate new moves if a move is made
            moveMade = False

        drawGameState(screen, gs)
        # Highlight the square of the selected piece and its valid moves
        if clicked:
            p.draw.rect(screen, (255, 0, 0),
                        ((col * squareSize) + 1, (row * squareSize) + 1, squareSize - 3, squareSize - 3), 4)
            for i in validMoves:
                if i.startRow == squareSelected[0] and i.startCol == squareSelected[1]:
                    p.draw.rect(screen, (0, 128, 0),
                                ((i.endCol * squareSize) + 1, (i.endRow * squareSize) + 1, squareSize - 3, squareSize - 3), 4)

        if gs.checkmate:
            gameOver = True
            if gs.whiteToMove:
                writeText(screen, "Black wins by checkmate")
            else:
                writeText(screen, "White wins by checkmate")
        elif gs.stalemate:
            gameOver = True
            writeText(screen, "Stalemate")

        clock.tick(fps)
        p.display.flip()


def writeText(screen, text):
    font = p.font.SysFont(text, 40, True, False)
    textObject = font.render(text, 0, p.Color("White"))
    textLocation = p.Rect(0, 0, screenWidth, screenHeight).move(
        screenWidth/2 - textObject.get_width()/2, screenHeight/2 - textObject.get_height()/3)
    screen.blit(textObject, textLocation)
    textObject = font.render(text, 0, p.Color("Black"))
    screen.blit(textObject, textLocation.move(2, 2))


def drawGameState(screen, gs):
    drawBoard(screen)  # Draw the board
    drawPieces(screen, gs.board)
    displayMoveLog(screen, gs.moveLog)


def drawBoard(screen):
    colors = [(255, 222, 173), (205, 133, 63)]

    for row in range(dimension):
        for column in range(dimension):
            color = colors[(row + column) % 2]
            p.draw.rect(screen, color, p.Rect(column * squareSize, row * squareSize, squareSize, squareSize))


def drawPieces(screen, board):
    for row in range(dimension):
        for column in range(dimension):
            piece = board[row][column]
            if piece != "--":
                screen.blit(images[piece], p.Rect(column * squareSize, row * squareSize, squareSize, squareSize))


def animate_moves(screen, board, move, clock):
    colors = [(255, 222, 173), (205, 133, 63)]
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    frameCount = (int(abs(dR) + abs(dC)**0.5))*fps
    for frame in range(frameCount + 1):
        r, c = (move.startRow + dR*frame/frameCount, move.startCol + dC*frame/frameCount)
        drawBoard(screen)
        drawPieces(screen, board)
        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = p.Rect(move.endCol*squareSize, move.endRow*squareSize, squareSize, squareSize)
        p.draw.rect(screen, color, endSquare)
        if move.pieceCaptured != '--':
            screen.blit(images[move.pieceCaptured], endSquare)
        screen.blit(images[move.pieceMoved], p.Rect(c*squareSize, r*squareSize, squareSize, squareSize))
        p.display.flip()
        clock.tick(60)

def displayMoveLog(screen, moveLog):
    edit = p.font.SysFont(None, 25, False, False)  # Font Initialization
    movesEdit = p.font.SysFont(None, 20, False, False)  # Font Initialization

    boxWidth = windowWidth - (screenWidth + 2*padding)
    boxHeight = windowHeight - 2*padding
    left = screenWidth + padding
    top = padding
    box = p.Rect(left, top, boxWidth, boxHeight)
    p.draw.rect(screen, "White", box, 2)

    text = "Move Log"
    textObject = edit.render(text, 0, p.Color("White"))
    location = p.Rect(screenWidth, 0, boxWidth, boxHeight).move((windowWidth - screenWidth)/2 -
                                                                textObject.get_width()/2, 2*padding)
    screen.blit(textObject, location)

    # Display moves
    moveTexts = moveLog
    moveTextX = 2.5*padding
    moveTextY = 0
    for i in range(len(moveLog)):
        if moveLog[i].pieceMoved[0] == "b":
            color = "Black"
        else:
            color = "White"
        text = moveLog[i].getChessNotation()
        notation = movesEdit.render(text, 0, p.Color(color))
        if moveTextY >= (windowHeight - 7*padding):
            moveTextY = 0
            moveTextX += notation.get_width() + 2*padding
        notationLocation = p.Rect(screenWidth, 4*padding, boxWidth, boxHeight).move(moveTextX, moveTextY)
        screen.blit(notation, notationLocation)
        moveTextY += 1.5*padding


if __name__ == "__main__":
    main()


