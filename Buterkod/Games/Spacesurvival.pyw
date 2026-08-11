import os
import random
import tkinter as tk
from PIL import Image, ImageTk  # pip install pillow


class HlebBasicsGame:

  def __init__(self, root):
    self.root = root
    self.root.title("Hleb Basics")
    self.root.attributes("-fullscreen", True)

    self.canvas = tk.Canvas(root, bg="#fdf0d5", highlightthickness=0)
    self.canvas.pack(fill=tk.BOTH, expand=True)

    self.state = "menu"
    self.score = 0
    self.toasters_left = 5
    self.time_left = 90

    self.player_x = 400
    self.player_y = 400
    self.step_speed = 25  # Шаг как в твоем примере
    self.player_size = 40

    self.menu_image = None
    self.load_menu_image()

    self.root.bind("<Key>", self.move)
    self.canvas.bind("<Button-1>", self.handle_click)

    self.update_loop()

  def load_menu_image(self):
    img_path = os.path.join("..", "Images", "menu.png")
    if not os.path.exists(img_path):
      img_path = os.path.join("Images", "menu.png")

    if os.path.exists(img_path):
      try:
        pil_img = Image.open(img_path)
        self.pil_menu_image = pil_img
        self.menu_image = ImageTk.PhotoImage(pil_img)
      except Exception as e:
        print(f"Не удалось загрузить картинку меню: {e}")

  def handle_click(self, event):
    sw = self.canvas.winfo_width()
    sh = self.canvas.winfo_height()
    cx, cy = sw // 2, sh // 2

    if self.state == "menu":
      if cx - 120 <= event.x <= cx + 120 and cy + 40 <= event.y <= cy + 110:
        self.start_gameplay()
      elif cx - 120 <= event.x <= cx + 120 and cy + 130 <= event.y <= cy + 200:
        self.root.destroy()
    elif self.state in ["gameover", "win"]:
      if cx - 110 <= event.x <= cx + 110 and cy + 60 <= event.y <= cy + 120:
        self.state = "menu"

  def start_gameplay(self):
    self.state = "gameplay"
    self.score = 0
    self.toasters_left = 5
    self.time_left = 90

    sw = self.canvas.winfo_width()
    sh = self.canvas.winfo_height()
    cx, cy = sw // 2, sh // 2

    self.player_x = cx
    self.player_y = cy + 200

    self.map_w = 1600
    self.map_h = 1200

    self.toasters = []
    for _ in range(5):
      tx = random.randint(cx - self.map_w // 2 + 100, cx + self.map_w // 2 - 100)
      ty = random.randint(cy - self.map_h // 2 + 100, cy + self.map_h // 2 - 100)
      self.toasters.append({"x": tx, "y": ty})

    self.baldi_x = cx - 300
    self.baldi_y = cy - 300
    self.baldi_speed = 3.5

  # ТОЧНО ТВОЯ ФУНКЦИЯ ХОДЬБЫ ИЗ ТВОЕГО ФАЙЛА
  def move(self, event):
    if self.state != "gameplay":
      k = event.keysym.lower()
      if k == "escape":
        self.root.destroy()
      if self.state == "menu" and k in ["space", "return"]:
        self.start_gameplay()
      return

    char = event.char.lower() if event.char else ""
    code = event.keycode

    min_x, max_x = 0, self.map_w
    min_y, max_y = 0, self.map_h

    # W / Ц
    if char in ["w", "ц"] or code == 87:
      if self.player_y - self.step_speed >= min_y:
        self.player_y -= self.step_speed

    # S / Ы
    elif char in ["s", "ы"] or code == 83:
      if self.player_y + self.step_speed + self.player_size <= max_y:
        self.player_y += self.step_speed

    # A / Ф
    elif char in ["a", "ф"] or code == 65:
      if self.player_x - self.step_speed >= min_x:
        self.player_x -= self.step_speed

    # D / В
    elif char in ["d", "в"] or code == 68:
      if self.player_x + self.step_speed + self.player_size <= max_x:
        self.player_x += self.step_speed
      
    elif event.keysym.lower() == "escape":
      self.root.destroy()

  def update_loop(self):
    self.canvas.delete("all")

    if self.state == "menu":
      self.render_menu()
    elif self.state == "gameplay":
      self.render_gameplay()
    elif self.state in ["gameover", "win"]:
      self.render_end_screen()

    self.root.after(30, self.update_loop)

  def render_menu(self):
    sw = self.canvas.winfo_width()
    sh = self.canvas.winfo_height()
    cx, cy = sw // 2, sh // 2

    if self.menu_image:
      resized_img = self.pil_menu_image.resize((sw, sh), Image.Resampling.LANCZOS)
      self.bg_tk = ImageTk.PhotoImage(resized_img)
      self.canvas.create_image(0, 0, image=self.bg_tk, anchor="nw")
    else:
      self.canvas.create_rectangle(0, 0, sw, sh, fill="#f4a261", outline="")

    self.canvas.create_rectangle(cx - 220, cy - 180, cx + 220, cy + 220, fill="#fff3b0", outline="#d4a373", width=4)

    self.canvas.create_text(
        cx, cy - 130, text="HLEB BASICS", fill="#bc6c25", font=("Arial", 32, "bold")
    )
    self.canvas.create_text(
        cx, cy - 80, text="Засунь хлебушки в тостеры\nи убеги от Хлебного Балди!", fill="#606c38", font=("Arial", 14, "bold"), justify="center"
    )

    self.canvas.create_rectangle(cx - 120, cy + 40, cx + 120, cy + 110, fill="#283618", outline="#606c38", width=3)
    self.canvas.create_text(cx, cy + 75, text="ИГРАТЬ", fill="#ffffff", font=("Arial", 18, "bold"))

    self.canvas.create_rectangle(cx - 120, cy + 130, cx + 120, cy + 200, fill="#bc4749", outline="#d90429", width=3)
    self.canvas.create_text(cx, cy + 165, text="ВЫХОД", fill="#ffffff", font=("Arial", 18, "bold"))

  def render_gameplay(self):
    sw = self.canvas.winfo_width()
    sh = self.canvas.winfo_height()
    cx, cy = sw // 2, sh // 2

    if hasattr(self, "frame_counter"):
      self.frame_counter += 1
    else:
      self.frame_counter = 0

    if self.frame_counter >= 30:
      self.time_left -= 1
      self.frame_counter = 0
      if self.time_left <= 0:
        self.state = "gameover"
        self.end_message = "ХЛЕБ ПОДГОТОВИЛСЯ К ТОСТУ БЕЗ ТЕБЯ! ИГРА ОКОНЧЕНА."
        return

    # Движение Хлебного Балди следом за нами
    b_dx = self.player_x - self.baldi_x
    b_dy = self.player_y - self.baldi_y
    b_dist = (b_dx**2 + b_dy**2)**0.5
    if b_dist > 5:
      self.baldi_x += (b_dx / b_dist) * self.baldi_speed
      self.baldi_y += (b_dy / b_dist) * self.baldi_speed

    if b_dist < 35:
      self.state = "gameover"
      self.end_message = "ХЛЕБНЫЙ БАЛДИ ПОЙМАЛ ТЕБЯ И СДЕЛАЛ ТОСТ!"
      return

    cam_x = self.player_x - cx
    cam_y = self.player_y - cy

    def tx(x):
      return x - cam_x

    def ty(y):
      return y - cam_y

    min_x, max_x = 0, self.map_w
    min_y, max_y = 0, self.map_h

    self.canvas.create_rectangle(
        tx(min_x), ty(min_y), tx(max_x), ty(max_y),
        fill="#e9d8a6", outline="#dda15e", width=6
    )

    for t in self.toasters[:]:
      dist_t = ((self.player_x - t["x"])**2 + (self.player_y - t["y"])**2)**0.5
      if dist_t < 40:
        self.toasters.remove(t)
        self.toasters_left -= 1
        self.score += 200
      else:
        rx, ry = t["x"], t["y"]
        if abs(rx - self.player_x) < sw and abs(ry - self.player_y) < sh:
          self.canvas.create_rectangle(
              tx(rx - 20), ty(ry - 15), tx(rx + 20), ty(ry + 15),
              fill="#adb5bd", outline="#495057", width=3
          )
          self.canvas.create_text(tx(rx), ty(ry), text="🍞🔥", font=("Arial", 14))

    px, py = self.player_x, self.player_y
    self.canvas.create_rectangle(
        tx(px), ty(py),
        tx(px + self.player_size), ty(py + self.player_size),
        fill="#d4a373", outline="#bc6c25", width=3
    )
    self.canvas.create_text(tx(px + self.player_size // 2), ty(py + self.player_size // 2), text="🍞", font=("Arial", 16))

    bx, by = self.baldi_x, self.baldi_y
    if abs(bx - self.player_x) < sw and abs(by - self.player_y) < sh:
      self.canvas.create_rectangle(
          tx(bx - 24), ty(by - 28), tx(bx + 24), ty(by + 28),
          fill="#bc6c25", outline="#606c38", width=4
      )
      self.canvas.create_text(tx(bx), ty(by), text="🍞👨‍🦲", font=("Arial", 18))

    self.canvas.create_rectangle(0, sh - 90, sw, sh, fill="#fefae0", outline="#bc6c25", width=4)
    self.canvas.create_text(
        180, sh - 45, text=f"ТОСТЕРОВ ОСТАЛОСЬ: {self.toasters_left}", fill="#bc6c25", font=("Arial", 16, "bold")
    )
    self.canvas.create_text(
        sw // 2, sh - 45, text=f"СЧЕТ: {self.score}", fill="#606c38", font=("Arial", 16, "bold")
    )
    self.canvas.create_text(
        sw - 180, sh - 45, text=f"ВРЕМЯ: {self.time_left}с", fill="#d90429", font=("Arial", 16, "bold")
    )

    if self.toasters_left == 0:
      self.state = "win"
      self.end_message = f"ПОБЕДА! ВЕСЬ ХЛЕБ ЗАПЕЧЕН ДО ХРУСТЯЩЕЙ КОРОЧКИ!\nСчет: {self.score}"

  def render_end_screen(self):
    sw = self.canvas.winfo_width()
    sh = self.canvas.winfo_height()
    cx, cy = sw // 2, sh // 2

    self.canvas.create_rectangle(
        cx - 220, cy - 130, cx + 220, cy + 160,
        fill="#fff3b0", outline="#bc6c25" if self.state == "gameover" else "#606c38", width=4
    )

    title = "ПОРАЖЕНИЕ" if self.state == "gameover" else "УСПЕХ!"
    color = "#d90429" if self.state == "gameover" else "#606c38"

    self.canvas.create_text(cx, cy - 75, text=title, fill=color, font=("Arial", 24, "bold"))
    self.canvas.create_text(cx, cy - 15, text=self.end_message, fill="#333333", font=("Arial", 12, "bold"), justify="center")

    self.canvas.create_rectangle(cx - 110, cy + 60, cx + 110, cy + 120, fill="#283618", outline="", width=2)
    self.canvas.create_text(cx, cy + 90, text="В МЕНЮ", fill="#ffffff", font=("Arial", 14, "bold"))


root = tk.Tk()
game = HlebBasicsGame(root)
root.mainloop()