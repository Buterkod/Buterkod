import random
import tkinter as tk


class SnakeGame:

  def __init__(self, root):
    self.root = root
    self.root.title("Змейка 2.0")
    self.canvas = tk.Canvas(root, width=400, height=400, bg="#111111")
    self.canvas.pack()

    self.score = 0
    self.score_text = self.canvas.create_text(
        60, 20, text="Счет: 0", fill="#00ffcc", font=("Arial", 12, "bold")
    )

    self.snake = [(100, 100), (90, 100), (80, 100)]
    self.direction = "Right"
    self.food = self.spawn_food()

    self.root.bind("<Key>", self.change_direction)
    self.update_game()

  def spawn_food(self):
    x = random.randint(0, 38) * 10
    y = random.randint(0, 38) * 10
    return self.canvas.create_rectangle(
        x, y, x + 10, y + 10, fill="#ff5555", outline=""
    )

  def change_direction(self, event):
    key = event.keysym.lower()
    new_dir = self.direction
    
    if key in ["w", "up"]:
      new_dir = "Up"
    elif key in ["s", "down"]:
      new_dir = "Down"
    elif key in ["a", "left"]:
      new_dir = "Left"
    elif key in ["d", "right"]:
      new_dir = "Right"

    opposites = {"Up": "Down", "Down": "Up", "Left": "Right", "Right": "Left"}
    if opposites.get(new_dir) != self.direction:
      self.direction = new_dir

  def update_game(self):
    head_x, head_y = self.snake[0]
    if self.direction == "Left":
      head_x -= 10
    elif self.direction == "Right":
      head_x += 10
    elif self.direction == "Up":
      head_y -= 10
    elif self.direction == "Down":
      head_y += 10

    new_head = (head_x, head_y)

    if (
        head_x < 0
        or head_x >= 400
        or head_y < 0
        or head_y >= 400
        or new_head in self.snake
    ):
      self.canvas.create_rectangle(
          50, 150, 350, 250, fill="#222222", outline="#ff5555", width=3
      )
      self.canvas.create_text(
          200, 190, text="КОНЕЦ ИГРЫ", fill="#ff5555", font=("Arial", 20, "bold")
      )
      self.canvas.create_text(
          200,
          220,
          text=f"Итоговый счет: {self.score}",
          fill="white",
          font=("Arial", 12),
      )
      return

    self.snake.insert(0, new_head)

    food_coords = self.canvas.coords(self.food)
    if head_x == food_coords[0] and head_y == food_coords[1]:
      self.canvas.delete(self.food)
      self.food = self.spawn_food()
      self.score += 1
      self.canvas.itemconfig(self.score_text, text=f"Счет: {self.score}")
    else:
      self.snake.pop()

    self.canvas.delete("snake")
    for i, (x, y) in enumerate(self.snake):
      color = "#00ffcc" if i == 0 else "#00aa88"
      self.canvas.create_rectangle(
          x, y, x + 10, y + 10, fill=color, outline="", tags="snake"
      )

    self.root.after(90, self.update_game)


root = tk.Tk()
game = SnakeGame(root)
root.mainloop()