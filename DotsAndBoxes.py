# Dots and Boxes
#
# Connect dots to get the most territories

import pygame, sys
from pygame.locals import *

FPS = 30
WINDOWWIDTH = 600
WINDOWHEIGHT = 620

BOARDWIDTH = 8
BOARDHEIGHT = 7
SPACESIZE = 70
INNERSPACESIZE = 64
INNERSPACEMARGIN = int((SPACESIZE - INNERSPACESIZE) / 2)
BOARDPIXELWIDTH = BOARDWIDTH * SPACESIZE
BOARDPIXELHEIGHT = BOARDHEIGHT * SPACESIZE
XMARGIN = int((WINDOWWIDTH - BOARDPIXELWIDTH) / 2)
YMARGIN = XMARGIN
BOARDRECT = pygame.Rect(XMARGIN, YMARGIN, BOARDPIXELWIDTH, BOARDPIXELHEIGHT)
BOTTOMSPACEHEIGHT = WINDOWHEIGHT - (BOARDPIXELHEIGHT + YMARGIN * 2)

LINEBGWIDTH = 1
LINEWIDTH = 7

BGCOLOR = (10, 90, 75) # blue
BOARDCOLOR = (255, 255, 255) # white
LINEBGCOLOR = (185, 185, 185) # light gray
LINECOLOR = (0, 0, 0) # black
FONTCOLOR = (255, 255, 255) # white
FONTRECTCOLOR = (255, 190, 0) # yellow
HIGHLIGHTCOLOR = (50, 175, 70) # green
PLAYERCOLOR = (180, 20, 20) # red
COMPUTERCOLOR = (255, 150, 0) # yellow

DOTIMAGE = pygame.image.load("dot.png")
DOTIMAGEWIDTH = 15
DOTIMAGEHEIGHT = 15

def main():
    global FPSCLOCK, DISPLAYSURF, FONT

    pygame.init()
    FPSCLOCK = pygame.time.Clock()

    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    pygame.display.set_caption("Dots and Boxes")

    FONT = pygame.font.Font("freesansbold.ttf", 36)

    while True:
        playAgain = runGame()
        if not playAgain:
            pygame.quit()
            sys.exit()

def runGame():
    # Run the game until there are no moves left to take
    playerScore = 0
    computerScore = 0

    mouseX = 0
    mouseY = 0

    lineCoordsList = []
    dotRects = getDotRects()
    firstDotClicked = None
    secondDotClicked = None
    board = createBoard()
    
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEMOTION:
                mouseX, mouseY = event.pos
            elif event.type == MOUSEBUTTONUP:
                dotClicked = getDotAtPixel(dotRects, mouseX, mouseY)
                if dotClicked and not firstDotClicked:
                    firstDotClicked = dotClicked
                elif dotClicked and firstDotClicked and not secondDotClicked:
                    if dotsAdjacent(firstDotClicked, dotClicked):
                        secondDotClicked = dotClicked
                    else:
                        firstDotClicked = dotClicked

        if firstDotClicked and secondDotClicked:
            linePoints = ((firstDotClicked.centerx, firstDotClicked.centery), (secondDotClicked.centerx, secondDotClicked.centery))
            linePointsReversed = ((secondDotClicked.centerx, secondDotClicked.centery), (firstDotClicked.centerx, firstDotClicked.centery))
            if linePoints not in lineCoordsList and linePointsReversed not in lineCoordsList:
                lineCoordsList.append(linePoints)
                lineCoordsList.append(linePointsReversed)
                board = makeLineFilledOnBoard(board, linePoints)
            firstDotClicked, secondDotClicked = None, None
        board = makeSpaceFilledOnBoard(board)
        
        draw(lineCoordsList, dotRects, firstDotClicked, board)
        pygame.display.update()
        FPSCLOCK.tick(FPS)

def createBoard():
    # Create a board dict with an entry for each space
    board = {}
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            spaceName = str(x) + str(y)
            surroundingLines = getSurroundingLines(x, y)
            surroundingLines = dict(zip(surroundingLines, [False, False, False, False,
                                                           False, False, False, False]))
            board[spaceName] = [surroundingLines, None]
    return board
    
def getDotAtPixel(dotRects, mouseX, mouseY):
    # Find the dot on the board that was clicked
    for dotRect in dotRects:
        if dotRect.collidepoint(mouseX, mouseY):
            return dotRect
        
def getDotRects():
    # Make a list of rect objects for dots on the board
    dotRects = []
    for x in range(BOARDWIDTH + 1):
        for y in range(BOARDHEIGHT + 1):
            left, top = getLeftTopCoordsOfBox(x, y)
            xPos = left - int(DOTIMAGEWIDTH / 2)
            yPos = top - int(DOTIMAGEHEIGHT / 2)
            dotRects.append(pygame.Rect(xPos, yPos, DOTIMAGEWIDTH, DOTIMAGEHEIGHT))
    return dotRects

