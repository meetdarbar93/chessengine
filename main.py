import pygame as p
import engine

WIDTH = HEIGHT =  512
DIMENSION = 8
SQUARE_SIZE = HEIGHT//DIMENSION
MAX_FPS = 15 #for animations
IMAGES = {}

def load_image():
    pieces = ["bQ","bN","bB","bK","bR","bp","wp","wQ","wN","wB","wK","wR"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load(f"images/{piece}.png"),(SQUARE_SIZE,SQUARE_SIZE))

def main():
    p.init()
    screen = p.display.set_mode((WIDTH,HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = engine.GameState()
    valid_move = gs.get_valid_move()
    move_made = False

    load_image()
    print(gs.board)
    running = True
    sq_selected = ()
    player_click = []

    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos()
                col = location[0]//SQUARE_SIZE
                row = location[1]//SQUARE_SIZE

                if sq_selected == (row,col):
                    sq_selected = ()
                    player_click = []

                else:
                    sq_selected = (row, col)
                    player_click.append(sq_selected)
                
                if len(player_click) ==2:
                    move = engine.Move(player_click[0],player_click[1],gs.board)
                    print(move.get_chess_notation())
                    for i in range(len(valid_move)):
                        if move == valid_move[i]:
                            gs.make_move(valid_move[i])
                            move_made = True
                            sq_selected = ()
                            player_click = []
                    if not move_made:
                        player_click = [sq_selected]

            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:
                    gs.undo_move()
                    move_made = True

        if move_made:
            valid_move = gs.get_valid_move()
            move_made = False

        draw_gamestate(screen,gs)
        clock.tick(MAX_FPS)
        p.display.flip()

def draw_gamestate(screen,gs):
    draw_board(screen)#draw scqare on board
    draw_pieces(screen,gs.board) # draw pieces on squuare

def draw_board(screen):
    colors = [p.Color("light gray"),p.Color("dark green")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r+c)%2)]
            p.draw.rect(screen,color,p.Rect(c*SQUARE_SIZE,r*SQUARE_SIZE,SQUARE_SIZE,SQUARE_SIZE))

def draw_pieces(screen,board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece],p.Rect(c*SQUARE_SIZE,r*SQUARE_SIZE,SQUARE_SIZE,SQUARE_SIZE))


if __name__ == "__main__":
    main()
