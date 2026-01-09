import customtkinter as ctk
import random
from PIL import Image, ImageTk
import os

# ---------- CONFIG ----------
BOARD_WIDTH = 36
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

        win_w = BOARD_WIDTH * CELL_SIZE + 60
        win_h = BOARD_HEIGHT * CELL_SIZE + 160
        self.root.geometry(f"{win_w}x{win_h}")
        self.root.update()

        # Game state
        self.direction = "Right"
        self.next_direction = "Right"
        self.snake = []
        self.food = None
        self.running = False
        self.score = 0
        self.current_screen = "menu"
        self.bg_offset_x = 0
        self.bg_offset_y = 0
        self.bg_speed_x = 0.5
        self.bg_speed_y = 0.3

        self.bg_pil_image = None
        self.bg_image_tk = None
        self.bg_image_id = None
        self.snake_skin_img = None
        self.ui_frames = []
        self.canvas = None

        self.load_background()
        self.show_main_menu()
        self.root.bind("<Key>", self.on_key_press)
        self.root.focus_set()
        self.start_bg_animation()

    def safe_destroy_ui(self):
        for frame in self.ui_frames[:]:
            try:
                frame.destroy()
                self.ui_frames.remove(frame)
            except:
                pass

    def load_background(self):
        try:
            if os.path.exists(BG_IMAGE_PATH):
                w, h = BOARD_WIDTH * CELL_SIZE * 2, BOARD_HEIGHT * CELL_SIZE * 2
                self.bg_pil_image = Image.open(BG_IMAGE_PATH).resize((w, h), Image.Resampling.LANCZOS)
                self.bg_image_tk = ImageTk.PhotoImage(self.bg_pil_image)
                print("Background loaded successfully")
        except Exception as e:
            print(f"BG load error: {e}")

    def ensure_canvas(self):
        if self.canvas is None or not self.canvas.winfo_exists():
            canvas_w = BOARD_WIDTH * CELL_SIZE
            canvas_h = BOARD_HEIGHT * CELL_SIZE
            self.canvas = ctk.CTkCanvas(self.root, width=canvas_w, height=canvas_h, bg="#000000", highlightthickness=0)
            self.canvas.pack(padx=20, pady=20)

            if self.bg_image_tk and self.bg_image_id is None:
                self.bg_image_id = self.canvas.create_image(0, 0, image=self.bg_image_tk, anchor="nw", tags="bg")

        return self.canvas

    def clear_game_elements(self):
        if self.canvas:
            self.canvas.delete("snake", "food", "gameover", "grid")

    def clear_menu_elements(self):
        if self.canvas:
            self.canvas.delete("menu_overlay", "menu_title", "start_btn")

    def draw_grid(self):
        if not self.canvas: return
        self.canvas.delete("grid")
        for x in range(0, BOARD_WIDTH * CELL_SIZE, CELL_SIZE):
            self.canvas.create_line(x, 0, x, BOARD_HEIGHT * CELL_SIZE, fill="#444444", tags="grid")
        for y in range(0, BOARD_HEIGHT * CELL_SIZE, CELL_SIZE):
            self.canvas.create_line(0, y, BOARD_WIDTH * CELL_SIZE, y, fill="#444444", tags="grid")

    def start_bg_animation(self):
        if self.canvas and self.canvas.winfo_exists() and self.bg_image_id:
            self.bg_offset_x = (self.bg_offset_x + self.bg_speed_x) % (BOARD_WIDTH * CELL_SIZE)
            self.bg_offset_y = (self.bg_offset_y + self.bg_speed_y) % (BOARD_HEIGHT * CELL_SIZE)
            self.canvas.coords(self.bg_image_id, self.bg_offset_x, self.bg_offset_y)
        self.root.after(50, self.start_bg_animation)

    def show_main_menu(self):
        self.safe_destroy_ui()
        self.current_screen = "menu"
        self.running = False

        self.canvas = self.ensure_canvas()
        self.clear_game_elements()
        self.clear_menu_elements()
        self.draw_grid()

        # Purple overlay
        overlay_w, overlay_h = BOARD_WIDTH * CELL_SIZE, BOARD_HEIGHT * CELL_SIZE
        self.canvas.create_rectangle(0, 0, overlay_w, overlay_h, fill="#3a0f72", stipple="gray25", outline="", tags="menu_overlay")

        # Title
        title_x, title_y = overlay_w // 2, overlay_h // 3
        self.canvas.create_text(title_x + 4, title_y + 4, text="SNAKE GAME", fill="#1a0533", font=("Impact", 52, "bold"), tags="menu_title")
        self.canvas.create_text(title_x, title_y, text="SNAKE GAME", fill="#aa44ff", font=("Impact", 52, "bold"), tags="menu_title")
        self.canvas.create_text(title_x - 2, title_y - 2, text="SNAKE GAME", fill="#ff88ff", font=("Impact", 52, "bold"), tags="menu_title")
        self.canvas.create_text(title_x, title_y + 80, text="RETRO ARCADE EDITION", fill="#cc88ff", font=("Courier New", 24, "bold"), tags="menu_title")

        # START Button
        btn_w, btn_h = 260, 75
        btn_x = title_x - btn_w // 2
        btn_y = title_y + 160
        self.canvas.create_rectangle(btn_x + 8, btn_y + 8, btn_x + btn_w + 4, btn_y + btn_h + 4, fill="#660000", outline="", tags="start_btn")
        self.canvas.create_rectangle(btn_x, btn_y, btn_x + btn_w, btn_y + btn_h, fill="#cc0000", outline="#990000", width=6, tags="start_btn")
        self.canvas.create_rectangle(btn_x + 6, btn_y + 6, btn_x + btn_w - 6, btn_y + 25, fill="#ff6666", outline="", tags="start_btn")
        self.canvas.create_text(btn_x + btn_w//2 + 3, btn_y + btn_h//2 + 3, text="START GAME", fill="#440000", font=("Impact", 26, "bold"), tags="start_btn")
        self.canvas.create_text(btn_x + btn_w//2, btn_y + btn_h//2, text="START GAME", fill="#ffffff", font=("Impact", 26, "bold"), tags="start_btn")

        self.canvas.tag_bind("start_btn", "<Button-1>", self.on_start_click)
        self.canvas.tag_bind("start_btn", "<Enter>", lambda e: self.button_hover("start_btn", True))
        self.canvas.tag_bind("start_btn", "<Leave>", lambda e: self.button_hover("start_btn", False))

    def button_hover(self, tag, hover):
        if self.canvas:
            color = "#ff3333" if hover else "#990000"
            self.canvas.itemconfig(tag, outline=color)

    def on_start_click(self, event):
        self.show_game_screen()

    def show_game_screen(self):
        self.current_screen = "game"
        self.canvas = self.ensure_canvas()
        self.clear_menu_elements()
        self.draw_grid()
        self.build_game_ui()
        self.reset_game()

    def build_game_ui(self):
        self.safe_destroy_ui()

        # Top frame
        top_frame = ctk.CTkFrame(self.root)
        top_frame.pack(fill="x", padx=20, pady=(20, 5))
        self.ui_frames.append(top_frame)

        ctk.CTkLabel(top_frame, text="Score:", font=ctk.CTkFont(size=20, weight="bold")).pack(side="left", padx=(25, 10))
        self.score_label = ctk.CTkLabel(top_frame, text="0", font=ctk.CTkFont(size=28, weight="bold"))
        self.score_label.pack(side="left", padx=5)
        self.status_label = ctk.CTkLabel(top_frame, text="Ready", font=ctk.CTkFont(size=20, weight="bold"))
        self.status_label.pack(side="right", padx=(10, 25))

        # Canvas
        self.canvas.pack(padx=20, pady=(0, 10))

        # Bottom buttons - BIG & VISIBLE
        bottom_frame = ctk.CTkFrame(self.root)
        bottom_frame.pack(fill="x", padx=20, pady=(0, 20))
        self.ui_frames.append(bottom_frame)

        self.start_button = ctk.CTkButton(bottom_frame, text="START", width=130, height=45, font=ctk.CTkFont(size=18, weight="bold"), command=self.start_game)
        self.start_button.pack(side="left", padx=(25, 10))

        self.reset_button = ctk.CTkButton(bottom_frame, text="RESET", width=130, height=45, font=ctk.CTkFont(size=18, weight="bold"), command=self.reset_game)
        self.reset_button.pack(side="left", padx=10)

        self.menu_button = ctk.CTkButton(bottom_frame, text="MENU", width=130, height=45, font=ctk.CTkFont(size=18, weight="bold"), command=self.show_main_menu)
        self.menu_button.pack(side="right", padx=(10, 25))

        self.load_snake_skin()

    def load_snake_skin(self):
        try:
            if os.path.exists(SNAKE_SKIN_PATH) and not self.snake_skin_img:
                img = Image.open(SNAKE_SKIN_PATH).resize((CELL_SIZE, CELL_SIZE), Image.Resampling.LANCZOS)
                self.snake_skin_img = ImageTk.PhotoImage(img)
        except:
            pass

    def normalize_pos(self, x, y):
        return (x % BOARD_WIDTH, y % BOARD_HEIGHT)

    def start_game(self):
        if self.running or self.current_screen != "game": return
        self.reset_game()
        self.running = True
        self.set_status("Running")
        self.game_loop()

    def reset_game(self):
        if self.current_screen != "game": return
        self.running = False
        self.direction = "Right"
        self.next_direction = "Right"
        self.score = 0
        if self.score_label:
            self.score_label.configure(text="0")
        self.clear_game_elements()
        self.draw_grid()
        mid_x, mid_y = BOARD_WIDTH // 2, BOARD_HEIGHT // 2
        self.snake = [(mid_x - 1, mid_y), (mid_x, mid_y)]
        self.draw_snake()
        self.place_food()
        self.set_status("Ready")

    def set_status(self, text):
        if self.status_label:
            self.status_label.configure(text=text)

    def place_food(self):
        while True:
            fx = random.randint(0, BOARD_WIDTH - 1)
            fy = random.randint(0, BOARD_HEIGHT - 1)
            if (fx, fy) not in self.snake:
                self.food = (fx, fy)
                self.draw_food()
                break

    def on_key_press(self, event):
        if self.current_screen != "game": return
        key = event.keysym
        if key not in ("Up", "Down", "Left", "Right"): return
        opposite = {"Up": "Down", "Down": "Up", "Left": "Right", "Right": "Left"}
        if opposite[key] != self.direction:
            self.next_direction = key

    def game_loop(self):
        if not self.running or self.current_screen != "game": return
        self.direction = self.next_direction
        head_x, head_y = self.snake[-1]
        if self.direction == "Up": head_y -= 1
        elif self.direction == "Down": head_y += 1
        elif self.direction == "Left": head_x -= 1
        elif self.direction == "Right": head_x += 1
        new_head = self.normalize_pos(head_x, head_y)
        if new_head in self.snake[:-1]:
            self.game_over()
            return
        self.snake.append(new_head)
        if self.food and new_head == self.food:
            self.score += 10
            if self.score_label:
                self.score_label.configure(text=str(self.score))
            self.place_food()
        else:
            self.snake.pop(0)
        self.draw_snake()
        self.root.after(GAME_SPEED, self.game_loop)

    def draw_snake(self):
        if not self.canvas: return
        self.canvas.delete("snake")
        if not self.snake_skin_img or not self.snake: return
        for i, (x, y) in enumerate(self.snake):
            cx = x * CELL_SIZE + CELL_SIZE // 2
            cy = y * CELL_SIZE + CELL_SIZE // 2
            self.canvas.create_image(cx, cy, image=self.snake_skin_img, tags="snake")
        r = CELL_SIZE // 2
        hx, hy = self.snake[-1]
        hx, hy = hx * CELL_SIZE + CELL_SIZE // 2, hy * CELL_SIZE + CELL_SIZE // 2
        self.canvas.create_oval(hx - r + 2, hy - r + 2, hx + r - 2, hy + r - 2, fill="#004000", outline="", tags="snake")
        self.canvas.create_oval(hx - r + 4, hy - r + 4, hx + r - 6, hy, fill="#66ff66", outline="", tags="snake")
        tx, ty = self.snake[0]
        tx, ty = tx * CELL_SIZE + CELL_SIZE // 2, ty * CELL_SIZE + CELL_SIZE // 2
        self.canvas.create_oval(tx - r + 2, ty - r + 2, tx + r - 2, ty + r - 2, fill="#003300", outline="", tags="snake")
        self.canvas.create_oval(tx - r + 4, ty, tx + r - 6, ty + r - 4, fill="#55dd55", outline="", tags="snake")

    def draw_food(self):
        if not self.canvas or not self.food: return
        self.canvas.delete("food")
        fx, fy = self.food
        x1, y1 = fx * CELL_SIZE, fy * CELL_SIZE
        x2, y2 = x1 + CELL_SIZE, y1 + CELL_SIZE
        self.canvas.create_oval(x1 + 2, y1 + 2, x2 - 2, y2 - 2, fill="#ff4444", outline="black", width=1, tags="food")
        self.canvas.create_oval(x1 + 4, y1 + 4, x1 + CELL_SIZE // 2, y1 + CELL_SIZE // 2, fill="#ffbbbb", outline="", tags="food")
        self.canvas.create_oval(x1 + CELL_SIZE // 3, y1 + CELL_SIZE // 3, x2 - 3, y2 - 3, outline="#770000", width=2, tags="food")

    def game_over(self):
        self.running = False
        self.set_status("Game Over")
        if not self.canvas: return
        w, h = BOARD_WIDTH * CELL_SIZE, BOARD_HEIGHT * CELL_SIZE
        self.canvas.create_rectangle(0, 0, w, h, fill="#6a0dad", stipple="gray50", outline="", tags="gameover")
        tx, ty = w//2, h//2
        self.canvas.create_text(tx + 3, ty + 3, text="GAME OVER", fill="#400000", font=("Impact", 42, "bold"), tags="gameover")
        self.canvas.create_text(tx, ty, text="GAME OVER", fill="#ff5555", font=("Impact", 42, "bold"), tags="gameover")
        self.canvas.create_text(tx - 2, ty - 2, text="GAME OVER", fill="#ffe0e0", font=("Impact", 42, "bold"), tags="gameover")
        self.canvas.create_text(tx, ty + 55, text=f"Score: {self.score}", fill="#ffffff", font=("Calibri", 26, "bold"), tags="gameover")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = SnakeGameApp()
    app.run()