def makeLineFilledOnBoard(board, line):
    # Set a line to filled on the board
    breakFromLoop = False
    for space in board:
        for surroundingLine in board[space][0]:
            if surroundingLine == line:
                board[space][0][line] = True
                breakFromLoop = True
                break
        if breakFromLoop:
            break
    return board

def makeSpaceFilledOnBoard(board):
    # Make spaces on the board surrounded by filled lines filled in
    for space in board:
        if board[space][1] == None:
            linesFilled = True
            for surroundingLine in board[space][0]:
                if board[space][0][surroundingLine] == False:
                    linesFilled = False
                if not linesFilled:
                    break
            if linesFilled:
                board[space][1] = "player"
    return board

def dotsAdjacent(dot1, dot2):
    # Check if two dots are next to one another
    dot1X, dot1Y = dot1.left, dot1.top
    dot2X, dot2Y = dot2.left, dot2.top
    if (dot1X == dot2X + SPACESIZE or dot1X == dot2X - SPACESIZE) and dot1Y == dot2Y:
        return True
    elif (dot1Y == dot2Y + SPACESIZE or dot1Y == dot2Y - SPACESIZE) and dot1X == dot2X:
        return True
    return False

def draw(lineCoordsList, dotRects, firstDotClicked, board):
    # Draw the background, lines connecting dots, and dots
    drawBackground()
    drawLines(lineCoordsList)
    drawSpaces(board)
    drawDots(dotRects, firstDotClicked)

def drawBackground():
    # Fill the display and draw the board
    DISPLAYSURF.fill(BGCOLOR)
    pygame.draw.rect(DISPLAYSURF, BOARDCOLOR, BOARDRECT)
    for x in range(BOARDWIDTH + 1):
        for y in range(BOARDHEIGHT + 1):
            left, top = getLeftTopCoordsOfBox(x, y)
            pygame.draw.line(DISPLAYSURF, LINEBGCOLOR, (XMARGIN, top), (XMARGIN + BOARDPIXELWIDTH, top), LINEBGWIDTH)
            pygame.draw.line(DISPLAYSURF, LINEBGCOLOR, (left, YMARGIN), (left, YMARGIN + BOARDPIXELHEIGHT), LINEBGWIDTH)

def drawLines(lineCoordsList):
    # Draw the lines created by the player
    for startPoint, endPoint in lineCoordsList:
        pygame.draw.line(DISPLAYSURF, LINECOLOR, (startPoint[0], startPoint[1]), (endPoint[0], endPoint[1]), LINEWIDTH)

def drawDots(dotRects, firstDotClicked):
    # Draw the dots on the board
    for dotRect in dotRects:
        dotImageX, dotImageY = dotRect.left, dotRect.top
        DISPLAYSURF.blit(DOTIMAGE, (dotImageX, dotImageY))
        if dotRect == firstDotClicked:
            highlightDot(dotRect.centerx, dotRect.centery)

def drawSpaces(board):
    # Fill in owned spaces on the board
    for space in board:
        x, y = int(space[0]), int(space[1])
        rectX, rectY = getLeftTopCoordsOfBox(x, y)
        rectObj = pygame.Rect(rectX + INNERSPACEMARGIN, rectY + INNERSPACEMARGIN, INNERSPACESIZE, INNERSPACESIZE)
        if board[space][1] == "player":
            rectObj = pygame.draw.rect(DISPLAYSURF, PLAYERCOLOR, rectObj)
        elif board[space][1] == "computer":
            rectObj = pygame.draw.rect(DISPLAYSURF, COMPUTERCOLOR, rectObj)
        
def getSurroundingLines(x, y):
    # Get the coordinates of the start and end points of the lines surrounding a box
    leftTopX, leftTopY = getLeftTopCoordsOfBox(x, y)
    leftTop = (leftTopX, leftTopY)
    
    rightTopX, rightTopY = leftTopX + SPACESIZE, leftTopY
    rightTop = (rightTopX, rightTopY)
    
    leftBottomX, leftBottomY = leftTopX, leftTopY + SPACESIZE
    leftBottom = (leftBottomX, leftBottomY)
    
    rightBottomX, rightBottomY = leftTopX + SPACESIZE, leftTopY + SPACESIZE
    rightBottom = (rightBottomX, rightBottomY)

    return ((leftTop, rightTop), (rightTop, rightBottom), (rightBottom, leftBottom), (leftBottom, leftTop),
            (rightTop, leftTop), (rightBottom, rightTop), (leftBottom, rightBottom), (leftTop, leftBottom))

def highlightDot(x, y):
    # Draw a highlight around a specified dot
    pygame.draw.circle(DISPLAYSURF, HIGHLIGHTCOLOR, (x, y), int(DOTIMAGEWIDTH / 2) + 2, 2)
    
def getLeftTopCoordsOfBox(x, y):
    # Get the pixel coordinates of a box
    left = XMARGIN + x * SPACESIZE
    top = YMARGIN + y * SPACESIZE
    return left, top

if __name__ == "__main__":
    main()
