import tkinter as tk

# Настройки главного окна
root = tk.Tk()
root.title("Управление серым квадратом (WASD)")
root.geometry("800x600")
root.resizable(False, False)

# Игровое поле
canvas = tk.Canvas(root, width=800, height=600, bg="#1e1e1e")
canvas.pack()

# Параметры игрока (серый квадрат)
SQUARE_SIZE = 50
player_x = 375
player_y = 275
speed = 25  # Скорость шага

player = canvas.create_rectangle(
    player_x,
    player_y,
    player_x + SQUARE_SIZE,
    player_y + SQUARE_SIZE,
    fill="gray",
    outline="",
)


# Функция ходьбы: проверяет и символ, и физическое положение клавиши
def move(event):
    global player_x, player_y

    char = event.char.lower() if event.char else ""
    code = event.keycode

    # W / Ц
    if char in ["w", "ц"] or code == 87:
        if player_y - speed >= 0:
            player_y -= speed

    # S / Ы
    elif char in ["s", "ы"] or code == 83:
        if player_y + speed + SQUARE_SIZE <= 600:
            player_y += speed

    # A / Ф
    elif char in ["a", "ф"] or code == 65:
        if player_x - speed >= 0:
            player_x -= speed

    # D / В
    elif char in ["d", "в"] or code == 68:
        if player_x + speed + SQUARE_SIZE <= 800:
            player_x += speed

    # Обновление позиции квадрата на экране
    canvas.coords(
        player,
        player_x,
        player_y,
        player_x + SQUARE_SIZE,
        player_y + SQUARE_SIZE,
    )


# Привязка кнопок клавиатуры
root.bind("<Key>", move)

# Старт программы
root.mainloop()
