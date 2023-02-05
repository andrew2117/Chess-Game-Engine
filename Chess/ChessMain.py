""" 
This is our main driver file. It will be responsible for handling user input and displaying the current GameState object. 
"""
import pygame as p
import ChessEngine, SmartMoveFinder
import time
from multiprocessing import Process, Queue

WIDTH = HEIGHT = 512
DIMENSION = 8 #Dimensions of a chess board are 8x8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15 #Animations
IMAGES = {}

'''
Initialize a global dictionary of images. This will be called exactly once in the main
'''

def load_images():
    pieces = ['wp', 'wR', 'wN', 'wB', 'wQ', 'wK', 'bp', 'bR', 'bN', 'bB', 'bQ', 'bK']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))
    #Note: we can acces an image by saying 'IMAGES['piece-name']'


'''
The main driver for our code. This will handle user input and updating the graphics.
'''

def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState()
    validMoves = gs.get_valid_moves()
    moveMade = False #flag variable for when a move is made

    load_images() #only do this one, before the while loop
    running = True
    sqSelected = () #no square is selected initialized, keep track of the last click of the user (tuple:(row, col))
    playerClicks = [] #keep track of the player clicks (two tuples: [(6, 4), (4, 4)])
    gameOver = False
    playerOne = True #If a human is playing white, then this will be true, if an AI is playing, then false
    playerTwo = False #Same as above but for black 
    AIThinking = False
    moveFinderProcess = False
    while running:
        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            #mouse handler 
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver and humanTurn:
                    location = p.mouse.get_pos()#(x, y) location of mouse
                    col = location[0]//SQ_SIZE
                    row = location[1]//SQ_SIZE
                    if sqSelected == (row, col): #the user clicked the same square twice
                        sqSelected = () #deselect
                        playerClicks = [] #clear player clicks
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected) #sppend for both 1st and 2nd clicks
                    if len(playerClicks) == 2: #after 2nd click
                        move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                        print(move.get_chess_notation())
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gs.make_move(validMoves[i])
                                moveMade = True
                                sqSelected = () #reset user clicks
                                playerClicks = []
                        if not moveMade:
                            playerClicks = [sqSelected]
            #key handlers
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z: #undo when 'z' is pressed
                    gs.undo_move()
                    moveMade = True
                    gameOver = False
                    if AIThinking:
                       moveFinderProcess.terminate()
                       AIThinking = False
                    moveUndone = True
                if e.key == p.K_r: #redo when 'r' is pressed
                    gs = ChessEngine.GameState()
                    validMoves = gs.get_valid_moves()
                    playerClicks = []
                    moveMade = False
                    gameOver = False
                    if AIThinking:
                       moveFinderProcess.terminate()
                       AIThinking = False
                    moveUndone = True

        #AI move finder
        if not gameOver and not humanTurn and not moveUndone:
            if not AIThinking:
                AIThinking = True
                print("thinking....")
                returnQueue = Queue() #used to pass data between threads
                moveFinderProcess = Process(target=SmartMoveFinder.find_best_move, args=(gs, validMoves, returnQueue))
                moveFinderProcess.start() #call find_best_move(gs, validMoves, returnQueue)

            if not moveFinderProcess.is_alive():
                AIMove = returnQueue.get()
                if AIMove is None:
                    AIMove = SmartMoveFinder.find_random_move(validMoves)
                gs.make_move(AIMove)
                moveMade = True
                AIThinking = False
    
        if moveMade:
            validMoves = gs.get_valid_moves()
            moveMade = False
            moveUndone = False

        draw_game_state(screen, gs, validMoves, sqSelected)

        if gs.checkMate:
            gameOver = True
            draw_text(screen, "Jaque Mate Perra")
        elif gs.staleMate:
            gameOver = True
            draw_text(screen, "EMPATE")
            
        clock.tick(MAX_FPS)
        p.display.flip()



"""
Highlight square selected and moves for piece selected
"""
def highlighting_squares(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'): #sqSelected is a piece that can be moved
            #highlight selected square
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(120) #if this value is ->9 transparent, 255 opaque
            s.fill(p.Color('cyan'))
            screen.blit(s, ((c*SQ_SIZE, r*SQ_SIZE)))
            #highlight moves from that square
            s.fill(p.Color('black'))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (SQ_SIZE*move.endCol, SQ_SIZE*move.endRow))

"""
Responsible for all the graphics within a current state
"""
def draw_game_state(screen, gs, validMoves, sqSelected):
    draw_board(screen) #draw squares on the board
    highlighting_squares(screen, gs, validMoves, sqSelected)
    draw_pieces(screen, gs.board) #draw pieces on top of those squares


"""
Draw the squares on the board using the current GameState.board
"""
def draw_board(screen):
    colors = [p.Color("white"), p.Color("gray")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r+c) % 2)]
            p.draw.rect(screen, color, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

            
"""
Draw the pieces on the board using the 
"""
def draw_pieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--": #Not empty piece
                screen.blit(IMAGES[piece], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))


def draw_text(screen, text):
    font = p.font.SysFont("Helvetica", 60, True, False)
    textObject = font.render(text, 0, p.Color('black'))
    textLocation = p.Rect(0,0, WIDTH, HEIGHT).move(WIDTH/2 - textObject.get_width()/2, HEIGHT/2 - textObject.get_height()/2)
    screen.blit(textObject, textLocation)

if __name__ == "__main__":
    main()