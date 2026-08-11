import tkinter as tk


class ToasterMaze:

  def __init__(self, root):
    self.root = root
    self.root.title("Лабиринт Тостера")
    self.canvas = tk.Canvas(root, width=350, height=350, bg="#fefae0")
    self.canvas.pack()

    self.player = self.canvas.create_rectangle(
        20, 20, 40, 40, fill="#e63946", outline=""
    )
    self.goal = self.canvas.create_rectangle(
        290, 290, 330, 330, fill="#ffb703", outline=""
    )

    self.canvas.create_text(
        310, 310, text="🍞", font=("Arial", 16), anchor="center"
    )

    self.walls = [
        self.canvas.create_rectangle(0, 55, 270, 75, fill="#dda15e"),
        self.canvas.create_rectangle(80, 130, 350, 150, fill="#dda15e"),
        self.canvas.create_rectangle(50, 210, 290, 230, fill="#dda15e"),
    ]

    self.root.bind("<Key>", self.move)

  def move(self, event):
    dx, dy = 0, 0
    key = event.keysym.lower()

    if key in ["a", "left"]:
      dx = -12
    elif key in ["d", "right"]:
      dx = 12
    elif key in ["w", "up"]:
      dy = -12
    elif key in ["s", "down"]:
      dy = 12

    self.canvas.move(self.player, dx, dy)
    p_coords = self.canvas.coords(self.player)

    g_coords = self.canvas.coords(self.goal)
    if (
        p_coords[0] < g_coords[2]
        and p_coords[2] > g_coords[0]
        and p_coords[1] < g_coords[3]
        and p_coords[3] > g_coords[1]
    ):
      self.canvas.create_rectangle(
          50, 120, 300, 220, fill="#283618", outline="#dda15e", width=3
      )
      self.canvas.create_text(
          175, 155, text="ПОБЕДА!", fill="#dda15e", font=("Arial", 22, "bold")
      )
      self.canvas.create_text(
          175,
          190,
          text="Тостер дошел до хлеба!",
          fill="white",
          font=("Arial", 11),
      )
      self.root.unbind("<Key>")


root = tk.Tk()
game = ToasterMaze(root)
root.mainloop()