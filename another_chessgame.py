import pygame

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 800
ROWS, COLS = 8, 8
SQUARE_SIZE = WIDTH // COLS

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (118, 150, 86)  # Chessboard green
LIGHT_GRAY = (200, 200, 200)  # Light gray for white pieces

# Screen setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chess Game")

# Unicode chess characters
PIECE_SYMBOLS = {
    "wp": "♙", "wr": "♖", "wn": "♘", "wb": "♗", "wq": "♕", "wk": "♔",
    "bp": "♟", "br": "♜", "bn": "♞", "bb": "♝", "bq": "♛", "bk": "♚"
}

# Chessboard setup
initial_board = [
    ["br", "bn", "bb", "bq", "bk", "bb", "bn", "br"],
    ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
    ["", "", "", "", "", "", "", ""],
    ["", "", "", "", "", "", "", ""],
    ["", "", "", "", "", "", "", ""],
    ["", "", "", "", "", "", "", ""],
    ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
    ["wr", "wn", "wb", "wq", "wk", "wb", "wn", "wr"]
]

def draw_board(screen):
    """Draw the chessboard."""
    for row in range(ROWS):
        for col in range(COLS):
            color = GREEN if (row + col) % 2 == 0 else WHITE
            pygame.draw.rect(screen, color, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

def draw_pieces(screen, board):
    """Draw the chess pieces using Unicode characters."""
    font = pygame.font.SysFont("segoeuisymbol", SQUARE_SIZE)  # Use a Unicode-supported font
    for row in range(ROWS):
        for col in range(COLS):
            piece = board[row][col]
            if piece:
                # Set the color for white and black pieces
                color = BLACK if piece[0] == "b" else LIGHT_GRAY  # White pieces are light gray
                # Render the Unicode character
                text = font.render(PIECE_SYMBOLS[piece], True, color)
                # Center the piece in the square
                text_rect = text.get_rect(center=(col * SQUARE_SIZE + SQUARE_SIZE // 2, row * SQUARE_SIZE + SQUARE_SIZE // 2))
                screen.blit(text, text_rect)

def is_valid_move(piece, start_row, start_col, end_row, end_col, board):
    """Check if a move is valid for the given piece."""
    piece_type = piece[1]
    row_diff = end_row - start_row
    col_diff = end_col - start_col

    # Check if the destination is occupied by a piece of the same color
    if board[end_row][end_col] and board[end_row][end_col][0] == piece[0]:
        return False

    # Pawn moves
    if piece_type == "p":
        direction = -1 if piece[0] == "w" else 1  # White pawns move up, black pawns move down
        # Move forward one square
        if col_diff == 0 and row_diff == direction and not board[end_row][end_col]:
            return True
        # Move forward two squares (only on first move)
        if col_diff == 0 and row_diff == 2 * direction and not board[end_row][end_col]:
            if (piece[0] == "w" and start_row == 6) or (piece[0] == "b" and start_row == 1):
                return True
        # Capture diagonally
        if abs(col_diff) == 1 and row_diff == direction and board[end_row][end_col]:
            return True
        return False

    # Rook moves
    if piece_type == "r":
        if start_row == end_row:  # Horizontal move
            step = 1 if end_col > start_col else -1
            for col in range(start_col + step, end_col, step):
                if board[start_row][col]:
                    return False
            return True
        if start_col == end_col:  # Vertical move
            step = 1 if end_row > start_row else -1
            for row in range(start_row + step, end_row, step):
                if board[row][start_col]:
                    return False
            return True
        return False

    # Knight moves
    if piece_type == "n":
        return (abs(row_diff) == 2 and abs(col_diff) == 1) or (abs(row_diff) == 1 and abs(col_diff) == 2)

    # Bishop moves
    if piece_type == "b":
        if abs(row_diff) == abs(col_diff):  # Diagonal move
            row_step = 1 if end_row > start_row else -1
            col_step = 1 if end_col > start_col else -1
            row, col = start_row + row_step, start_col + col_step
            while row != end_row and col != end_col:
                if board[row][col]:
                    return False
                row += row_step
                col += col_step
            return True
        return False

    # Queen moves
    if piece_type == "q":
        # Queen moves like a rook or a bishop
        # Check rook-like moves (horizontal/vertical)
        if start_row == end_row:  # Horizontal move
            step = 1 if end_col > start_col else -1
            for col in range(start_col + step, end_col, step):
                if board[start_row][col]:
                    return False
            return True
        if start_col == end_col:  # Vertical move
            step = 1 if end_row > start_row else -1
            for row in range(start_row + step, end_row, step):
                if board[row][start_col]:
                    return False
            return True
        # Check bishop-like moves (diagonal)
        if abs(row_diff) == abs(col_diff):  # Diagonal move
            row_step = 1 if end_row > start_row else -1
            col_step = 1 if end_col > start_col else -1
            row, col = start_row + row_step, start_col + col_step
            while row != end_row and col != end_col:
                if board[row][col]:
                    return False
                row += row_step
                col += col_step
            return True
        return False

    # King moves
    if piece_type == "k":
        return abs(row_diff) <= 1 and abs(col_diff) <= 1

    return False

def find_king(board, color):
    """Find the position of the king of the given color."""
    for row in range(ROWS):
        for col in range(COLS):
            piece = board[row][col]
            if piece and piece[0] == color and piece[1] == "k":
                return (row, col)
    return None

def is_in_check(board, color):
    """Check if the king of the given color is in check."""
    king_pos = find_king(board, color)
    if not king_pos:
        return False

    # Check if any opponent's piece can attack the king
    opponent_color = "b" if color == "w" else "w"
    for row in range(ROWS):
        for col in range(COLS):
            piece = board[row][col]
            if piece and piece[0] == opponent_color:
                if is_valid_move(piece, row, col, king_pos[0], king_pos[1], board):
                    return True
    return False

def has_legal_moves(board, color):
    """Check if the player of the given color has any legal moves."""
    for start_row in range(ROWS):
        for start_col in range(COLS):
            piece = board[start_row][start_col]
            if piece and piece[0] == color:
                for end_row in range(ROWS):
                    for end_col in range(COLS):
                        if is_valid_move(piece, start_row, start_col, end_row, end_col, board):
                            # Simulate the move to check if it leaves the king in check
                            temp_board = [row[:] for row in board]
                            temp_board[end_row][end_col] = temp_board[start_row][start_col]
                            temp_board[start_row][start_col] = ""
                            if not is_in_check(temp_board, color):
                                return True
    return False

def is_checkmate(board, color):
    """Check if the player of the given color is in checkmate."""
    return is_in_check(board, color) and not has_legal_moves(board, color)

def is_stalemate(board, color):
    """Check if the player of the given color is in stalemate."""
    return not is_in_check(board, color) and not has_legal_moves(board, color)

def show_start_screen(screen):
    """Display the starting game screen."""
    screen.fill(BLACK)
    font = pygame.font.SysFont("arial", 50)
    title = font.render("Chess Game", True, WHITE)
    instruction = font.render("Press SPACE to Start", True, WHITE)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 50))
    screen.blit(instruction, (WIDTH // 2 - instruction.get_width() // 2, HEIGHT // 2 + 50))
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
            if event.type == pygame.KEYDOWN:
                print("Key pressed:", event.key)  # Debug: Print the key code
                if event.key == pygame.K_SPACE:
                    print("SPACE key detected!")  # Debug: Confirm SPACE key
                    waiting = False
    return True

def show_end_screen(screen, winner):
    """Display the ending game screen."""
    screen.fill(BLACK)
    font = pygame.font.SysFont("arial", 50)
    if winner:
        message = font.render(f"Checkmate! {winner.capitalize()} Wins!", True, WHITE)
    else:
        message = font.render("Stalemate!", True, WHITE)
    instruction = font.render("Press R to Restart or Q to Quit", True, WHITE)
    screen.blit(message, (WIDTH // 2 - message.get_width() // 2, HEIGHT // 2 - 50))
    screen.blit(instruction, (WIDTH // 2 - instruction.get_width() // 2, HEIGHT // 2 + 50))
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return True  # Restart
                if event.key == pygame.K_q:
                    pygame.quit()
                    return False  # Quit

def main():
    """Main game loop."""
    while True:
        # Show the start screen
        if not show_start_screen(screen):
            break  # Exit if the player quits from the start screen

        print("Starting the game!")  # Debug: Confirm the game loop starts

        # Initialize the game
        board = [row[:] for row in initial_board]  # Reset the board
        selected_piece = None
        selected_pos = None
        turn = "w"  # Start with white's turn
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = pygame.mouse.get_pos()
                    col = x // SQUARE_SIZE
                    row = y // SQUARE_SIZE

                    if selected_piece:
                        # Check if the move is valid
                        if is_valid_move(selected_piece, selected_pos[0], selected_pos[1], row, col, board):
                            # Simulate the move to check if it leaves the king in check
                            temp_board = [row[:] for row in board]
                            temp_board[row][col] = temp_board[selected_pos[0]][selected_pos[1]]
                            temp_board[selected_pos[0]][selected_pos[1]] = ""
                            if not is_in_check(temp_board, turn):
                                # Move the piece
                                board[row][col] = selected_piece
                                board[selected_pos[0]][selected_pos[1]] = ""
                                selected_piece = None
                                selected_pos = None
                                turn = "b" if turn == "w" else "w"  # Switch turns
                            else:
                                # Invalid move (leaves king in check), deselect the piece
                                selected_piece = None
                                selected_pos = None
                        else:
                            # Invalid move, deselect the piece
                            selected_piece = None
                            selected_pos = None
                    else:
                        # Select a piece (only if it's the correct turn)
                        piece = board[row][col]
                        if piece and piece[0] == turn:
                            selected_piece = piece
                            selected_pos = (row, col)

            # Draw the board and pieces
            draw_board(screen)
            draw_pieces(screen, board)
            pygame.display.flip()

            # Check for checkmate or stalemate
            if is_checkmate(board, turn):
                winner = "black" if turn == "w" else "white"
                if not show_end_screen(screen, winner):
                    running = False
                else:
                    break  # Restart the game
            elif is_stalemate(board, turn):
                if not show_end_screen(screen, None):  # Stalemate
                    running = False
                else:
                    break  # Restart the game

    pygame.quit()

if __name__ == "__main__":
    main()