"""
GameEngine: owns the board, turn state, and round-end logic.

You (the player) always play X and click to move. The computer always
plays O and moves automatically right after you, using a simple
random-move AI (see game/ai.py) - this is given infrastructure, not
something you need to build.

The scoreboard tracks X wins, O wins, and draws across rounds.
R starts a new round without changing the match score, while M resets
the entire match and clears the scoreboard.
"""

from game.rules import check_winner, is_board_full
from game.renderer import board_pos_to_cell
from game.ai import choose_move

HUMAN_SYMBOL = 'X'
COMPUTER_SYMBOL = 'O'


class GameEngine:
    def __init__(self):
        self.x_wins = 0
        self.o_wins = 0
        self.draws = 0
        self.starting_player = HUMAN_SYMBOL
        self._reset_round()

    def _reset_round(self, starting_player=None):
        if starting_player is not None:
            self.starting_player = starting_player
        self.board = [[None] * 3 for _ in range(3)]
        self.current_player = self.starting_player
        self.round_over = False
        self.winner = None   # 'X', 'O', or None (meaning draw, only valid when round_over)
        self._maybe_take_computer_turn()

    def _reset_match(self):
        self.x_wins = 0
        self.o_wins = 0
        self.draws = 0
        self._reset_round()

    def handle_click(self, pos):
        if self.round_over:
            return
        if self.current_player != HUMAN_SYMBOL:
            return   # not your turn - the computer is about to move (or already has)
        cell = board_pos_to_cell(pos)
        if cell is None:
            return
        row, col = cell
        if self.board[row][col] is not None:
            return
        self.board[row][col] = self.current_player
        self.check_round_end()
        if self.round_over:
            return
        self.current_player = 'O' if self.current_player == 'X' else 'X'
        self._maybe_take_computer_turn()

    def _maybe_take_computer_turn(self):
        if self.round_over or self.current_player != COMPUTER_SYMBOL:
            return
        move = choose_move(self.board)
        if move is None:
            return
        row, col = move
        self.board[row][col] = self.current_player
        self.check_round_end()
        if self.round_over:
            return
        self.current_player = 'O' if self.current_player == 'X' else 'X'

    def handle_keydown(self, key):
        import pygame
        if key == pygame.K_x:
            self._reset_round(HUMAN_SYMBOL)
        elif key == pygame.K_o:
            self._reset_round(COMPUTER_SYMBOL)
        elif key == pygame.K_r:
            self._reset_round()
        elif key == pygame.K_m:
            self._reset_match()

    def check_round_end(self):
        if self.round_over:
            return
        winner = check_winner(self.board)
        if winner:
            self.round_over = True
            self.winner = winner
            if winner == HUMAN_SYMBOL:
                self.x_wins += 1
            else:
                self.o_wins += 1
            return
        if is_board_full(self.board):
            self.round_over = True
            self.winner = None
            self.draws += 1

    def draw(self, surface, font):
        from game import renderer
        renderer.draw_board(surface, self.board)
        score_label = f"X: {self.x_wins}   O: {self.o_wins}   Draws: {self.draws}"
        renderer.draw_text(surface, font, score_label, (10, 20))
        turn_label = "Your turn (X)" if self.current_player == HUMAN_SYMBOL else "Computer's turn (O)"
        renderer.draw_text(surface, font, turn_label, (10, 50))
        renderer.draw_text(surface, font, f"Starting: {self.starting_player}   X/O: choose starter", (10, 75))

        if self.round_over:
            text = f"{self.winner} wins!" if self.winner else "Draw!"
            renderer.draw_banner(surface, font, f"{text} Press R for new round, M to reset match.")
        else:
            renderer.draw_text(surface, font, "X/O: Choose Starter   R: New Round   M: Reset Match", (10, 475))
