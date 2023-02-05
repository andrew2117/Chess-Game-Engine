""" 
This class is responsible for storing all the information about the current state of a chess game. 
It will also be responsible for determining the valid moves at the curent state. It will also keep a move log. 
"""

#Board is an 8x8 2d array, each element of the array has 2 characters.
#The firts character represents the clor of the piece, 'b' or 'w'.
#The second character represents the type of the piece, 'K', 'Q', 'R', 'B', 'N' or 'p'.
#The "--" represents an empty space with no piece.
class GameState():
    def __init__(self):
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]]

        self.move_functions = {'p': self.get_pawn_moves, 'R': self.get_rook_moves, 'N': self.get_knight_moves,
                               'B': self.get_bishop_moves, 'Q': self.get_queen_moves, 'K': self.get_king_moves}
        self.moveLog = []
        self.whiteToMove = True
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.inCheck = False
        self.pins = []  #pieces who blocks the king from checks
        self.checks = []
        self.checkMate = False
        self.staleMate = False
        self.enpassantPossible = () #coordinates for the square where on passant capture is possible
        self.enPassantPossibleLog = [self.enpassantPossible]
        #castling rights
        self.currentCastlingRights = CastleRights(True, True, True, True)
        self.castleRightsLog = [CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks, self.currentCastlingRights.wqs, self.currentCastlingRights.bqs)]


    """
    Takes a move as a parameter and executes it (this will now work for castling, pawn promotion and en-pessant)
    """
    def make_move(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move) #Log the move so we can undo it later
        self.whiteToMove = not self.whiteToMove #swap players
        #update the king's position
        if move.pieceMoved == "wK":
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == "bK":
            self.blackKingLocation = (move.endRow, move.endCol)
        #if pawn move twice , next move can capture enpassant
        if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:
            self.enpassantPossible = ((move.endRow + move.startRow)//2, move.endCol)
        else:
            self.enpassantPossible = ()
        #if enpassant move , must update the board to capture the pawn
        if move.enPassant:
            self.board[move.startRow][move.endCol] = "--" #capturing the pawn
        #pawn promotion
        """ if move.isPawnPromotion:
            #promotedPiece = input("Promote to Q, R, B or N:")
            promotedPiece = 'Q'
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + promotedPiece """
        
        #castle moves
        if move.castle:
            if move.endCol - move.startCol == 2: #king side
                self.board[move.endRow][move.endCol-1] = self.board[move.endRow][move.endCol+1] #move rook
                self.board[move.endRow][move.endCol+1] = '--' #empty space where rook was
            else: #queen side
                self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-2] #move rook
                self.board[move.endRow][move.endCol-2] = '--' #empty space where rook was

        self.enPassantPossibleLog.append(self.enpassantPossible)
        #update castling rights
        self.update_castle_rights(move)
        self.castleRightsLog.append(CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks, self.currentCastlingRights.wqs, self.currentCastlingRights.bqs))

    '''
    Undo the las move made
    '''  
    def undo_move(self):
        if len(self.moveLog) != 0: #make sure that there is a move to undo
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove #switch turns back

            #update the king's position
            if move.pieceMoved == "wK":
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == "bK":
                self.blackKingLocation = (move.startRow, move.startCol)

            #undo enpassant
            if move.enPassant:
                self.board[move.endRow][move.endCol] = '--' #removes the pawn that was added in the wrong square
                self.board[move.startRow][move.endCol] = move.pieceCaptured #puts the pawn back on the correct square it was captured from
           
            self.enPassantPossibleLog.pop()
            self.enpassantPossible = self.enPassantPossibleLog[-1]

            #give back castle right if m0ove took them away
            self.castleRightsLog.pop() #remove last move updates
            castleRights = self.castleRightsLog[-1]
            self.currentCastlingRights.wks = castleRights.wks
            self.currentCastlingRights.bks = castleRights.bks
            self.currentCastlingRights.wqs = castleRights.wqs
            self.currentCastlingRights.bqs = castleRights.bqs

            #undo castle
            if move.castle:
                if move.endCol - move.startCol == 2: #king side
                    self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-1] #move rook
                    self.board[move.endRow][move.endCol-1] = '--' #empty space where rook was
                else: #queen side
                    self.board[move.endRow][move.endCol-2] = self.board[move.endRow][move.endCol+1] #move rook
                    self.board[move.endRow][move.endCol+1] = '--' #empty space where rook was

            self.checkMate = False
            self.staleMates = False 

    '''
    All moves considering checks
    '''
    def get_valid_moves(self):
        moves = []
        self.inCheck, self.pins, self.checks = self.check_for_pins_and_checks()
        if self.whiteToMove:
            kingRow = self.whiteKingLocation[0]
            kingCol = self.whiteKingLocation[1]
        else:
            kingRow = self.blackKingLocation[0]
            kingCol = self.blackKingLocation[1]
        if self.inCheck:
            if len(self.checks) == 1: #only 1 check, block check or move king 
                moves = self.get_all_possible_moves()
                #to block a check you must move a piece into one of the squares between the enemy and piece and king 
                check = self.checks[0] #check information
                checkRow = check[0]
                checkCol = check[1]
                pieceChecking = self.board[checkRow][checkCol] #enemy piece causing the check
                validSquares = [] #squares that pieces can move to
                #if knight, must capture knight or move king, other pieces can be blocked
                if pieceChecking[1] == 'N':
                    validSquares = [(checkRow, checkCol)]
                else:
                    for i in range(1, 8):
                        validSquare = (kingRow + check[2] * i, kingCol + check[3] * i) #check[2] and check[3] are the check directions
                        validSquares.append(validSquare)
                        if validSquare[0] == checkRow and validSquare[1] == checkCol: #once you get to piece and checks
                            break
                #get rind of any moves that don't block check or move king
                for i in range(len(moves)-1, -1, -1): #go through backwards when you are removing from a list as iterating 
                    if moves[i].pieceMoved[1] != 'K': #move doesn't move king so it must block or capture
                        if not (moves[i].endRow, moves[i].endCol) in validSquares: #move doesn't block check or capture piece
                            moves.remove(moves[i])
            else: #double check, king has to move
                self.get_king_moves(kingRow, kingCol, moves)
        else: #not in check so all moves are fine
            moves = self.get_all_possible_moves()
        
        if len(moves) == 0:
            if self.inCheck:
                self.checkMate = True
            else:
                self.staleMate = True
        else:
            self.checkMate = False
            self.staleMate = False
        return moves


    '''
    All moves without considering checks
    '''
    def get_all_possible_moves(self):
        moves = []
        for r in range(len(self.board)): #number of rows
            for c in range(len(self.board[r])): #number of cols in given row
                turn = self.board[r][c][0]
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.move_functions[piece](r, c, moves) #call the apropiate move function based on piece type
        return moves

    '''         
    Get all the pawn moves for the pawn located at row, col and add these moves to the list
    '''             
    def get_pawn_moves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        if self.whiteToMove: #white pawn moves
            moveAmount = -1
            startRow = 6
            enemyColor = 'b'
            kingRow, kingCol = self.whiteKingLocation
        else:
            moveAmount = 1
            startRow = 1
            enemyColor = 'w'
            kingRow, kingCol = self.blackKingLocation
            
        if self.board[r + moveAmount][c] == "--": #1 square pawn advance
                if not piecePinned or pinDirection == (moveAmount, 0):
                    moves.append(Move((r, c), (r + moveAmount, c), self.board))
                    if r == startRow and self.board[r + 2 * moveAmount][c] == "--": #2 square pawn advance
                        moves.append(Move((r, c), (r + 2 * moveAmount, c), self.board))

        if c - 1 >= 0: #captures to the left
            if not piecePinned or pinDirection == (moveAmount, -1):
                if self.board[r + moveAmount][c - 1][0] == enemyColor:
                    moves.append(Move((r, c), (r + moveAmount, c - 1), self.board))
                if (r + moveAmount, c - 1) == self.enpassantPossible:
                    attackingPiece = blockingPiece = False
                    if kingRow == r:
                        if kingCol < c: #king is left to the pawn
                            #inside between king and pawn; outside range between pawn border
                            insideRange = range(kingCol + 1, c - 1)
                            outsideRange = range(c + 1, 8)
                        else:
                            insideRange = range(kingCol - 1, c, -1)
                            outsideRange = range(c - 2, -1, -1)
                        for i in insideRange:
                            if self.board[r][i] != "--": #some other piece beside en-passant pawn blocks
                                blockingPiece = True
                        for i in outsideRange:
                            square = self.board[r][i]
                            if square[0] == enemyColor and (square[1] == "R" or square[1] == "Q"): #attacking piece
                                attackingPiece = True
                            elif square != "--":
                                blockingPiece = True
                    if not attackingPiece or blockingPiece:
                        moves.append(Move((r, c), (r + moveAmount, c - 1), self.board, enPassant=True))
        if c+1 <= 7: #captures to the right
            if not piecePinned or pinDirection == (moveAmount, 1):
                if self.board[r + moveAmount][c + 1][0] == enemyColor:
                    moves.append(Move((r, c), (r + moveAmount, c + 1), self.board))
                if (r + moveAmount, c + 1) == self.enpassantPossible:
                    attackingPiece = blockingPiece = False
                    if kingRow == r:
                        if kingCol < c: #king is left to the pawn
                            #inside between king and pawn; outside range between pawn border
                            insideRange = range(kingCol + 1, c)
                            outsideRange = range(c + 2, 8)
                        else:
                            insideRange = range(kingCol - 1, c + 1, -1)
                            outsideRange = range(c - 1, -1, -1)
                        for i in insideRange:
                            if self.board[r][i] != "--": #some other piece beside en-passant pawn blocks
                                blockingPiece = True
                        for i in outsideRange:
                            square = self.board[r][i]
                            if square[0] == enemyColor and (square[1] == "R" or square[1] == "Q"): #attacking piece
                                attackingPiece = True
                            elif square != "--":
                                blockingPiece = True
                    if not attackingPiece or blockingPiece:
                        moves.append(Move((r, c), (r + moveAmount, c + 1), self.board, enPassant=True))

    '''
     Get all the rook moves for the rook located at row, col and add these moves to the list
    '''             
    def get_rook_moves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                if self.board[r][c][1] != 'Q': #can't move queen from pin on rook moves, only remove it on bishop moves
                    self.pins.remove(self.pins[i])
                break
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1)) # up, left, down, right
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8: # on board
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == "--":    # empty space valid
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                        elif endPiece[0] == enemyColor:     # enemy piece valid
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                            break
                        else:  # friendly piece invalid
                            break
                else:   # off board
                    break
        
    '''
     Get all the bishop moves for the bishop located at row, col and add these moves to the list
    '''  
    def get_bishop_moves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1)) 
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):   # max of 7 squares
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8: # on board
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == "--":    # empty space valid
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                        elif endPiece[0] == enemyColor:     # enemy piece valid
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                            break
                        else:  # friendly piece invalid
                            break
                else:   # off board
                    break

    '''
     Get all the knight moves for the knight located at row, col and add these moves to the list
    '''      
    def get_knight_moves(self, r, c, moves):
        piecePinned = False        
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                self.pins.remove(self.pins[i])
                break
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        allyColor = "w" if self.whiteToMove else "b"
        for m in knightMoves:
            endRow = r + m[0] 
            endCol = c + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8: # on board
                if not piecePinned:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] != allyColor:     # not an ally piece (empty or enemy piece)
                        moves.append(Move((r, c), (endRow, endCol), self.board))

    '''
     Get all the queen moves for the queen located at row, col and add these moves to the list
    '''  
    def get_queen_moves(self, r, c, moves):
        self.get_rook_moves(r,c, moves)
        self.get_bishop_moves(r,c, moves)

    '''
     Get all the king moves for the king located at row, col and add these moves to the list
    '''  
    def get_king_moves(self, r, c, moves):
        rowMoves = (-1, -1, -1, 0, 0, 1, 1, 1)
        colMoves = (-1, 0, 1, -1, 1, -1, 0, 1)
        allyColor = "w" if self.whiteToMove else "b"
        for i in range(8):
            endRow = r + rowMoves[i]
            endCol = c + colMoves[i]
            if 0 <= endRow < 8 and 0 <= endCol < 8: # on board
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] != allyColor:   # not an ally piece (empty or enemy piece)
                        #place king on end square and check for checks
                        if allyColor == 'w':
                            self.whiteKingLocation = (endRow, endCol)
                        else:
                            self.blackKingLocation = (endRow, endCol)
                        inCheck, pins, checks = self.check_for_pins_and_checks()
                        if not inCheck:
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                        #place king back on original location
                        if allyColor == 'w':
                            self.whiteKingLocation = (r, c)
                        else:
                            self.blackKingLocation = (r, c)
        self.get_castle_moves(r, c, moves, allyColor)
    '''
     Generates castle moves for the king at (r,c) and add them to the list of moves
    '''  
    def get_castle_moves(self, r, c, moves, allyColor):
        inCheck = self.square_under_attack(r, c, allyColor)
        if inCheck:
            return #can't castle in check
        if (self.whiteToMove and self.currentCastlingRights.wks) or (not self.whiteToMove and self.currentCastlingRights.bks): #can't castle if given up rights
            self.get_king_side_castle_moves(r, c, moves, allyColor)
        if (self.whiteToMove and self.currentCastlingRights.wqs) or (not self.whiteToMove and self.currentCastlingRights.bqs): #can't castle if given up rights
            self.get_queen_side_castle_moves(r, c, moves, allyColor)
      
    '''
    Generate kingside castle moves for the king at (r,c). This method will only be called if player still has castle rights kingside.
    '''  
    def get_king_side_castle_moves(self, r, c, moves, allyColor):
        #check if two square between king and rook are clear and not under attack
        if self.board[r][c+1] == '--' and self.board[r][c+2] == '--' and not self.square_under_attack(r, c+1, allyColor) and \
        not self.square_under_attack(r, c+2, allyColor):
            moves.append(Move((r, c), (r, c+2), self.board, castle = True))

    '''
    Generate queenside castle moves for the king at (r,c). This method will only be called if player still has castle rights queenside.
    '''  
    def get_queen_side_castle_moves(self, r, c, moves, allyColor):
        #check if two square between king and rook are clear and two squares left of king are not under attack
        if self.board[r][c-1] == '--' and self.board[r][c-2] == '--' and self.board[r][c-3] == '--' and \
        not self.square_under_attack(r, c-1, allyColor) and not self.square_under_attack(r, c-2, allyColor):
            moves.append(Move((r, c), (r, c-2), self.board, castle = True))
    

    def square_under_attack(self, r, c, allyColor):
        #check outward from square
        enemyColor = "w" if allyColor == 'b' else "b"
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            d = directions[j]
            for i in range(1, 8):
                endRow = r + d[0] *i
                endCol = c + d[1] *i
                if 0 <= endRow < 8 and 0 <= endCol < 8: # on board
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] == allyColor: # not attack from that direction
                        break
                    elif endPiece[0] == enemyColor:
                        types = endPiece[1]
                        #5 posibilities here in this complex conditional
                        #1.) orthogonally away from king and piece is a rook
                        #2.) diagonally away from king and piece is a bishop
                        #3.) 1 square away diagonally from king and piece is a pawn 
                        #4.) any direction and piece is a queen
                        #5.) any direction 1 square away and piece is a king (this is necessaty to prevent a king move to a square controlled by another king)
                        if(0 <= j <= 3 and types == 'R') or \
                        (4 <= j <= 7 and types == 'B') or \
                        (i == 1 and types == 'p' and ((enemyColor == 'w' and  6 <= j <= 7) or (enemyColor == 'b' and 4 <= j <= 5))) or \
                        (types == 'Q') or (i == 1 and types == 'K'):
                            return True
                        else:  #enemy piece not applying check
                            break
                else:  #off board
                    break
        #check for knight checks
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        for m in knightMoves:
            endRow = r + m[0] 
            endCol = c + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] ==  enemyColor and endPiece[1] == 'N': #enemy knight attacking king
                    return True
        return False

        
    '''
    Returns if a player is in check, a list of pins, and a list of checks
    '''
    def check_for_pins_and_checks(self):
        pins = [] # squares where the allied pinned piece is and direction pinned from
        checks = [] #squares where the enemy is applying a check
        inCheck = False
        if self.whiteToMove:
            enemyColor = "b"
            allyColor = "w"
            startRow = self.whiteKingLocation[0]
            startCol = self.whiteKingLocation[1]
        else:
            enemyColor = "w"
            allyColor = "b"
            startRow = self.blackKingLocation[0]
            startCol = self.blackKingLocation[1]
        #check outward form king for pins and checks, keep track of pins
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            d = directions[j]
            possiblePin = () #reset possible pin
            for i in range(1, 8):
                endRow = startRow + d[0] * i
                endCol = startCol + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8: # on board
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] == allyColor and endPiece[1] != 'K': # not an ally piece (empty or enemy piece)
                        if possiblePin == (): #1st allied piece could pinned
                            possiblePin = (endRow, endCol, d[0], d[1])
                        else:   #2nd allied piece, so no pin or check is possible in this direction
                            break
                    elif endPiece[0] == enemyColor:
                        types = endPiece[1]
                        #5 posibilities here in this complex conditional
                        #1.) orthogonally away from king and piece is a rook
                        #2.) diagonally away from king and piece is a bishop
                        #3.) 1 square away diagonally from king and piece is a pawn 
                        #4.) any direction and piece is a queen
                        #5.) any direction 1 square away and piece is a king (this is necessaty to prevent a king move to a square controlled by another king)
                        if(0 <= j <= 3 and types == 'R') or \
                        (4 <= j <= 7 and types == 'B') or \
                        (i == 1 and types == 'p' and ((enemyColor == 'w' and  6 <= j <= 7) or (enemyColor == 'b' and 4 <= j <= 5))) or \
                        (types == 'Q') or (i == 1 and types == 'K'):
                            if possiblePin == (): #no piece blocking, so check
                                inCheck = True
                                checks.append((endRow, endCol, d[0], d[1]))
                                break
                            else: #piece is blocking so pin
                                pins.append(possiblePin)
                        else:  #enemy piece not applying check
                            break
                else:  #off board
                    break
        #check for knight checks
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        for m in knightMoves:
            endRow = startRow + m[0] 
            endCol = startCol + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] ==  enemyColor and endPiece[1] == 'N': #enemy knight attacking king
                    inCheck = True
                    checks.append((endRow, endCol, m[0], m[1]))
        return inCheck, pins, checks


    def update_castle_rights(self, move):
        if move.pieceMoved == 'wK':
            self.currentCastlingRights.wks = False 
            self.currentCastlingRights.wqs = False 
        elif move.pieceMoved == 'bK':
            self.currentCastlingRights.bks = False
            self.currentCastlingRights.bqs = False
        elif move.pieceMoved == 'wR':
            if move.startRow == 7:
                if move.startCol == 7: #right rook
                    self.currentCastlingRights.wks = False
                elif move.startCol == 0: #left rook
                    self.currentCastlingRights.wqs = False
        elif move.pieceMoved == 'bR':
            if move.startRow == 0:
                if move.startCol == 7: #right rook
                    self.currentCastlingRights.bks = False
                elif move.startCol == 0: #left rook
                    self.currentCastlingRights.bqs = False


class CastleRights():
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs

class Move():
    # maps keys to values
    # key : value
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4,
                   "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3,
                   "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startsq, endsq, board, enPassant = False, isPawnPromotion = False, castle = False):
        self.startRow = startsq[0]
        self.startCol = startsq[1]
        self.endRow = endsq[0]
        self.endCol = endsq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        #en passant
        self.enPassant = enPassant
        #pawn promotion
        self.isPawnPromotion = isPawnPromotion
        self.castle = castle
        if enPassant:
            self.pieceCaptured = 'bp' if self.pieceMoved == 'wp' else 'wp' #enpassant captures opposite colored pawn
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol

    '''
    Overriding the equals method
    '''
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False
    

    def get_chess_notation(self):
        #you can add to make this like real chess notation
        return self.get_rank_file(self.startRow, self.startCol) + self.get_rank_file(self.endRow, self.endCol)

    def get_rank_file(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]
