class GameState():
    def __init__(self):
        #8*8 board is list of list
        self.board = [
            ["bR","bN","bB","bQ","bK","bB","bN","bR"],
            ["bp","bp","bp","bp","bp","bp","bp","bp"],
            ["--","--","--","--","--","--","--","--"],
            ["--","--","--","--","--","--","--","--"],
            ["--","--","--","--","--","--","--","--"],
            ["--","--","--","--","--","--","--","--"],
            ["wp","wp","wp","wp","wp","wp","wp","wp"],
            ["wR","wN","wB","wQ","wK","wB","wN","wR"],
        ]
        self.white_move = True
        self.movelog = []
        self.white_king_position = (7,4)
        self.black_king_position = (0,4)
        self.checkmate = False
        self.stalemate = False
        self.enpassant_possiable = ()

        self.piece_move_functions = {
            'p': self.get_pawn_moves,
            'R': self.get_rook_moves,
            'N': self.get_knight_moves,
            'B': self.get_bishop_moves,
            'Q': self.get_queen_moves,
            'K': self.get_king_moves,
        }

    def make_move(self,move):
        self.board[move.start_row][move.start_col] = "--"
        self.board[move.end_row][move.end_col] = move.piece_moved
        self.movelog.append(move)
        self.white_move = not self.white_move
        #if king moved
        if move.piece_moved =="wK":
            self.white_king_position = (move.end_row,move.end_col)
        elif move.piece_moved =="bK":
            self.black_king_position = (move.end_row,move.end_col)
        #pawn promotion    
        if move.is_pawn_promotion:
            self.board[move.end_row][move.end_col] = move.piece_moved[0] + 'Q'

        #en-passant move
        if move.is_enpassant_move:
            self.board[move.start_row][move.end_col] == "--"
        
        #update en-passant possiable variable
        if move.piece_moved[1] =='p' and abs(move.start_row - move.end_row) == 2:
            self.enpassant_possiable = (move.start_row + move.end_row//2,move.start_col)
        else:
            self.enpassant_possiable = ()



    def undo_move(self):
        if len(self.movelog) != 0:
            move = self.movelog.pop()
            self.board[move.start_row][move.start_col] = move.piece_moved
            self.board[move.end_row][move.end_col] = move.piece_captured
            self.white_move = not self.white_move
            #if king moved
            if move.piece_moved =="wK":
                self.white_king_position = (move.start_row,move.start_col)
            elif move.piece_moved =="bK":
                self.black_king_position = (move.start_row,move.start_col)

        #undo en-passant
        if move.is_enpassant_move:
            self.board[move.end_row][move.end_col] = "--"
            self.board[move.start_row][move.end_col] = move.piece_captured
            self.enpassant_possiable = (move.end_row,move.end_col)
        #undo 2 square pawn advance
        if move.piece_moved[1] == 'p' and abs(move.start_row - move.end_row) == 2:
            self.enpassant_possiable = ()

    def get_valid_move(self):
        temp_enpassant_possiable = self.enpassant_possiable
        #1).getting all possiable move
        move = self.get_all_possiable_move()
        #2).for each move make the move
        for i in range(len(move)-1,-1,-1):
            self.make_move(move[i])
            #3).generating all opponants move
            #4).for each of your opponents move,see if they attacking your king ?
            self.white_move = not self.white_move
            if self.in_check():
                move.remove(move[i]) #5).if do they attack your king, not a valid move
            self.white_move = not self.white_move
            self.undo_move()
        if len(move) == 0:
            if self.in_check():
                self.checkmate = True
            else:
                self.stalemate = True
        else:
            self.checkmate = False
            self.stalemate = False

        self.enpassant_possiable = temp_enpassant_possiable

        return move

    def in_check(self):
        if self.white_move:
            return self.square_under_attack(self.white_king_position[0],self.white_king_position[1])
        else:
            return self.square_under_attack(self.black_king_position[0],self.black_king_position[1])


    def square_under_attack(self, r , c):
        self.white_move = not self.white_move
        oppo_moves = self.get_all_possiable_move()
        self.white_move = not self.white_move
        for move in oppo_moves:
            if move.end_row == r and move.end_col == c:
                return True
        return False

    def get_all_possiable_move(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]
                if (turn == 'w' and self.white_move) or (turn == 'b' and not self.white_move):
                    piece = self.board[r][c][1]
                    move_func = self.piece_move_functions.get(piece) 
                    if move_func:
                        move_func(r, c, moves)
        return moves


    

    def get_pawn_moves(self, r, c,moves):
        #for first pawn move of white
        if self.white_move:
            if self.board[r - 1][c] == "--":
                moves.append(Move((r,c),(r-1,c),self.board))
                if r == 6 and self.board[r - 2][c] == "--":
                    moves.append(Move((r,c),(r-2,c),self.board))
            #capture for white
            if c-1 >= 0:
                if self.board[r-1][c-1][0] =='b':
                    moves.append(Move((r,c),(r-1,c-1),self.board))  
                elif(r-1,c-1) == self.enpassant_possiable:
                    moves.append(Move((r,c),(r-1,c-1),self.board,is_enpassant_move=True))  
            if c+1 <=7:
                if self.board[r-1][c+1][0] =='b':
                    moves.append(Move((r,c),(r-1,c+1),self.board))   
                elif(r-1,c+1) == self.enpassant_possiable:
                    moves.append(Move((r,c),(r-1,c+1),self.board,is_enpassant_move=True)) 

        #for first pawn move of black
        else:
            if self.board[r + 1][c] == "--":
                moves.append(Move((r,c),(r+1,c),self.board))
                if r == 1 and self.board[r + 2][c] == "--":
                    moves.append(Move((r,c),(r+2,c),self.board))
            #capture for black
            if c-1 >= 0:
                if self.board[r+1][c-1][0] =='w':
                    moves.append(Move((r,c),(r+1,c-1),self.board)) 
                elif(r+1,c-1) == self.enpassant_possiable:
                    moves.append(Move((r,c),(r+1,c-1),self.board,is_enpassant_move=True)) 
            if c+1 <=7:
                if self.board[r+1][c+1][0] =='w':
                    moves.append(Move((r,c),(r+1,c+1),self.board))    
                elif(r+1,c+1) == self.enpassant_possiable:
                    moves.append(Move((r,c),(r+1,c+1),self.board,is_enpassant_move=True)) 
    
    def get_knight_moves(self, r, c, moves):
        knight_moves = [
            (-2, -1), (-2, 1), 
            (-1, -2), (-1, 2), 
            (1, -2), (1, 2), 
            (2, -1), (2, 1)
        ]

        ally_color = 'w' if self.white_move else 'b'

        for move in knight_moves:
            end_row = r + move[0]
            end_col = c + move[1]

            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece == "--" or end_piece[0] != ally_color:
                    moves.append(Move((r, c), (end_row, end_col), self.board))


    def get_bishop_moves(self, r, c, moves):
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]  # Diagonal directions
        enemy_color = 'b' if self.white_move else 'w'
        
        for d in directions:
            for i in range(1, 8):
                end_row = r + d[0] * i
                end_col = c + d[1] * i

                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    end_piece = self.board[end_row][end_col]

                    if end_piece == "--":
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                    elif end_piece[0] == enemy_color:
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                        break
                    else:  # Own piece
                        break
                else:  # Off the board
                    break


    def get_rook_moves(self, r, c,moves):
        directions = ((-1,0),(0,-1),(1,0),(0,1))
        enemy_color = 'b' if self.white_move else 'w'
        for d in directions:
            for i in range(1, 8):
                end_row = r + d[0] * i
                end_col = c + d[1] * i
                
                if 0 <= end_row < 8 and 0 <= end_col < 8 :
                    end_piece  = self.board[end_row][end_col]
                    if end_piece == "--":
                        moves.append(Move((r,c),(end_row,end_col),self.board))
                    elif end_piece[0] == enemy_color:
                        moves.append(Move((r,c),(end_row,end_col),self.board))
                        break
                    else:
                        break
                else:
                    break

    def get_king_moves(self, r, c, moves):
        king_moves = [
            (-1, 0), (1, 0),    # up, down
            (0, -1), (0, 1),    # left, right
            (-1, -1), (-1, 1),  # up-left, up-right
            (1, -1), (1, 1)     # down-left, down-right
        ]

        ally_color = 'w' if self.white_move else 'b'

        for d in king_moves:
            end_row = r + d[0]
            end_col = c + d[1]

            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece == "--" or end_piece[0] != ally_color:
                    moves.append(Move((r, c), (end_row, end_col), self.board))


    def get_queen_moves(self, r, c, moves):
        self.get_rook_moves(r, c, moves)
        self.get_bishop_moves(r, c, moves)

