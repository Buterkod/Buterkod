import tkinter as tk


class PixelPlatformer:

  def __init__(self, root):
    self.root = root
    self.root.title("Пиксельный Платформер")
    self.canvas = tk.Canvas(root, width=500, height=400, bg="#87CEEB")
    self.canvas.pack()

    self.score = 0
    self.score_lbl = self.canvas.create_text(
        70, 20, text="Очки: 0", font=("Arial", 14, "bold"), fill="white"
    )

    self.player = self.canvas.create_rectangle(
        50, 280, 80, 320, fill="#d4a373", outline="#bc6c25", width=2
    )
    self.ground = self.canvas.create_rectangle(
        0, 350, 500, 400, fill="#283618", outline=""
    )
    self.platforms = [
        self.canvas.create_rectangle(
            150, 260, 280, 275, fill="#dda15e", outline=""
        ),
        self.canvas.create_rectangle(
            320, 180, 450, 195, fill="#dda15e", outline=""
        ),
        self.canvas.create_rectangle(
            80, 130, 200, 145, fill="#dda15e", outline=""
        ),
    ]

    self.y_velocity = 0
    self.is_jumping = False

    self.keys = {}
    self.root.bind("<KeyPress>", lambda e: self.keys.update({e.keysym: True}))
    self.root.bind(
        "<KeyRelease>", lambda e: self.keys.pop(e.keysym, None)
    )

    self.update_physics()

  def update_physics(self):
    dx = 0
    if "a" in self.keys or "Left" in self.keys:
      dx = -6
    if "d" in self.keys or "Right" in self.keys:
      dx = 6
    if (
        "w" in self.keys
        or "Space" in self.keys
        or "Up" in self.keys
        and not self.is_jumping
    ):
      # Проверка на прыжок
      pass

    # Исправленный блок обработки прыжка по клавишам
    if ("w" in self.keys or "Up" in self.keys or "space" in self.keys) and not self.is_jumping:
      self.y_velocity = -13
      self.is_jumping = True

    self.y_velocity += 0.8
    self.canvas.move(self.player, dx, self.y_velocity)

    p_coords = self.canvas.coords(self.player)
    g_coords = self.canvas.coords(self.ground)

    if p_coords[3] >= g_coords[1]:
      self.canvas.coords(
          self.player,
          p_coords[0],
          g_coords[1] - 40,
          p_coords[2],
          g_coords[1],
      )
      self.y_velocity = 0
      self.is_jumping = False

    for plat in self.platforms:
      pl_coords = self.canvas.coords(plat)
      if (
          p_coords[2] > pl_coords[0]
          and p_coords[0] < pl_coords[2]
          and p_coords[3] >= pl_coords[1]
          and p_coords[3] - self.y_velocity <= pl_coords[1]
          and self.y_velocity > 0
      ):
        self.canvas.coords(
            self.player,
            p_coords[0],
            pl_coords[1] - 40,
            p_coords[2],
            pl_coords[1],
        )
        self.y_velocity = 0
        self.is_jumping = False
        self.score += 10
        self.canvas.itemconfig(self.score_lbl, text=f"Очки: {self.score}")

    if p_coords[0] < 0:
      self.canvas.move(self.player, -p_coords[0], 0)
    elif p_coords[2] > 500:
      self.canvas.move(self.player, 500 - p_coords[2], 0)

    self.root.after(20, self.update_physics)


root = tk.Tk()
game = PixelPlatformer(root)
root.mainloop()