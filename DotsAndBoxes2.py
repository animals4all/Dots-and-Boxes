#Dots and Boxes
#
#Connect dots to get the most territories

import pygame, sys, random
from pygame.locals import *

FPS = 30
WINDOWWIDTH = 600
WINDOWHEIGHT = 620

SPACESIZE = 70
FILLINGSIZE = 50
FILLINGMARGIN = int((SPACESIZE - FILLINGSIZE) / 2)

BOARDWIDTH = 8
BOARDHEIGHT = 7
BOARDPIXELWIDTH = BOARDWIDTH * SPACESIZE
BOARDPIXELHEIGHT = BOARDHEIGHT * SPACESIZE
BOARDMARGIN = int((WINDOWWIDTH - BOARDPIXELWIDTH) / 2)
BOARDRECT = pygame.Rect(BOARDMARGIN, BOARDMARGIN, BOARDPIXELWIDTH, BOARDPIXELHEIGHT)

LINEWIDTH = 1
FILLEDLINEWIDTH = 7

TURNCIRCLERADIUS = 10

PLAYER = "player"
COMPUTER = "computer"

DOTIMAGE = pygame.image.load("dot.png")
DOTIMAGEWIDTH = 15
DOTIMAGEHEIGHT = 15

ICONIMAGE = pygame.image.load("icon.png")

BGCOLOR = (10, 90, 75) # turquoise
BOARDCOLOR = (255, 255, 255) # white
LINECOLOR = (185, 185, 185) # light gray
FILLEDLINECOLOR = (0, 0, 0) # black
FONTCOLOR = (255, 255, 255) # white
FONTRECTCOLOR = (255, 190, 0) # yellow
TURNCIRCLECOLOR = (255, 255, 255) # white
HIGHLIGHTCOLOR = (50, 175, 70) # green
PLAYERCOLOR = (180, 20, 20) # red
COMPUTERCOLOR = (60, 5, 60) # purple

def main():
    global FPSCLOCK, DISPLAYSURF, FONT

    pygame.init()
    FPSCLOCK = pygame.time.Clock()

    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    pygame.display.set_caption("Dots and Boxes")
    pygame.display.set_icon(ICONIMAGE)
    
    FONT = pygame.font.Font("freesansbold.ttf", 36)

    while True:
        playAgain = runGame()
        if not playAgain:
            pygame.quit()
            sys.exit()

def runGame():
    # Run the game until there are no moves left to take
    playerScore, computerScore = 0, 0
    turn = PLAYER
    
    mouseX, mouseY = 0, 0
    firstDotClicked, secondDotClicked = None, None
    
    board = createBoard()

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
                
            elif event.type == MOUSEMOTION:
                mouseX, mouseY = event.pos
                
            elif event.type == MOUSEBUTTONUP:
                dotClicked = getDotAtPixel(mouseX, mouseY)
                
                if dotClicked and not firstDotClicked:
                    firstDotClicked = dotClicked
                    
                elif dotClicked and firstDotClicked and not secondDotClicked:
                    lineFilled = isLineFilled(board, firstDotClicked, dotClicked)
                    if dotsAdjacent(firstDotClicked, dotClicked) and not lineFilled:
                        secondDotClicked = dotClicked
                    else:
                        firstDotClicked, secondDotClicked = None, None
                        
                else:
                    firstDotClicked, secondDotClicked = None, None

        if firstDotClicked and secondDotClicked:
            fillLine(board, firstDotClicked, secondDotClicked)
            boxesFilled = fillBoxes(board, turn)
            firstDotClicked, secondDotClicked = None, None

            if boxesFilled == 0:
                if turn == PLAYER:
                    playerScore += boxesFilled
                    turn = COMPUTER
                else:
                    computerScore += boxesFilled
                    turn = PLAYER
                
        draw(board, firstDotClicked, playerScore, computerScore, turn)
        pygame.display.update()
        FPSCLOCK.tick(FPS)

        if isGameOver(board):
            if playerScore > computerScore:
                winner = PLAYER
            elif computerScore > playerScore:
                winner = COMPUTER
            else:
                winner = None
                
            return showGameOverScreen(winner)

def createBoard():
    # Create a board dict w/ keys containing space coords and values containing whether the box is f
    # illed or not, who owns the box, and a list containing the lines surrounding the box.
    
    board = {}
    
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
                board[(x, y)] = [False, None,
                                 [[((x,y), (x,y+1)), False],
                                  [((x,y), (x+1,y)), False],
                                  [((x+1,y), (x+1,y+1)), False],
                                  [((x+1,y+1), (x,y+1)), False]]]

    return board
    
