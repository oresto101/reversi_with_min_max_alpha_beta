import sys
import copy
import time

def make_move(board, row, col, color):
    board[row][col] = color
    for direction_row in [-1, 0, 1]:
        for direction_col in [-1, 0, 1]:
            if direction_row == 0 and direction_col == 0:
                continue
            r, c = row + direction_row, col + direction_col
            captured = []
            while 0 <= r < 8 and 0 <= c < 8:
                if board[r][c] == "-":
                    break
                if board[r][c] == color:
                    for row_captured, col_captured in captured:
                        board[row_captured][col_captured] = color
                    break
                captured.append((r, c))
                r += direction_row
                c += direction_col
    return board


def parse_move(move_str):
    row_str, col_str = move_str.split()
    row = int(row_str)
    col = int(col_str)
    return row, col


def is_game_ended(board):
    for col in board:
        for row in col:
            if row == '-':
                return False
    return True


def print_board(board: list[list]):
    print("  1 2 3 4 5 6 7 8")
    for i, list in enumerate(board):
        print(f"{i + 1} {' '.join(list)}")
    print()


def is_valid_move(board, row, col, current_player):
    if board[row][col] != "-":
        return False
    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            if dr == 0 and dc == 0:
                continue
            r, c = row + dr, col + dc
            captured = False
            while 0 <= r < 8 and 0 <= c < 8:
                if board[r][c] == "-":
                    break
                if board[r][c] == current_player:
                    captured = True
                    break
                r += dr
                c += dc
            if captured:
                return True

    return False


def get_legal_moves(board, color):
    legal_moves = []
    for row in range(8):
        for col in range(8):
            if is_valid_move(board, row, col, color):
                legal_moves.append((row + 1, col + 1))
    return legal_moves


def mobility_strategy(board, color):
    player_moves = get_legal_moves(board, color)
    opponent_moves = get_legal_moves(board, 'W' if color == 'B' else 'B')
    return len(player_moves) - len(opponent_moves)


def disc_count_strategy(board, color):
    player_amount = sum(row.count(color) for row in board)
    opponent_amount = sum(row.count('W' if color == 'B' else 'B') for row in board)
    return player_amount - opponent_amount


def corner_strategy(board, color):
    corner_coords = [(0, 0), (0, 7), (7, 0), (7, 7)]
    player_corners = sum(board[r][c] == color for r, c in corner_coords)
    opponent_corners = sum(1 for corner in corner_coords if board[corner[0]][corner[1]] == ('W' if color == 'B' else 'B'))
    return player_corners - opponent_corners


def heuristic(board, current_player, strategy):
    if strategy == 'dc':
        return disc_count_strategy(board, current_player)
    elif strategy == 'cs':
        return corner_strategy(board, current_player)
    elif strategy == 'ms':
        return mobility_strategy(board, current_player)


def minimax(board, player, strategy, depth, alpha, beta, maximizing):
    global total_nodes
    total_nodes += 1
    legal_moves = get_legal_moves(board, player)
    if depth == 0 or not legal_moves:
        return heuristic(board, player, strategy), None

    if player == maximizing:
        best_value = -sys.maxsize
        best_move = None
        for move in legal_moves:
            new_board = make_move(copy.deepcopy(board), move[0]-1, move[1]-1, player)
            value, _ = minimax(new_board, 'W' if player == 'B' else 'B', strategy, depth - 1, beta, alpha, maximizing)
            if value > best_value:
                best_value = value
                best_move = move
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return best_value, best_move
    else:
        best_value = sys.maxsize
        best_move = None
        for move in legal_moves:
            new_board = make_move(copy.deepcopy(board), move[0] - 1, move[1] - 1, player)
            value, _ = minimax(new_board, 'W' if player == 'B' else 'B', strategy, depth - 1, beta, alpha, maximizing)
            if value > best_value:
                best_value = value
                best_move = move
            best_value = min(best_value, value)
            beta = min(beta, value)
            if beta <= alpha:
                break
        return best_value, best_move

total_nodes = 0

def find_best_move(board, player, strategy, depth):
    global total_nodes
    total_nodes = 0
    _, best_move = minimax(board, player, strategy, depth, sys.maxsize, -sys.maxsize, player)
    return best_move


def play_game(player_color, strategy):
    start_time = time.time()
    board = [['-' for _ in range(8)] for _ in range(8)]
    current_player = 'W'
    color_to_player = {player_color: "player"}
    board[3][3] = 'W'
    board[4][4] = 'W'
    board[3][4] = 'B'
    board[4][3] = 'B'
    while not is_game_ended(board):
        if player_color in ['B', 'W'] and color_to_player[current_player] == 'player':
            print_board(board)
            legal_moves = get_legal_moves(board, current_player)
            print(f"Current legal moves for you: {legal_moves}")
            made_move = parse_move(input("Enter the coordinates of the move\n"))
            if made_move not in legal_moves:
                print("Move is not legal please try again")
                continue
            board = make_move(board, made_move[0] - 1, made_move[1] - 1, current_player)
        else:
            move = find_best_move(board, current_player, strategy, 4)
            board = make_move(board, move[0] - 1, move[1] - 1, current_player)
            print(f"Total nodes for move by ai: {total_nodes}")
        current_player = 'W' if current_player == 'B' else 'B'
    print(f"Program ran for {time.time()-start_time} s")
    white_amount, black_amount = sum(row.count('W') for row in board), sum(row.count('B') for row in board)
    print(f"White pieces: {white_amount}, Black pieces: {black_amount}")
    print("Final board")
    print_board(board)


if __name__ == '__main__':
    play_game('', 'dc')
