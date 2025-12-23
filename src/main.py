import customtkinter as ctk
import random
from PIL import Image, ImageTk  # pip install pillow

# ---------- CONFIG ----------

BOARD_WIDTH = 30
BOARD_HEIGHT = 20
CELL_SIZE = 20
GAME_SPEED = 120

BG_IMAGE_PATH = r"D:\Project\SnakeGame\Stock game image\bg_pic.jpg"
SNAKE_SKIN_PATH = r"D:\Project\SnakeGame\Stock game image\snake_skin.jpg"


class SnakeGameApp:
    def __init__(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.root = ctk.CTk()
        self.root.title("Snake Game")
        self.root.resizable(False, False)

        win_w = BOARD_WIDTH * CELL_SIZE + 40
        win_h = BOARD_HEIGHT * CELL_SIZE + 120
        self.root.geometry(f"{win_w}x{win_h}")

        # game state
        self.direction = "Right"
        self.next_direction = "Right"
        self.snake = []
        self.food = None
        self.running = False
        self.score = 0

        # images
        self.bg_image = None
        self.bg_image_id = None
        self.snake_skin_img = None  # texture for segments

        self.build_layout()
        self.root.bind("<Key>", self.on_key_press)

    # ---------- UI LAYOUT ----------

    def build_layout(self):
        top = ctk.CTkFrame(self.root)
        top.pack(fill="x", padx=10, pady=10)

        self.score_label = ctk.CTkLabel(top, text="Score: 0")
        self.score_label.pack(side="left")

        self.status_label = ctk.CTkLabel(top, text="Ready")
        self.status_label.pack(side="right")

        canvas_width = BOARD_WIDTH * CELL_SIZE
        canvas_height = BOARD_HEIGHT * CELL_SIZE

        self.canvas = ctk.CTkCanvas(
            self.root,
            width=canvas_width,
            height=canvas_height,
            bg="#000000",
            highlightthickness=0,
        )
        self.canvas.pack(padx=10, pady=(0, 10))

        bottom = ctk.CTkFrame(self.root)
        bottom.pack(fill="x", padx=10, pady=(0, 10))

        self.start_button = ctk.CTkButton(bottom, text="Start", command=self.start_game)
        self.start_button.pack(side="left")

        self.reset_button = ctk.CTkButton(bottom, text="Reset", command=self.reset_game)
        self.reset_button.pack(side="left", padx=(10, 0))

        self.load_background()
        self.load_snake_skin()
        self.draw_grid()

    def load_background(self):
        img = Image.open(BG_IMAGE_PATH)
        img = img.resize((BOARD_WIDTH * CELL_SIZE, BOARD_HEIGHT * CELL_SIZE), Image.LANCZOS)
        self.bg_image = ImageTk.PhotoImage(img)
        self.bg_image_id = self.canvas.create_image(0, 0, image=self.bg_image, anchor="nw")

    def load_snake_skin(self):
        """Load and resize the snake skin texture once, reused for all segments."""
        img = Image.open(SNAKE_SKIN_PATH)
        img = img.resize((CELL_SIZE, CELL_SIZE), Image.LANCZOS)
        self.snake_skin_img = ImageTk.PhotoImage(img)

    def draw_grid(self):
        for x in range(0, BOARD_WIDTH * CELL_SIZE, CELL_SIZE):
            self.canvas.create_line(x, 0, x, BOARD_HEIGHT * CELL_SIZE, fill="#444444")
        for y in range(0, BOARD_HEIGHT * CELL_SIZE, CELL_SIZE):
            self.canvas.create_line(0, y, BOARD_WIDTH * CELL_SIZE, y, fill="#444444")

    def set_status(self, text: str):
        self.status_label.configure(text=text)
        self.root.update_idletasks()

    # ---------- GAME CONTROL ----------

    def start_game(self):
        if self.running:
            return
        self.reset_game()
        self.running = True
        self.set_status("Running")
        self.game_loop()

    def reset_game(self):
        self.running = False
        self.direction = "Right"
        self.next_direction = "Right"
        self.score = 0
        self.score_label.configure(text="Score: 0")

        self.canvas.delete("all")
        self.load_background()
        self.draw_grid()

        mid_x = BOARD_WIDTH // 2
        mid_y = BOARD_HEIGHT // 2
        self.snake = [(mid_x - 1, mid_y), (mid_x, mid_y)]
        self.draw_snake()

        self.place_food()
        self.set_status("Ready")

    # ---------- DRAWING (TEXTURED + ROUNDED 3D ENDS) ----------

    def draw_snake(self):
        self.canvas.delete("snake")
        if not self.snake_skin_img or not self.snake:
            return

        # draw textured body segments
        for (x, y) in self.snake:
            cx = x * CELL_SIZE + CELL_SIZE // 2
            cy = y * CELL_SIZE + CELL_SIZE // 2
            self.canvas.create_image(
                cx,
                cy,
                image=self.snake_skin_img,
                tags="snake",
            )

        r = CELL_SIZE // 2

        # ----- rounded 3D head cap -----
        head_x, head_y = self.snake[-1]
        hx = head_x * CELL_SIZE + CELL_SIZE // 2
        hy = head_y * CELL_SIZE + CELL_SIZE // 2

        self.canvas.create_oval(
            hx - r + 2, hy - r + 2, hx + r - 2, hy + r - 2,
            fill="#004000",
            outline="",
            tags="snake",
        )
        self.canvas.create_oval(
            hx - r + 4, hy - r + 4, hx + r - 6, hy,
            fill="#66ff66",
            outline="",
            tags="snake",
        )

        # ----- rounded 3D tail cap -----
        tail_x, tail_y = self.snake[0]
        tx = tail_x * CELL_SIZE + CELL_SIZE // 2
        ty = tail_y * CELL_SIZE + CELL_SIZE // 2

        self.canvas.create_oval(
            tx - r + 2, ty - r + 2, tx + r - 2, ty + r - 2,
            fill="#003300",
            outline="",
            tags="snake",
        )
        self.canvas.create_oval(
            tx - r + 4, ty, tx + r - 6, ty + r - 4,
            fill="#55dd55",
            outline="",
            tags="snake",
        )

    def draw_food(self):
        self.canvas.delete("food")
        if not self.food:
            return

        fx, fy = self.food
        x1 = fx * CELL_SIZE
        y1 = fy * CELL_SIZE
        x2 = x1 + CELL_SIZE
        y2 = y1 + CELL_SIZE

        # base orb
        self.canvas.create_oval(
            x1 + 2, y1 + 2, x2 - 2, y2 - 2,
            fill="#ff4444",
            outline="black",
            width=1,
            tags="food",
        )

        # highlight
        self.canvas.create_oval(
            x1 + 4, y1 + 4, x1 + CELL_SIZE // 2, y1 + CELL_SIZE // 2,
            fill="#ffbbbb",
            outline="",
            tags="food",
        )

        # shadow ring
        self.canvas.create_oval(
            x1 + CELL_SIZE // 3, y1 + CELL_SIZE // 3,
            x2 - 3, y2 - 3,
            outline="#770000",
            width=2,
            tags="food",
        )

    # ---------- GAME OVER OVERLAY ----------

    def show_game_over_overlay(self):
        """Translucent purple overlay and 3D 'GAME OVER' text plus score."""
        w = BOARD_WIDTH * CELL_SIZE
        h = BOARD_HEIGHT * CELL_SIZE

        self.canvas.create_rectangle(
            0, 0, w, h,
            fill="#6a0dad",
            stipple="gray50",
            outline="",
            tags="gameover",
        )

        text_x = w // 2
        text_y = h // 2

        # back shadow
        self.canvas.create_text(
            text_x + 3, text_y + 3,
            text="GAME OVER",
            fill="#400000",
            font=("Impact", 40, "bold"),
            tags="gameover",
        )

        # main red text
        self.canvas.create_text(
            text_x, text_y,
            text="GAME OVER",
            fill="#ff5555",
            font=("Impact", 40, "bold"),
            tags="gameover",
        )

        # highlight
        self.canvas.create_text(
            text_x - 2, text_y - 2,
            text="GAME OVER",
            fill="#ffe0e0",
            font=("Impact", 40, "bold"),
            tags="gameover",
        )

        # score below
        score_text = f"Score: {self.score}"
        self.canvas.create_text(
            text_x, text_y + 50,
            text=score_text,
            fill="#ffffff",
            font=("Calibri", 24, "bold"),
            tags="gameover",
        )

    # ---------- LOGIC ----------

    def place_food(self):
        while True:
            fx = random.randint(0, BOARD_WIDTH - 1)
            fy = random.randint(0, BOARD_HEIGHT - 1)
            if (fx, fy) not in self.snake:
                self.food = (fx, fy)
                break
        self.draw_food()

    def on_key_press(self, event):
        key = event.keysym
        if key not in ("Up", "Down", "Left", "Right"):
            return
        opposite = {"Up": "Down", "Down": "Up", "Left": "Right", "Right": "Left"}
        if opposite[key] != self.direction:
            self.next_direction = key

    def game_loop(self):
        if not self.running:
            return

        self.direction = self.next_direction

        head_x, head_y = self.snake[-1]
        if self.direction == "Up":
            head_y -= 1
        elif self.direction == "Down":
            head_y += 1
        elif self.direction == "Left":
            head_x -= 1
        elif self.direction == "Right":
            head_x += 1

        new_head = (head_x, head_y)

        # wall collision
        if not (0 <= head_x < BOARD_WIDTH and 0 <= head_y < BOARD_HEIGHT):
            self.game_over()
            return

        # self collision
        if new_head in self.snake:
            self.game_over()
            return

        # move
        self.snake.append(new_head)

        # eat → grow
        if self.food and new_head == self.food:
            self.score += 10
            self.score_label.configure(text=f"Score: {self.score}")
            self.place_food()
        else:
            self.snake.pop(0)

        self.draw_snake()
        self.draw_food()

        self.root.after(GAME_SPEED, self.game_loop)

    def game_over(self):
        self.running = False
        self.set_status("Game Over")
        self.show_game_over_overlay()

    def run(self):
        self.reset_game()
        self.root.mainloop()


if __name__ == "__main__":
    app = SnakeGameApp()
    app.run()