def draw(board, dotToHighlight, playerScore, computerScore, turn):
    # Draw the background, dots, filled lines, score information, and filled boxes
    drawBackground()
    drawFilledBoxes(board)
    drawLines(board)
    drawDots(dotToHighlight)
    drawInfo(playerScore, computerScore, turn)

def drawBackground():
    # Fill the display and draw the board
    DISPLAYSURF.fill(BGCOLOR)
    pygame.draw.rect(DISPLAYSURF, BOARDCOLOR, BOARDRECT)
    for x in range(BOARDWIDTH + 1):
        for y in range(BOARDHEIGHT + 1):
            left, top = getLeftTopCoordsOfBox(x, y)
            pygame.draw.line(DISPLAYSURF,
                             LINECOLOR,
                             (BOARDMARGIN, top), (BOARDMARGIN + BOARDPIXELWIDTH, top),
                             LINEWIDTH)
            pygame.draw.line(DISPLAYSURF,
                             LINECOLOR,
                             (left, BOARDMARGIN), (left, BOARDMARGIN + BOARDPIXELHEIGHT),
                             LINEWIDTH)

def drawFilledBoxes(board):
    # Draw boxes that have been filled on the board
    for space in board:
        if board[space][0]:
            x, y = space[0], space[1]
            spaceLeft, spaceTop = getLeftTopCoordsOfBox(x, y)
            fillRect = pygame.Rect(spaceLeft + FILLINGMARGIN, spaceTop + FILLINGMARGIN,
                                   FILLINGSIZE, FILLINGSIZE)
            
            if board[space][1] == PLAYER:
                pygame.draw.rect(DISPLAYSURF, PLAYERCOLOR, fillRect)
            else:
                pygame.draw.rect(DISPLAYSURF, COMPUTERCOLOR, fillRect)
    
def drawLines(board):
    # Draw the filled lines on the board
    for space in board:
        for line in board[space][2]:
            if line[1]:
                lineX1, lineY1 = getLeftTopCoordsOfBox(line[0][0][0], line[0][0][1])
                lineX2, lineY2 = getLeftTopCoordsOfBox(line[0][1][0], line[0][1][1])
                pygame.draw.line(DISPLAYSURF, FILLEDLINECOLOR, (lineX1, lineY1),
                                 (lineX2, lineY2),
                                 FILLEDLINEWIDTH)
                
def drawDots(dotToHighlight):
    # Draw the dots on the board
    for x in range(BOARDWIDTH + 1):
        for y in range(BOARDHEIGHT + 1):
            dotLeft, dotTop = getLeftTopCoordsOfBox(x, y)
            dotX, dotY = dotLeft - int(DOTIMAGEWIDTH/2), dotTop - int(DOTIMAGEHEIGHT/2)
            DISPLAYSURF.blit(DOTIMAGE, (dotX, dotY))
            
            if dotToHighlight and dotToHighlight[0] == x and dotToHighlight[1] == y:
                highlightDot(dotLeft, dotTop)
                
def highlightDot(x, y):
    # Draw a highlight around a specified dot
    pygame.draw.circle(DISPLAYSURF, HIGHLIGHTCOLOR, (x, y), int(DOTIMAGEWIDTH / 2) + 2, 2)

def drawInfo(playerScore, computerScore, turn):
    # Draw the player's score and the computer's score
    playerText = "Player's score: " + str(playerScore)
    playerTextSurf = FONT.render(playerText, True, FONTCOLOR)
    playerTextRect = playerTextSurf.get_rect()
    playerTextRect.topleft = (BOARDMARGIN, BOARDPIXELHEIGHT + BOARDMARGIN + 20)

    computerText = "Computer's score: " + str(computerScore)
    computerTextSurf = FONT.render(computerText, True, FONTCOLOR)
    computerTextRect = computerTextSurf.get_rect()
    computerTextRect.topleft = (BOARDMARGIN, playerTextRect.bottom + 5)

    DISPLAYSURF.blit(playerTextSurf, playerTextRect)
    DISPLAYSURF.blit(computerTextSurf, computerTextRect)

    if turn == PLAYER:
        pygame.draw.circle(DISPLAYSURF, TURNCIRCLECOLOR,
                           (playerTextRect.right + 20, playerTextRect.centery), TURNCIRCLERADIUS)
    else:
        pygame.draw.circle(DISPLAYSURF, TURNCIRCLECOLOR,
                           (computerTextRect.right + 20, computerTextRect.centery),
                           TURNCIRCLERADIUS)

