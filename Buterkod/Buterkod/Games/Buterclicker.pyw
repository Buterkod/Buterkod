import tkinter as tk


class SandwichClicker:

  def __init__(self, root):
    self.root = root
    self.root.title("Бутербродный Кликер")
    self.root.geometry("350x520")
    self.root.config(bg="#faedcd")

    self.crumbs = 0
    self.cps = 0
    self.click_power = 1

    self.label_score = tk.Label(
        root,
        text="Крошки: 0",
        font=("Arial", 20, "bold"),
        bg="#faedcd",
        fg="#bc6c25",
    )
    self.label_score.pack(pady=15)

    self.label_cps = tk.Label(
        root,
        text="Крошек в секунду: 0",
        font=("Arial", 11),
        bg="#faedcd",
        fg="#606c38",
    )
    self.label_cps.pack()

    self.btn = tk.Button(
        root,
        text="🥪\nЖми на бутерброд!",
        font=("Arial", 14, "bold"),
        bg="#dda15e",
        fg="white",
        activebackground="#bc6c25",
        activeforeground="white",
        command=self.click_sandwich,
        width=18,
        height=5,
        bd=4,
        relief="raised",
    )
    self.btn.pack(pady=20)

    shop_frame = tk.LabelFrame(
        root,
        text=" Магазин улучшений ",
        font=("Arial", 11, "bold"),
        bg="#faedcd",
        fg="#283618",
    )
    shop_frame.pack(fill="both", expand=True, padx=20, pady=10)

    self.btn_upgrade1 = tk.Button(
        shop_frame,
        text="🔪 Нож для масла (+1 к клику) - 15 кр.",
        font=("Arial", 10),
        bg="#fefae0",
        command=self.buy_upgrade1,
    )
    self.btn_upgrade1.pack(fill="x", padx=10, pady=5)
    self.cost1 = 15

    self.btn_upgrade2 = tk.Button(
        shop_frame,
        text="🤖 Авто-тостер (+1 кр/сек) - 50 кр.",
        font=("Arial", 10),
        bg="#fefae0",
        command=self.buy_upgrade2,
    )
    self.btn_upgrade2.pack(fill="x", padx=10, pady=5)
    self.cost2 = 50

    self.root.after(1000, self.auto_click)

  def click_sandwich(self):
    self.crumbs += self.click_power
    self.update_labels()

  def buy_upgrade1(self):
    if self.crumbs >= self.cost1:
      self.crumbs -= self.cost1
      self.click_power += 1
      self.cost1 = int(self.cost1 * 1.5)
      self.btn_upgrade1.config(
          text=f"🔪 Нож для масла (+{self.click_power} к клику) - {self.cost1} кр."
      )
      self.update_labels()

  def buy_upgrade2(self):
    if self.crumbs >= self.cost2:
      self.crumbs -= self.cost2
      self.cps += 1
      self.cost2 = int(self.cost2 * 1.6)
      self.btn_upgrade2.config(
          text=f"🤖 Авто-тостер (+{self.cps} кр/сек) - {self.cost2} кр."
      )
      self.update_labels()

  def auto_click(self):
    if self.cps > 0:
      self.crumbs += self.cps
      self.update_labels()
    self.root.after(1000, self.auto_click)

  def update_labels(self):
    self.label_score.config(text=f"Крошки: {self.crumbs}")
    self.label_cps.config(text=f"Крошек в секунду: {self.cps}")


root = tk.Tk()
game = SandwichClicker(root)
root.mainloop()