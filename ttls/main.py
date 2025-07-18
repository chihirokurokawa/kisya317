
import pyxel
import random
import copy

# --- 定数 ---
SCREEN_WIDTH = 160
SCREEN_HEIGHT = 200
# タイルサイズを小さくし、ボードを細かく、高くする
TILE_SIZE = 5
BOARD_WIDTH = 16 # (16 * 5 = 80px)
BOARD_HEIGHT = 40 # (40 * 5 = 200px), 画面の高さ一杯まで
# FALL_SPEEDはレベルに応じて可変にする
INITIAL_FALL_SPEED = 30

# --- テトリミノの形 ---
TETROMINOES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1], [1, 1]],  # O
    [[0, 1, 0], [1, 1, 1]],  # T
    [[0, 1, 1], [1, 1, 0]],  # S
    [[1, 1, 0], [0, 1, 1]],  # Z
    [[1, 0, 0], [1, 1, 1]],  # J
    [[0, 0, 1], [1, 1, 1]],  # L
]

# --- テトリミノの色 ---
TETROMINO_COLORS = [2, 10, 11, 12, 13, 14, 5]

class Game:
    def __init__(self):
        self.board = [[0 for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]
        self.frame_count = 0
        self.score = 0
        self.game_over = False

        # レベルシステム
        self.level = 1
        self.next_level_score = 1000
        self.fall_speed = INITIAL_FALL_SPEED

        self.held_tetromino_shape = None
        self.can_hold = True

        self.next_tetromino_shape = random.choice(TETROMINOES)
        self.new_tetromino()

    def new_tetromino(self):
        self.current_tetromino_shape = self.next_tetromino_shape
        self.current_tetromino_color = TETROMINO_COLORS[TETROMINOES.index(self.current_tetromino_shape)]
        self.next_tetromino_shape = random.choice(TETROMINOES)
        self.current_x = BOARD_WIDTH // 2 - len(self.current_tetromino_shape[0]) // 2
        self.current_y = 0
        self.can_hold = True

        if not self.is_valid_position(self.current_tetromino_shape, self.current_x, self.current_y):
            self.game_over = True

    def is_valid_position(self, shape, x, y):
        for row_idx, row in enumerate(shape):
            for col_idx, cell in enumerate(row):
                if cell != 0:
                    board_x = x + col_idx
                    board_y = y + row_idx
                    if not (0 <= board_x < BOARD_WIDTH and 0 <= board_y < BOARD_HEIGHT and self.board[board_y][board_x] == 0):
                        return False
        return True

    def place_tetromino(self):
        shape = self.current_tetromino_shape
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell != 0:
                    self.board[self.current_y + y][self.current_x + x] = self.current_tetromino_color
        self.check_and_clear_lines()
        self.new_tetromino()

    def check_and_clear_lines(self):
        lines_cleared = 0
        new_board = [row for row in self.board if 0 in row]
        lines_cleared = BOARD_HEIGHT - len(new_board)
        for _ in range(lines_cleared):
            new_board.insert(0, [0 for _ in range(BOARD_WIDTH)])
        self.board = new_board
        if lines_cleared > 0:
            self.score += [0, 100, 300, 500, 800][lines_cleared]

        # レベルアップ処理
        while self.score >= self.next_level_score:
            self.level += 1
            self.next_level_score += 1000
            self.fall_speed = max(3, self.fall_speed - 2) # 落下速度アップ (最低速度は3)

    def hold(self):
        if not self.can_hold: return
        self.can_hold = False
        if self.held_tetromino_shape is None:
            self.held_tetromino_shape = self.current_tetromino_shape
            self.new_tetromino()
        else:
            self.held_tetromino_shape, self.current_tetromino_shape = self.current_tetromino_shape, self.held_tetromino_shape
            self.current_tetromino_color = TETROMINO_COLORS[TETROMINOES.index(self.current_tetromino_shape)]
            self.current_x = BOARD_WIDTH // 2 - len(self.current_tetromino_shape[0]) // 2
            self.current_y = 0

    def update(self):
        if self.game_over: return

        self.frame_count += 1

        # --- 入力処理 ---
        if pyxel.btnp(pyxel.KEY_LEFT):
            if self.is_valid_position(self.current_tetromino_shape, self.current_x - 1, self.current_y): self.current_x -= 1
        if pyxel.btnp(pyxel.KEY_RIGHT):
            if self.is_valid_position(self.current_tetromino_shape, self.current_x + 1, self.current_y): self.current_x += 1
        if pyxel.btnp(pyxel.KEY_DOWN):
            if self.is_valid_position(self.current_tetromino_shape, self.current_x, self.current_y + 1): self.current_y += 1
        
        if pyxel.btnp(pyxel.KEY_UP): # ハードドロップ
            while self.is_valid_position(self.current_tetromino_shape, self.current_x, self.current_y + 1):
                self.current_y += 1
            self.place_tetromino()

        if pyxel.btnp(pyxel.KEY_SPACE): # 回転
            rotated_shape = list(zip(*self.current_tetromino_shape[::-1]))
            if self.is_valid_position(rotated_shape, self.current_x, self.current_y): self.current_tetromino_shape = rotated_shape
        
        if pyxel.btnp(pyxel.KEY_C): self.hold()

        # 自然落下 (レベルに応じて速度変更)
        if self.frame_count % self.fall_speed == 0:
            if self.is_valid_position(self.current_tetromino_shape, self.current_x, self.current_y + 1):
                self.current_y += 1
            else:
                self.place_tetromino()

    def draw_tetromino(self, shape, x, y, color, offset_x=0, offset_y=0, ghost=False):
        for row_idx, row in enumerate(shape):
            for col_idx, cell in enumerate(row):
                if cell != 0:
                    px = offset_x + (x + col_idx) * TILE_SIZE
                    py = offset_y + (y + row_idx) * TILE_SIZE
                    if ghost:
                        pyxel.rectb(px, py, TILE_SIZE, TILE_SIZE, color)
                    else:
                        pyxel.rect(px, py, TILE_SIZE, TILE_SIZE, color)

    def draw(self):
        board_offset_x = (SCREEN_WIDTH // 2) - (BOARD_WIDTH * TILE_SIZE) // 2
        for y in range(BOARD_HEIGHT):
            for x in range(BOARD_WIDTH):
                if self.board[y][x] != 0:
                    self.draw_tetromino([[1]], x, y, self.board[y][x], board_offset_x)

        if not self.game_over:
            # ゴーストピース
            ghost_y = self.current_y
            while self.is_valid_position(self.current_tetromino_shape, self.current_x, ghost_y + 1):
                ghost_y += 1
            self.draw_tetromino(self.current_tetromino_shape, self.current_x, ghost_y, self.current_tetromino_color, board_offset_x, ghost=True)
            
            # 現在のテトリミノ
            self.draw_tetromino(self.current_tetromino_shape, self.current_x, self.current_y, self.current_tetromino_color, board_offset_x)

        # UI
        pyxel.text(5, 5, f"SCORE\n{self.score}", 7)
        pyxel.text(5, 25, f"LEVEL\n{self.level}", 7) # レベル表示
        pyxel.text(SCREEN_WIDTH - 45, 5, "NEXT", 7)
        self.draw_tetromino(self.next_tetromino_shape, (SCREEN_WIDTH - 45) // TILE_SIZE, 3, TETROMINO_COLORS[TETROMINOES.index(self.next_tetromino_shape)])

        pyxel.text(5, 45, "HOLD", 7)
        if self.held_tetromino_shape:
            self.draw_tetromino(self.held_tetromino_shape, 5 // TILE_SIZE, 11, TETROMINO_COLORS[TETROMINOES.index(self.held_tetromino_shape)])

        if self.game_over:
            pyxel.text(SCREEN_WIDTH // 2 - 20, SCREEN_HEIGHT // 2, "GAME OVER", pyxel.frame_count % 16)
            pyxel.text(SCREEN_WIDTH // 2 - 35, SCREEN_HEIGHT // 2 + 10, "PRESS R TO RESTART", 7)

class App:
    def __init__(self):
        pyxel.init(SCREEN_WIDTH, SCREEN_HEIGHT, title="Modern Tetris")
        self.game = Game()
        pyxel.run(self.update, self.draw)

    def update(self):
        if pyxel.btnp(pyxel.KEY_Q): pyxel.quit()
        if self.game.game_over and pyxel.btnp(pyxel.KEY_R): self.game = Game()
        self.game.update()

    def draw(self):
        pyxel.cls(1)
        board_offset_x = (SCREEN_WIDTH // 2) - (BOARD_WIDTH * TILE_SIZE) // 2
        
        # プレイエリアの枠線
        board_pixel_height = BOARD_HEIGHT * TILE_SIZE
        board_pixel_width = BOARD_WIDTH * TILE_SIZE
        pyxel.rectb(board_offset_x - 1, -1, board_pixel_width + 2, board_pixel_height + 2, 0)
        
        self.game.draw()

App()