class Move():
    ranks_to_rows = {
        "1":7,
        "2":6,
        "3":5,
        "4":4,
        "5":3,
        "6":2,
        "7":1,
        "8":0,
    }

    rows_to_ranks = {v :k for k,v in ranks_to_rows.items()}

    files_to_cols = {
        "a":0,
        "b":1,
        "c":2,
        "d":3,
        "e":4,
        "f":5,
        "g":6,
        "h":7,
    }

    cols_to_files = {v:k for k,v in files_to_cols.items()}

    def __init__(self, start_sq, end_sq, board,is_enpassant_move = False):
        self.start_row = start_sq[0]
        self.start_col = start_sq[1]
        self.end_row = end_sq[0]
        self.end_col = end_sq[1]
        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]
        #pawn promotion
        self.is_pawn_promotion = (self.piece_moved == 'wp' and self.end_row == 0) or (self.piece_moved == 'bp' and self.end_row == 7)
        
        #en passant
        self.is_enpassant_move = is_enpassant_move
        if self.is_enpassant_move:
            self.piece_captured = 'wp' if self.piece_moved == 'bp' else 'bp'

        self.move_ID = self.start_row * 1000 + self.start_col * 100 + self.end_row * 10 + self.end_col

    def __eq__(self, other):
        if isinstance(other,Move):
            return self.move_ID == other.move_ID
        return False


    def get_chess_notation(self):
        return self.get_rank_file(self.start_row,self.start_col) + self.get_rank_file(self.end_row,self.end_col)

    def get_rank_file(self, r, c):
        return self.cols_to_files[c] + self.rows_to_ranks[r]
    
    