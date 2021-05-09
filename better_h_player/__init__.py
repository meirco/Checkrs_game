import players.simple_player as simple_player
from checkers.consts import BOARD_ROWS
from utils import INFINITY
import abstract
from checkers.consts import BACK_ROW, MY_COLORS
from checkers.consts import EM, PAWN_COLOR, KING_COLOR, OPPONENT_COLOR, MAX_TURNS_NO_JUMP
from collections import defaultdict


class Player(simple_player.Player):

    def __init__(self, setup_time, player_color, time_per_k_turns, k):
        simple_player.Player.__init__(self, setup_time, player_color, time_per_k_turns, k)

    # creating a dictionary of pieces, red and black
    def create_pieces_dict(self, state):
        pieces_dict = defaultdict(lambda: [])
        for index, (key, value) in enumerate(state.board.items()):
            if value != EM:
                if value in pieces_dict.keys():
                    pieces_dict[value] += [key]
                else:
                    pieces_dict[value] = [key]
        return pieces_dict

    # the function returns the difference value between the red and black players(according the pieces)
    def calc_players_utility(self, board):
        my_score = 0
        opponent_color = OPPONENT_COLOR[self.color]

        for (row, col), val in board.items():
            # my pawn
            if val == PAWN_COLOR[self.color]:
                my_score += abs(BACK_ROW[self.color] - row) + 1.5

            # opponent's pawn
            if val == PAWN_COLOR[opponent_color]:
                my_score -= abs(BACK_ROW[opponent_color] - row) + 1.5

            # my king
            if val == KING_COLOR[self.color]:
                my_score += BOARD_ROWS * 1.75

            # opponent's king
            if val == KING_COLOR[opponent_color]:
                my_score -= BOARD_ROWS * 1.75

        return my_score

    # to compensate player who keep pieces on the edges.
    def edges_first(self, board, color):
        my_pieces, op_pieces = 0, 0
        opponent_color = OPPONENT_COLOR[color]
        for square in board:
            # take just the edges.
            if square[1] == 7 or square[1] == 0:
                # if we find some piece on the edge
                if board[square] == PAWN_COLOR[color] or board[square] == KING_COLOR[color]:
                    my_pieces += 1
                if board[square] == PAWN_COLOR[opponent_color] or board[square] == KING_COLOR[opponent_color]:
                    op_pieces += 1
        return my_pieces,  op_pieces


    # the utility function.
    def utility(self, state):
        my_color = self.color
        if my_color == 'red':
            op_color = 'black'
        else:
            op_color = 'red'
        if len(state.get_possible_moves()) == 0:
            return INFINITY if state.curr_player != self.color else -INFINITY

        if state.turns_since_last_jump >= MAX_TURNS_NO_JUMP:
            return 0

        pieces_dict = self.create_pieces_dict(state)
        power_a = len(pieces_dict[PAWN_COLOR[self.color]]) * 10\
                  + len(pieces_dict[KING_COLOR[self.color]]) * 15
        power_b = len(pieces_dict[PAWN_COLOR[OPPONENT_COLOR[self.color]]]) * 10\
                  + len(pieces_dict[KING_COLOR[OPPONENT_COLOR[self.color]]]) * 15

        if power_a == 0:
            # we have no tools left
            return -INFINITY
        elif power_b == 0:
            # opponent has no tools left
            return INFINITY

        # defending on the back row.
        my_score_row = 0
        op_score_row = 0
        for (row, col), piece in state.board.items():
            if row == BACK_ROW[OPPONENT_COLOR[my_color]] and piece in MY_COLORS[my_color]:
                my_score_row += 5
        if my_score_row == 5 * 4:
            my_score_row += 5
            # also defending on the back row(except one case - enemy comes from the edges)
        elif my_score_row == 3 * 5:
            my_score_row += 4

        for (row, col), piece in state.board.items():
            if row == BACK_ROW[OPPONENT_COLOR[op_color]] and piece in MY_COLORS[op_color]:
                op_score_row += 5
        if op_score_row == 5 * 4:
            op_score_row += 5
        elif op_score_row == 3 * 5:
            op_score_row += 4


        # distance from promotion to be king.
        promoteA = 0
        promoteB = 0
        for (row, col), piece in state.board.items():
            if piece == PAWN_COLOR[my_color]:
                promoteA += 1 * (abs(BACK_ROW[op_color] - row))
            if piece == PAWN_COLOR[op_color]:
                promoteB += 1 * (abs(BACK_ROW[my_color] - row))

        my_sides, op_sides = self.edges_first(state.board, self.color)

        # we add it just to be more aggresive.
        my_score = self.calc_players_utility(state.board)


        return (power_a - power_b) + (my_score_row - op_score_row) - (promoteA - promoteB) + (my_sides - op_sides)



    def __repr__(self):
        return '{} {}'.format(abstract.AbstractPlayer.__repr__(self), 'better_h_player')