def showGameOverScreen(winner):
    # Show the end-of-game message and ask the player if they want to play again
    if winner == PLAYER:
        endMsg = "Game Over. Player wins!"
    elif winner == COMPUTER:
        endMsg = "Game Over. Computer wins!"
    else:
        endMsg = "Game Over. The game was a tie!"
        
    gameOverSurf = FONT.render(endMsg, True, FONTCOLOR, FONTRECTCOLOR)
    gameOverRect = gameOverSurf.get_rect()
    gameOverRect.centerx, gameOverRect.centery = int(WINDOWWIDTH/2), int(WINDOWHEIGHT/2)

    playAgainSurf = FONT.render("Play again", True, FONTCOLOR, FONTRECTCOLOR)
    playAgainRect = playAgainSurf.get_rect()
    playAgainRect.left, playAgainRect.top = gameOverRect.left + 20, gameOverRect.bottom + 20

    quitSurf = FONT.render("Quit", True, FONTCOLOR, FONTRECTCOLOR)
    quitRect = quitSurf.get_rect()
    quitRect.right, quitRect.top = gameOverRect.right - 20, gameOverRect.bottom + 20
    
    while True:
        mouseClicked = False
        
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEMOTION:
                mousex, mousey = event.pos
            elif event.type == MOUSEBUTTONUP:
                mousex, mousey = event.pos
                mouseClicked = True

        if mouseClicked and playAgainRect.collidepoint(mousex, mousey):
            return True
        elif mouseClicked and quitRect.collidepoint(mousex, mousey):
            return False

        DISPLAYSURF.blit(gameOverSurf, gameOverRect)
        DISPLAYSURF.blit(playAgainSurf, playAgainRect)
        DISPLAYSURF.blit(quitSurf, quitRect)
        pygame.display.update()
        FPSCLOCK.tick()

def getDotAtPixel(mouseX, mouseY):
    # Convert the pixel coordinates of the dot clicked to board coordinates
    for x in range(BOARDWIDTH + 1):
        for y in range(BOARDHEIGHT + 1):
            pixelX, pixelY = getLeftTopCoordsOfBox(x, y)
            pixelX -= int(DOTIMAGEWIDTH/2)
            pixelY -= int(DOTIMAGEHEIGHT/2)
            dotRect = pygame.Rect(pixelX, pixelY, DOTIMAGEWIDTH, DOTIMAGEHEIGHT)
            if dotRect.collidepoint(mouseX, mouseY):
                return (x, y)

    return None

def dotsAdjacent(dot1, dot2):
    # Check if two dots are next to one another
    dot1X, dot1Y = dot1[0], dot1[1]
    dot2X, dot2Y = dot2[0], dot2[1]

    if (dot1X == dot2X + 1 or dot1X == dot2X - 1) and dot1Y == dot2Y:
        return True
    elif (dot1Y == dot2Y + 1 or dot1Y == dot2Y - 1) and dot1X == dot2X:
        return True
    
    return False

def fillLine(board, point1, point2):
    # After two points have been clicked on the board, fill in the line they make
    for space in board:
        for line in board[space][2]:
            if set((point1, point2)) == set(line[0]):
                lineIndex = board[space][2].index(line)
                board[space][2][lineIndex][1] = True

def fillBoxes(board, turn):
    # Fill in boxes that are surrounded by filled lines
    boxesFilled = 0
    
    for space in board:
        if not board[space][0]:
            boxFilled = True
            
            for line in board[space][2]:
                if not line[1]:
                    boxFilled = False
                    
            if boxFilled:
                board[space][0] = True
                board[space][1] = turn
                boxesFilled += 1

    return boxesFilled

def isLineFilled(board, point1, point2):
    # Check if the given line on the board is filled in
    for space in board:
        for line in board[space][2]:
            if set(line[0]) == set((point1, point2)) and line[1]:
                return True
            
    return False
    
def getLeftTopCoordsOfBox(x, y):
    # Get the pixel coordinates of a box
    left = x * SPACESIZE + BOARDMARGIN
    top = y * SPACESIZE + BOARDMARGIN
    return left, top

def isGameOver(board):
    # Check if all the boxes on the board have been filled in
    gameOver = True
    for space in board:
        if not board[space][0]:
            gameOver = False

    return gameOver
    
if __name__ == "__main__":
    main()
