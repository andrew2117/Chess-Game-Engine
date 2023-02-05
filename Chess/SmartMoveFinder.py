import random

pieceScore = {"K": 0, "Q":10, "R": 5, "B":3, "N": 3, "p":1}

knightScores = [[1, 1, 1, 1, 1, 1, 1, 1],
                [1, 2, 2, 2, 2, 2, 2, 1],
                [1, 2, 3, 3, 3, 3, 2, 1],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [1, 2, 3, 3, 3, 3, 2, 1],
                [1, 2, 2, 2, 2, 2, 2, 1],
                [1, 1, 1, 1, 1, 1, 1, 1]]
               
piecePositionScores = {"N": knightScores}
CHECKMATE = 1000
DEPTH = 3


"""
Picks and returns a random move
"""
def find_random_move(validMoves):
    return validMoves[random.randint(0, len(validMoves)-1)]
    
"""
MiniMax algorithm without recursion
"""
def find_best_move_dummy(gs, validMoves):
    turnMultiplier = 1 if gs.whiteToMove else -1
    opponentMinMaxScore = CHECKMATE
    bestPlayerMove = None
    random.shuffle(validMoves)
    for playerMove in validMoves:
        gs.make_move(playerMove)
        opponentsMoves = gs.get_valid_moves()
        if gs.staleMate:
            opponentMaxScore = 0
        elif gs.checkMate:
            opponentMaxScore = -CHECKMATE
        else:            
            opponentMaxScore = -CHECKMATE
        for opponentsMove in opponentsMoves:
            gs.make_move(opponentsMove)
            gs.get_valid_moves()
            if gs.checkMate:
                score = CHECKMATE
            elif gs.staleMate:
                score = 0
            else:
                score = -turnMultiplier * score_material(gs.board)
            if score > opponentMaxScore:
                opponentMaxScore = score
            gs.undo_move()
        if opponentMaxScore < opponentMinMaxScore:
            opponentMinMaxScore = opponentMaxScore
            bestPlayerMove = playerMove 
        gs.undo_move()
    return bestPlayerMove

"""
Helper method to make first recursive call
"""
def find_best_move(gs, validMoves, returnQueue):
    global nextMove
    nextMove = None
    random.shuffle(validMoves)
    #ind_move_min_max(gs, validMoves, DEPTH, gs.whiteToMove)
    find_move_nega_max_alpha_beta(gs, validMoves, DEPTH, 1 if gs.whiteToMove else -1, -CHECKMATE, CHECKMATE)
    returnQueue.put(nextMove)

"""
MiniMax algotithm with recursion
"""
def find_move_min_max(gs, validMoves, depth, whiteToMove):
    global nextMove 
    if depth == 0:
        return score_material(gs.board)

    if whiteToMove:
        maxScore = -CHECKMATE
        for move in validMoves:
            gs.make_move(move)
            nextMoves = gs.get_valid_moves()
            score = find_move_min_max(gs, nextMoves, depth-1, False)
            if score > maxScore:
                maxScore = score
                if depth == DEPTH:
                    nextMove = move
            gs.undo_move()
        return maxScore

    else:
        minScore = CHECKMATE
        for move in validMoves:
            gs.make_move(move)
            nextMoves = gs.get_valid_moves()
            score = find_move_min_max(gs, nextMoves, depth-1, True)
            if score < minScore:
                minScore = score
                if depth == DEPTH:
                    nextMove = move
                gs.undo_move()
            return minScore

"""
Nega max without Alpha-Beta-Pruning algorithm
"""
def find_move_nega_max(gs, validMoves, depth, turnMultiplier):
    global nextMove
    if depth == 0:
        return turnMultiplier * score_board(gs)

    maxScore = -CHECKMATE
    for move in validMoves:
        gs.make_move(move)
        nextMoves = gs.get_valid_moves()
        score = -find_move_nega_max(gs, nextMoves, depth-1, -turnMultiplier)
        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                nextMove = move
        gs.undo_move()
    return maxScore

"""
Nega max with Alpha-Beta-Pruning
"""
def find_move_nega_max_alpha_beta(gs, validMoves, depth, turnMultiplier, alpha, beta):
    global nextMove
    if depth == 0:
        return turnMultiplier * score_board(gs)

    #move ordering - implement later
    maxScore = -CHECKMATE
    for move in validMoves:
        gs.make_move(move)
        nextMoves = gs.get_valid_moves()
        score = -find_move_nega_max_alpha_beta(gs, nextMoves, depth-1, -turnMultiplier, -beta, -alpha)
        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                nextMove = move
        gs.undo_move()
        if maxScore > alpha: #pruning happens
            alpha = maxScore
        if alpha >= beta:
            break
    return maxScore

"""
A positive score is good for white, a negative score is good for black
"""
def score_board(gs):
    if gs.checkMate:
        if gs.whiteToMove:
            return -CHECKMATE #black wins
        else:
            return CHECKMATE #white wins
    elif gs.staleMate:
        return 0 #neither side wins

    score = 0
    for row in range(len(gs.board)):
        for col in range(len(gs.board[row])):
            square = gs.board[row][col]
            if square != "--":
                #score it positionnally 
                piecePositionScore = 0
                if square[1] == "N":
                    piecePositionScore = piecePositionScores["N"][row][col]
                if square[0] == 'w':
                    score += pieceScore[square[1]] + piecePositionScore * .2
                elif square[0] == 'b':
                    score -= pieceScore[square[1]] + piecePositionScore * .2
    return score



def score_material(board):
    score = 0
    for row in board:
        for square in row:
            if square[0] == 'w':
                score += pieceScore[square[1]] 
            elif square[0] == 'b':
                score -= pieceScore[square[1]]

    return score