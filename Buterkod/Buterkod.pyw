import json
import os
import random
import subprocess
import sys
from PyQt6.QtCore import QPointF, Qt, QTimer, QUrl
from PyQt6.QtGui import QBrush, QColor, QLinearGradient, QPainter, QPixmap
from PyQt6.QtMultimedia import QAudioOutput, QMediaPlayer
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMenu,
    QPushButton,
    QScrollArea,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "users.json")
GAMES_DIR = os.path.join(BASE_DIR, "Games")
IMAGES_DIR = os.path.join(BASE_DIR, "Images")


def load_users():
  if os.path.exists(DB_FILE):
    try:
      with open(DB_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        fixed_data = {}
        for user, info in data.items():
          if isinstance(info, str):
            fixed_data[user] = {
                "password": info,
                "avatar": "🟩",
                "library": {},
                "friends": [],
                "requests": [],
                "dark_theme": False,
            }
          else:
            if "library" not in info:
              info["library"] = {}
            if "friends" not in info:
              info["friends"] = []
            if "requests" not in info:
              info["requests"] = []
            if "dark_theme" not in info:
              info["dark_theme"] = False
            fixed_data[user] = info
        return fixed_data
    except Exception as e:
      print(f"Ошибка загрузки пользователей: {e}")
  return {
      "admin": {
          "password": "123",
          "avatar": "🟩",
          "library": {},
          "friends": [],
          "requests": [],
          "dark_theme": False,
      }
  }


def save_users(users):
  try:
    with open(DB_FILE, "w", encoding="utf-8") as f:
      json.dump(users, f, ensure_ascii=False, indent=4)
  except Exception as e:
    print(f"Ошибка сохранения базы данных: {e}")


class AnimatedAuthBackground(QWidget):

  def __init__(self, parent=None):
    super().__init__(parent)
    self.color_shift = 0
    self.sandwiches = []

    for _ in range(25):
      self.sandwiches.append({
          "x": random.randint(0, 1200),
          "y": random.randint(0, 800),
          "speed": random.uniform(0.5, 1.5),
          "size": random.randint(24, 52),
          "angle": random.randint(0, 360),
          "rot_speed": random.uniform(-1, 1),
      })

    self.timer = QTimer(self)
    self.timer.timeout.connect(self.update_animation)
    self.timer.start(16)

  def update_animation(self):
    self.color_shift = (self.color_shift + 1) % 360
    w = self.width()
    h = self.height()

    for s in self.sandwiches:
      s["y"] -= s["speed"]
      s["angle"] += s["rot_speed"]
      if s["y"] < -60:
        s["y"] = h + 60
        s["x"] = random.randint(0, max(100, w))

    self.update()

  def resizeEvent(self, event):
    w = self.width()
    h = self.height()
    for s in self.sandwiches:
      if s["x"] > w:
        s["x"] = random.randint(0, w)
      if s["y"] > h:
        s["y"] = h
    super().resizeEvent(event)

  def paintEvent(self, event):
    painter = QPainter(self)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    gradient = QLinearGradient(0, 0, self.width(), self.height())
    c1 = QColor.fromHsv((self.color_shift) % 360, 200, 240)
    c2 = QColor.fromHsv((self.color_shift + 60) % 360, 220, 200)
    gradient.setColorAt(0, c1)
    gradient.setColorAt(1, c2)

    painter.fillRect(self.rect(), QBrush(gradient))

    painter.setFont(self.font())
    for s in self.sandwiches:
      painter.save()
      painter.translate(s["x"], s["y"])
      painter.rotate(s["angle"])
      font = painter.font()
      font.setPixelSize(s["size"])
      painter.setFont(font)
      painter.drawText(QPointF(0, 0), "🥪")
      painter.restore()


class MusicToggleButton(QPushButton):

  def __init__(self, main_window):
    super().__init__("🔊")
    self.main_window = main_window
    self.setFixedSize(45, 45)
    self.setStyleSheet(
        "background-color: rgba(255, 255, 255, 0.8);"
        " border-radius: 22px; font-size: 20px;"
    )
    self.clicked.connect(self.toggle_music)
    self.main_window.audio_output.mutedChanged.connect(self.update_icon)

  def toggle_music(self):
    is_muted = self.main_window.audio_output.isMuted()
    self.main_window.audio_output.setMuted(not is_muted)

  def update_icon(self, is_muted):
    if is_muted:
      self.setText("🔇")
    else:
      self.setText("🔊")


class LoginScreen(AnimatedAuthBackground):

  def __init__(self, main_window, switch_to_register):
    super().__init__()
    self.main_window = main_window

    main_layout = QVBoxLayout(self)

    top_row = QHBoxLayout()
    top_row.addStretch()
    self.music_btn = MusicToggleButton(main_window)
    top_row.addWidget(self.music_btn)
    main_layout.addLayout(top_row)

    center_layout = QVBoxLayout()
    center_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

    card = QFrame()
    card.setStyleSheet("background-color: white; border-radius: 40px;")
    card.setFixedSize(500, 470)
    card_layout = QVBoxLayout(card)
    card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

    logo = QLabel("🥪")
    logo.setStyleSheet("font-size: 48px; background: transparent;")
    logo.setAlignment(Qt.AlignmentFlag.AlignCenter)

    form_layout = QVBoxLayout()

    row1 = QHBoxLayout()
    lbl_user = QLabel("Никнейм:")
    lbl_user.setStyleSheet(
        "font-size: 16px; font-weight: bold; color: black; background:"
        " transparent;"
    )
    self.username_input = QLineEdit()
    self.username_input.setPlaceholderText("Введите ник")
    self.username_input.setStyleSheet(
        "padding: 8px; font-size: 14px; background: #fff; color: black;"
        " border: 1px solid #ccc; border-radius: 5px;"
    )
    row1.addWidget(lbl_user)
    row1.addWidget(self.username_input)

    row2 = QHBoxLayout()
    lbl_pass = QLabel("Пароль:")
    lbl_pass.setStyleSheet(
        "font-size: 16px; font-weight: bold; color: black; background:"
        " transparent;"
    )

    pass_layout = QHBoxLayout()
    pass_layout.setSpacing(5)
    self.password_input = QLineEdit()
    self.password_input.setPlaceholderText("Введите пароль")
    self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
    self.password_input.setStyleSheet(
        "padding: 8px; font-size: 14px; background: #fff; color: black;"
        " border: 1px solid #ccc; border-radius: 5px;"
    )

    self.eye_btn = QPushButton("👁")
    self.eye_btn.setFixedSize(35, 35)
    self.eye_btn.setStyleSheet(
        "background: #eee; border-radius: 5px; font-size: 16px;"
    )
    self.eye_btn.clicked.connect(self.toggle_password_visibility)

    pass_layout.addWidget(self.password_input)
    pass_layout.addWidget(self.eye_btn)

    row2.addWidget(lbl_pass)
    row2.addLayout(pass_layout)

    form_layout.addLayout(row1)
    form_layout.addLayout(row2)

    self.error_label = QLabel("")
    self.error_label.setStyleSheet(
        "color: #ff3333; font-size: 12px; background: transparent;"
    )
    self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

    login_btn = QPushButton("Войти")
    login_btn.setStyleSheet(
        "background-color: #333; color: white; font-weight: bold; padding:"
        " 10px; border-radius: 5px; font-size: 14px;"
    )
    login_btn.clicked.connect(self.try_login)

    switch_btn = QPushButton("Нет аккаунта?\nЗарегистрируйтесь")
    switch_btn.setStyleSheet(
        "color: #666; font-size: 12px; background: transparent;"
    )
    switch_btn.clicked.connect(switch_to_register)

    card_layout.addWidget(logo)
    card_layout.addSpacing(5)
    card_layout.addLayout(form_layout)
    card_layout.addWidget(self.error_label)
    card_layout.addWidget(login_btn)
    card_layout.addSpacing(5)
    card_layout.addWidget(switch_btn)

    center_layout.addWidget(card, alignment=Qt.AlignmentFlag.AlignCenter)
    main_layout.addLayout(center_layout)

  def toggle_password_visibility(self):
    if self.password_input.echoMode() == QLineEdit.EchoMode.Password:
      self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
      self.eye_btn.setText("👁‍🗨")
    else:
      self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
      self.eye_btn.setText("👁")

  def try_login(self):
    username = self.username_input.text().strip()
    password = self.password_input.text().strip()
    if not username or not password:
      self.error_label.setText("Заполните все поля!")
      return
    self.main_window.handle_login_attempt(username, password)

  def show_error(self, text):
    self.error_label.setText(text)


class RegisterScreen(AnimatedAuthBackground):

  def __init__(self, main_window, switch_to_login):
    super().__init__()
    self.main_window = main_window

    main_layout = QVBoxLayout(self)

    top_row = QHBoxLayout()
    top_row.addStretch()
    self.music_btn = MusicToggleButton(main_window)
    top_row.addWidget(self.music_btn)
    main_layout.addLayout(top_row)

    center_layout = QVBoxLayout()
    center_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

    card = QFrame()
    card.setStyleSheet("background-color: white; border-radius: 40px;")
    card.setFixedSize(500, 440)
    card_layout = QVBoxLayout(card)
    card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

    logo = QLabel("🥪")
    logo.setStyleSheet("font-size: 48px; background: transparent;")
    logo.setAlignment(Qt.AlignmentFlag.AlignCenter)

    form_layout = QVBoxLayout()

    row1 = QHBoxLayout()
    lbl_user = QLabel("Никнейм:")
    lbl_user.setStyleSheet(
        "font-size: 16px; font-weight: bold; color: black; background:"
        " transparent;"
    )
    self.username_input = QLineEdit()
    self.username_input.setPlaceholderText("Придумайте ник")
    self.username_input.setStyleSheet(
        "padding: 8px; font-size: 14px; background: #fff; color: black;"
        " border: 1px solid #ccc; border-radius: 5px;"
    )
    row1.addWidget(lbl_user)
    row1.addWidget(self.username_input)

    row2 = QHBoxLayout()
    lbl_pass = QLabel("Пароль:")
    lbl_pass.setStyleSheet(
        "font-size: 16px; font-weight: bold; color: black; background:"
        " transparent;"
    )

    pass_layout = QHBoxLayout()
    pass_layout.setSpacing(5)
    self.password_input = QLineEdit()
    self.password_input.setPlaceholderText("Придумайте пароль")
    self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
    self.password_input.setStyleSheet(
        "padding: 8px; font-size: 14px; background: #fff; color: black;"
        " border: 1px solid #ccc; border-radius: 5px;"
    )

    self.eye_btn = QPushButton("👁")
    self.eye_btn.setFixedSize(35, 35)
    self.eye_btn.setStyleSheet(
        "background: #eee; border-radius: 5px; font-size: 16px;"
    )
    self.eye_btn.clicked.connect(self.toggle_password_visibility)

    pass_layout.addWidget(self.password_input)
    pass_layout.addWidget(self.eye_btn)

    row2.addWidget(lbl_pass)
    row2.addLayout(pass_layout)

    form_layout.addLayout(row1)
    form_layout.addLayout(row2)

    self.error_label = QLabel("")
    self.error_label.setStyleSheet(
        "color: #ff3333; font-size: 12px; background: transparent;"
    )
    self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

    reg_btn = QPushButton("Зарегистрироваться")
    reg_btn.setStyleSheet(
        "background-color: #333; color: white; font-weight: bold; padding:"
        " 10px; border-radius: 5px; font-size: 14px;"
    )
    reg_btn.clicked.connect(self.try_register)

    switch_btn = QPushButton("Уже есть аккаунт?\nВойти")
    switch_btn.setStyleSheet(
        "color: #666; font-size: 12px; background: transparent;"
    )
    switch_btn.clicked.connect(switch_to_login)

    card_layout.addWidget(logo)
    card_layout.addSpacing(5)
    card_layout.addLayout(form_layout)
    card_layout.addWidget(self.error_label)
    card_layout.addWidget(reg_btn)
    card_layout.addSpacing(5)
    card_layout.addWidget(switch_btn)

    center_layout.addWidget(card, alignment=Qt.AlignmentFlag.AlignCenter)
    main_layout.addLayout(center_layout)

  def toggle_password_visibility(self):
    if self.password_input.echoMode() == QLineEdit.EchoMode.Password:
      self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
      self.eye_btn.setText("👁‍🗨")
    else:
      self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
      self.eye_btn.setText("👁")

  def try_register(self):
    username = self.username_input.text().strip()
    password = self.password_input.text().strip()
    if not username or not password:
      self.error_label.setText("Заполните все поля!")
      return
    self.main_window.handle_register_attempt(username, password)

  def show_error(self, text):
    self.error_label.setText(text)


class ProfileButton(QPushButton):

  def __init__(self, text, main_screen):
    super().__init__(text)
    self.main_screen = main_screen
    self.setStyleSheet(
        "QPushButton {"
        "   background: #222;"
        "   color: white;"
        "   padding: 8px 15px;"
        "   border-radius: 8px;"
        "   font-size: 14px;"
        "   font-weight: bold;"
        "}"
        "QPushButton:hover {"
        "   background: #333;"
        "}"
    )

  def mousePressEvent(self, event):
    self.main_screen.toggle_profile_menu()
    super().mousePressEvent(event)


class DownloadableGameCard(QFrame):

  def __init__(self, title, desc, action_text, callback, is_dark=False):
    super().__init__()
    self.callback = callback
    self.download_progress = 0
    self.is_downloading = False

    bg_color = "#1e1e1e" if is_dark else "white"
    text_color = "white" if is_dark else "#666"
    border_color = "#444" if is_dark else "#ddd"

    self.setStyleSheet(
        f"background: {bg_color}; border: 1px solid {border_color};"
        " border-radius: 12px;"
    )
    layout = QVBoxLayout(self)
    layout.setContentsMargins(15, 15, 15, 20)
    layout.setSpacing(10)

    self.img_lbl = QLabel()
    self.img_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
    img_path = os.path.join(IMAGES_DIR, "Game2.png")
    if os.path.exists(img_path):
      pixmap = QPixmap(img_path)
      self.img_lbl.setPixmap(
          pixmap.scaled(
              220,
              280,
              Qt.AspectRatioMode.KeepAspectRatio,
              Qt.TransformationMode.SmoothTransformation,
          )
      )
    else:
      self.img_lbl.setText("🖼️ Game2.png")
      self.img_lbl.setStyleSheet(
          "font-size: 14px; color: #888; border: 2px dashed #ccc; border-radius:"
          " 8px;"
      )
      self.img_lbl.setFixedSize(220, 280)
    layout.addWidget(self.img_lbl, alignment=Qt.AlignmentFlag.AlignCenter)

    self.t_lbl = QLabel(title)
    self.t_lbl.setStyleSheet(
        "font-size: 16px; font-weight: bold; color: #ff7700; border: none;"
    )
    self.t_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(self.t_lbl)

    btn_container = QVBoxLayout()
    self.action_btn = QPushButton(action_text)
    self.action_btn.setStyleSheet(
        "background: #4CAF50; color: white; padding: 8px 25px; border-radius:"
        " 6px; font-weight: bold; font-size: 14px;"
    )
    self.action_btn.clicked.connect(self.on_btn_clicked)
    btn_container.addWidget(
        self.action_btn, alignment=Qt.AlignmentFlag.AlignCenter
    )

    self.percent_lbl = QLabel("")
    self.percent_lbl.setStyleSheet(
        "font-size: 11px; color: #4CAF50; font-weight: bold; border: none;"
    )
    self.percent_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
    self.percent_lbl.hide()
    btn_container.addWidget(self.percent_lbl)

    layout.addLayout(btn_container)

    self.progress_bar = QFrame(self)
    self.progress_bar.setFixedHeight(6)
    self.progress_bar.setStyleSheet(
        "background-color: #4CAF50; border-radius: 0px 0px 12px 12px;"
    )
    self.progress_bar.setGeometry(0, 0, 0, 6)
    self.progress_bar.hide()

  def resizeEvent(self, event):
    super().resizeEvent(event)
    w = int(self.width() * (self.download_progress / 100.0))
    self.progress_bar.setGeometry(0, self.height() - 6, w, 6)

  def on_btn_clicked(self):
    if self.action_btn.text() == "Скачать" and not self.is_downloading:
      self.is_downloading = True
      self.action_btn.setEnabled(False)
      self.action_btn.setStyleSheet(
          "background: #a5d6a7; color: white; padding: 8px 25px; border-radius:"
          " 6px; font-weight: bold; font-size: 14px;"
      )
      self.percent_lbl.setText("0%")
      self.percent_lbl.show()
      self.progress_bar.show()

      self.timer = QTimer(self)
      self.timer.timeout.connect(self.update_download)
      self.timer.start(30)
    else:
      self.callback()

  def update_download(self):
    self.download_progress += 1
    self.percent_lbl.setText(f"{self.download_progress}%")

    w = int(self.width() * (self.download_progress / 100.0))
    self.progress_bar.setGeometry(0, self.height() - 6, w, 6)

    if self.download_progress >= 100:
      self.timer.stop()
      self.progress_bar.hide()
      self.percent_lbl.hide()
      self.action_btn.setEnabled(True)
      self.action_btn.setText("Играть")
      self.action_btn.setStyleSheet(
          "background: #4CAF50; color: white; padding: 8px 25px; border-radius:"
          " 6px; font-weight: bold; font-size: 14px;"
      )
      self.callback()


class MainScreen(QWidget):

  def __init__(self, main_window):
    super().__init__()
    self.main_window = main_window
    self.menu_is_open = False
    self.current_avatar = "🟩"
    self.current_name = "123123"
    self.menu = None
    self.has_new_library_item = False
    self.has_new_friend_notification = False

    self.main_layout_base = QVBoxLayout(self)
    self.main_layout_base.setContentsMargins(0, 0, 0, 0)
    self.main_layout_base.setSpacing(0)

    self.top_bar = QWidget()
    self.top_bar_layout = QHBoxLayout(self.top_bar)
    self.top_bar_layout.setContentsMargins(20, 15, 20, 15)

    self.about_btn = QPushButton("О Buterkod")
    self.about_btn.clicked.connect(lambda: self.main_window.switch_screen(4))
    self.top_bar_layout.addWidget(self.about_btn)

    self.top_bar_layout.addStretch()

    nav_layout = QHBoxLayout()
    nav_layout.setSpacing(15)

    self.shop_tab_btn = QPushButton("Хлебный магазин")
    self.shop_tab_btn.clicked.connect(self.show_shop)

    lib_container_layout = QHBoxLayout()
    lib_container_layout.setContentsMargins(0, 0, 0, 0)
    lib_container_layout.setSpacing(4)

    self.lib_tab_btn = QPushButton("Библиотека")
    self.lib_tab_btn.clicked.connect(self.show_library)

    self.notification_dot = QLabel()
    self.notification_dot.setFixedSize(12, 12)
    self.notification_dot.setStyleSheet(
        "background-color: #ffeb3b; border: 2px solid #333; border-radius:"
        " 6px;"
    )
    self.notification_dot.hide()

    lib_container_layout.addWidget(self.lib_tab_btn)
    lib_container_layout.addWidget(self.notification_dot)

    friend_container_layout = QHBoxLayout()
    friend_container_layout.setContentsMargins(0, 0, 0, 0)
    friend_container_layout.setSpacing(4)

    self.friends_tab_btn = QPushButton("Друзья")
    self.friends_tab_btn.clicked.connect(self.show_friends)

    self.friend_notification_dot = QLabel()
    self.friend_notification_dot.setFixedSize(12, 12)
    self.friend_notification_dot.setStyleSheet(
        "background-color: #ffeb3b; border: 2px solid #333; border-radius:"
        " 6px;"
    )
    self.friend_notification_dot.hide()

    friend_container_layout.addWidget(self.friends_tab_btn)
    friend_container_layout.addWidget(self.friend_notification_dot)

    nav_layout.addWidget(self.shop_tab_btn)
    nav_layout.addLayout(lib_container_layout)
    nav_layout.addLayout(friend_container_layout)
    self.top_bar_layout.addLayout(nav_layout)

    self.top_bar_layout.addStretch()

    self.profile_btn = ProfileButton(
        f" {self.current_avatar}  {self.current_name}  ▾", self
    )
    self.top_bar_layout.addWidget(self.profile_btn)

    self.main_layout_base.addWidget(self.top_bar)

    self.content_stack = QStackedWidget()

    # --- 1. ХЛЕБНЫЙ МАГАЗИН ---
    self.shop_widget = QWidget()
    shop_layout = QVBoxLayout(self.shop_widget)
    shop_layout.setAlignment(
        Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop
    )
    shop_layout.setContentsMargins(40, 30, 40, 40)

    shop_title = QLabel("Хлебный магазин")
    shop_title.setStyleSheet(
        "font-size: 26px; font-weight: bold; color: #ff7700;"
    )
    shop_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
    shop_layout.addWidget(shop_title)
    shop_layout.addSpacing(15)

    self.games_container = QFrame()
    games_container_layout = QVBoxLayout(self.games_container)
    games_container_layout.setContentsMargins(25, 25, 25, 25)
    games_container_layout.setSpacing(20)

    games_header = QLabel("Доступные игры")
    games_header.setStyleSheet("font-size: 20px; font-weight: bold;")
    games_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
    games_container_layout.addWidget(games_header)
    games_container_layout.addSpacing(10)

    self.games_list = [
        (
            "Космический выживач",
            "Собери ресурсы в открытом космосе и выживи!",
            "spaceSurvival.pyw",
        ),
        (
            "Пиксельный платформер",
            "Пройди все уровни, прыгая по платформам и уворачиваясь от врагов.",
            "pixelPlatformer.pyw",
        ),
        (
            "Змейка 2.0",
            "Классическая змейка в новом бутербродном исполнении.",
            "snakeTwoPointZero.pyw",
        ),
        (
            "Бутербродный Кликер",
            "Кликай по огромному сэндвичу и зарабатывай крошки.",
            "sandwichClicker.pyw",
        ),
        (
            "Лабиринт Тостера",
            "Найди выход из горячего лабиринта раньше, чем подгорит хлеб.",
            "toasterMaze.pyw",
        ),
    ]

    self.shop_buttons = {}
    self.shop_cards_layout_inner = QHBoxLayout()
    self.shop_cards_layout_inner.setSpacing(15)
    self.shop_card_frames = []

    for title, desc, filename in self.games_list:
      game_card = QFrame()
      game_card.setFixedWidth(220)
      game_card.setFixedHeight(340)

      card_inner = QVBoxLayout(game_card)
      card_inner.setContentsMargins(15, 15, 15, 15)
      card_inner.setSpacing(10)

      img_lbl = QLabel()
      img_path = os.path.join(IMAGES_DIR, "Game.png")
      if os.path.exists(img_path):
        pixmap = QPixmap(img_path)
        img_lbl.setPixmap(
            pixmap.scaled(
                180,
                110,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )
      else:
        img_lbl.setText("🖼️ Game.png")
        img_lbl.setStyleSheet(
            "font-size: 12px; color: #888; border: 2px dashed #ccc; border-radius:"
            " 8px;"
        )
        img_lbl.setFixedSize(180, 110)
      img_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
      card_inner.addWidget(img_lbl)

      t_lbl = QLabel(title)
      t_lbl.setStyleSheet(
          "font-size: 15px; font-weight: bold; color: #ff7700; border: none;"
      )
      t_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
      card_inner.addWidget(t_lbl)

      d_lbl = QLabel(desc)
      d_lbl.setStyleSheet("font-size: 11px; border: none;")
      d_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
      d_lbl.setWordWrap(True)
      card_inner.addWidget(d_lbl)

      card_inner.addStretch()

      buy_btn = QPushButton("Купить: 0 руб")
      buy_btn.setStyleSheet(
          "background: #ff7700; color: white; padding: 8px 15px; border-radius:"
          " 6px; font-weight: bold; font-size: 14px;"
      )
      buy_btn.clicked.connect(lambda _, t=title: self.buy_game(t))
      self.shop_buttons[title] = buy_btn
      card_inner.addWidget(buy_btn, alignment=Qt.AlignmentFlag.AlignCenter)

      self.shop_cards_layout_inner.addWidget(game_card)
      self.shop_card_frames.append(game_card)

    games_container_layout.addLayout(self.shop_cards_layout_inner)
    shop_layout.addWidget(self.games_container)

    shop_scroll = QScrollArea()
    shop_scroll.setWidgetResizable(True)
    shop_scroll.setWidget(self.shop_widget)
    shop_scroll.setStyleSheet("border: none;")

    # --- 2. БИБЛИОТЕКА ---
    self.lib_widget = QWidget()
    lib_layout = QVBoxLayout(self.lib_widget)
    lib_layout.setAlignment(
        Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop
    )
    lib_layout.setContentsMargins(40, 30, 40, 40)

    lib_title = QLabel("Библиотека игр")
    lib_title.setStyleSheet(
        "font-size: 26px; font-weight: bold; color: #ff7700;"
    )
    lib_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
    lib_layout.addWidget(lib_title)
    lib_layout.addSpacing(15)

    self.lib_container = QFrame()
    self.lib_container_layout = QVBoxLayout(self.lib_container)
    self.lib_container_layout.setContentsMargins(25, 25, 25, 25)

    self.lib_grid_layout = QGridLayout()
    self.lib_grid_layout.setSpacing(20)
    self.lib_container_layout.addLayout(self.lib_grid_layout)

    lib_layout.addWidget(self.lib_container)

    lib_scroll = QScrollArea()
    lib_scroll.setWidgetResizable(True)
    lib_scroll.setWidget(self.lib_widget)
    lib_scroll.setStyleSheet("border: none;")

    # --- 3. ДРУЗЬЯ ---
    self.friends_widget = QWidget()
    friends_main_layout = QVBoxLayout(self.friends_widget)
    friends_main_layout.setAlignment(
        Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop
    )
    friends_main_layout.setContentsMargins(40, 30, 40, 40)

    friends_title = QLabel("Друзья")
    friends_title.setStyleSheet(
        "font-size: 26px; font-weight: bold; color: #ff7700;"
    )
    friends_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
    friends_main_layout.addWidget(friends_title)
    friends_main_layout.addSpacing(15)

    self.friends_container = QFrame()
    self.friends_container.setFixedWidth(700)
    friends_container_layout = QVBoxLayout(self.friends_container)
    friends_container_layout.setContentsMargins(25, 25, 25, 25)

    cat_nav_layout = QHBoxLayout()
    cat_nav_layout.setSpacing(10)

    self.cat_friends_btn = QPushButton("Друзья")
    self.cat_add_btn = QPushButton("Добавить в друзья")
    self.cat_req_btn = QPushButton("Ожидание")

    cat_nav_layout.addWidget(self.cat_friends_btn)
    cat_nav_layout.addWidget(self.cat_add_btn)
    cat_nav_layout.addWidget(self.cat_req_btn)
    cat_nav_layout.addStretch()

    friends_container_layout.addLayout(cat_nav_layout)
    friends_container_layout.addSpacing(15)

    self.cat_friends_btn.clicked.connect(lambda: self.switch_friends_subtab(0))
    self.cat_add_btn.clicked.connect(lambda: self.switch_friends_subtab(1))
    self.cat_req_btn.clicked.connect(lambda: self.switch_friends_subtab(2))

    self.friends_sub_stack = QStackedWidget()

    self.friends_list_widget = QWidget()
    self.friends_list_layout = QVBoxLayout(self.friends_list_widget)
    self.friends_list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
    self.friends_sub_stack.addWidget(self.friends_list_widget)

    self.add_friend_widget = QWidget()
    add_friend_layout = QVBoxLayout(self.add_friend_widget)
    add_friend_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
    add_friend_layout.setSpacing(15)

    self.friend_search_input = QLineEdit()
    self.friend_search_input.setPlaceholderText("Введите никнейм друга...")
    self.friend_search_input.setStyleSheet(
        "padding: 8px; font-size: 14px; border: 1px solid #ccc; border-radius:"
        " 6px;"
    )

    send_req_btn = QPushButton("Отправить запрос")
    send_req_btn.setStyleSheet(
        "background: #ff7700; color: white; padding: 8px 20px; border-radius:"
        " 6px; font-weight: bold; font-size: 14px;"
    )
    send_req_btn.clicked.connect(self.send_friend_request)

    self.friend_req_status = QLabel("")
    self.friend_req_status.setStyleSheet("font-size: 13px; border: none;")

    add_friend_layout.addWidget(self.friend_search_input)
    add_friend_layout.addWidget(send_req_btn)
    add_friend_layout.addWidget(self.friend_req_status)
    self.friends_sub_stack.addWidget(self.add_friend_widget)

    self.requests_widget = QWidget()
    self.requests_layout = QVBoxLayout(self.requests_widget)
    self.requests_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
    self.friends_sub_stack.addWidget(self.requests_widget)

    friends_container_layout.addWidget(self.friends_sub_stack)
    friends_main_layout.addWidget(
        self.friends_container, alignment=Qt.AlignmentFlag.AlignCenter
    )

    friends_scroll = QScrollArea()
    friends_scroll.setWidgetResizable(True)
    friends_scroll.setWidget(self.friends_widget)
    friends_scroll.setStyleSheet("border: none;")

    self.content_stack.addWidget(shop_scroll)
    self.content_stack.addWidget(lib_scroll)
    self.content_stack.addWidget(friends_scroll)

    self.main_layout_base.addWidget(self.content_stack)
    self.show_shop()

  def show_shop(self):
    self.content_stack.setCurrentIndex(0)
    self.shop_tab_btn.setStyleSheet(
        "background: #ff7700; color: white; font-weight: bold; border-radius:"
        " 8px; padding: 6px 14px; font-size: 14px;"
    )
    self.lib_tab_btn.setStyleSheet(
        "background: #eee; color: #333; font-weight: bold; border-radius: 8px;"
        " padding: 6px 14px; font-size: 14px;"
    )
    self.friends_tab_btn.setStyleSheet(
        "background: #eee; color: #333; font-weight: bold; border-radius: 8px;"
        " padding: 6px 14px; font-size: 14px;"
    )
    self.apply_theme()
    self.refresh_shop_view()

  def show_library(self):
    self.has_new_library_item = False
    self.notification_dot.hide()
    self.content_stack.setCurrentIndex(1)
    self.lib_tab_btn.setStyleSheet(
        "background: #ff7700; color: white; font-weight: bold; border-radius:"
        " 8px; padding: 6px 14px; font-size: 14px;"
    )
    self.shop_tab_btn.setStyleSheet(
        "background: #eee; color: #333; font-weight: bold; border-radius: 8px;"
        " padding: 6px 14px; font-size: 14px;"
    )
    self.friends_tab_btn.setStyleSheet(
        "background: #eee; color: #333; font-weight: bold; border-radius: 8px;"
        " padding: 6px 14px; font-size: 14px;"
    )
    self.apply_theme()
    self.refresh_library_view()

  def show_friends(self):
    self.has_new_friend_notification = False
    self.friend_notification_dot.hide()
    self.content_stack.setCurrentIndex(2)
    self.friends_tab_btn.setStyleSheet(
        "background: #ff7700; color: white; font-weight: bold; border-radius:"
        " 8px; padding: 6px 14px; font-size: 14px;"
    )
    self.shop_tab_btn.setStyleSheet(
        "background: #eee; color: #333; font-weight: bold; border-radius: 8px;"
        " padding: 6px 14px; font-size: 14px;"
    )
    self.lib_tab_btn.setStyleSheet(
        "background: #eee; color: #333; font-weight: bold; border-radius: 8px;"
        " padding: 6px 14px; font-size: 14px;"
    )
    self.apply_theme()
    self.switch_friends_subtab(0)

  def switch_friends_subtab(self, index):
    self.friends_sub_stack.setCurrentIndex(index)
    dark = self.is_dark_theme()
    active = (
        "background: #ff7700; color: white; font-weight: bold; border-radius:"
        " 6px; padding: 8px 16px;"
    )
    inactive = (
        "background: #2a2a2a; color: #ccc; font-weight: bold; border: 1px solid"
        " #444; border-radius: 6px; padding: 8px 16px;"
        if dark
        else "background: white; color: #333; font-weight: bold; border: 1px"
        " solid #ccc; border-radius: 6px; padding: 8px 16px;"
    )
    self.cat_friends_btn.setStyleSheet(active if index == 0 else inactive)
    self.cat_add_btn.setStyleSheet(active if index == 1 else inactive)
    self.cat_req_btn.setStyleSheet(active if index == 2 else inactive)
    self.friend_req_status.setText("")
    self.refresh_friends_view()

  def update_user_info(self, avatar, username):
    self.current_avatar = avatar
    self.current_name = username
    if not self.menu_is_open:
      self.profile_btn.setText(f" {avatar}  {username}  ▾")
    self.has_new_library_item = False
    self.notification_dot.hide()
    self.has_new_friend_notification = False
    self.friend_notification_dot.hide()
    self.apply_theme()
    self.refresh_shop_view()
    self.refresh_library_view()
    self.refresh_friends_view()

  def refresh_shop_view(self):
    if not self.main_window.current_user:
      return
    user_db = self.main_window.users_db.get(
        self.main_window.current_user, {"library": {}}
    )
    library_games = user_db.get("library", {})
    for title, btn in self.shop_buttons.items():
      if title in library_games:
        btn.setText("Куплено")
        btn.setEnabled(False)
        btn.setStyleSheet(
            "background: #ccc; color: #666; padding: 8px 15px; border-radius:"
            " 6px; font-weight: bold; font-size: 14px;"
        )
      else:
        btn.setText("Купить: 0 руб")
        btn.setEnabled(True)
        btn.setStyleSheet(
            "background: #ff7700; color: white; padding: 8px 15px;"
            " border-radius: 6px; font-weight: bold; font-size: 14px;"
        )

  def buy_game(self, title):
    user_db = self.main_window.users_db[self.main_window.current_user]
    if title not in user_db["library"]:
      user_db["library"][title] = "download"
      save_users(self.main_window.users_db)
      self.has_new_library_item = True
      self.notification_dot.show()
      self.refresh_shop_view()

  def refresh_library_view(self):
    while self.lib_grid_layout.count():
      item = self.lib_grid_layout.takeAt(0)
      if item.widget():
        item.widget().deleteLater()

    user_db = self.main_window.users_db.get(
        self.main_window.current_user, {"library": {}}
    )
    library_games = user_db.get("library", {})

    if not library_games:
      lbl = QLabel("Ваша библиотека пока пуста. Купите игры в магазине!")
      lbl.setStyleSheet("font-size: 16px; color: #666; border: none;")
      lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
      self.lib_grid_layout.addWidget(lbl, 0, 0)
      return

    max_columns = 4
    for index, (title, status) in enumerate(library_games.items()):
      desc = next((d for t, d, f in self.games_list if t == title), "")
      action_text = "Скачать" if status == "download" else "Играть"
      card = DownloadableGameCard(
          title,
          desc,
          action_text,
          lambda t=title: self.on_game_action(t),
          is_dark=self.is_dark_theme(),
      )
      row = index // max_columns
      col = index % max_columns
      self.lib_grid_layout.addWidget(card, row, col)

  def on_game_action(self, title):
    user_db = self.main_window.users_db[self.main_window.current_user]
    if user_db["library"].get(title) == "download":
      user_db["library"][title] = "play"
      save_users(self.main_window.users_db)
      self.refresh_library_view()
    else:
      filename = next((f for t, d, f in self.games_list if t == title), "")
      game_path = os.path.join(GAMES_DIR, filename)
      if os.path.exists(game_path):
        subprocess.Popen([sys.executable, game_path])
      else:
        print(f"Файл игры не найден: {game_path}")

  def refresh_friends_view(self):
    while self.friends_list_layout.count():
      item = self.friends_list_layout.takeAt(0)
      if item.widget():
        item.widget().deleteLater()

    me = self.main_window.current_user
    my_data = self.main_window.users_db.get(me, {})
    friends = my_data.get("friends", [])
    requests = my_data.get("requests", [])

    dark = self.is_dark_theme()
    card_bg = "#222" if dark else "white"
    card_border = "#444" if dark else "#ddd"

    if not friends:
      lbl = QLabel("У вас пока нет друзей.")
      lbl.setStyleSheet("font-size: 15px; color: #777; border: none;")
      self.friends_list_layout.addWidget(lbl)
    else:
      for f_nick in friends:
        f_data = self.main_window.users_db.get(f_nick, {})
        f_avatar = f_data.get("avatar", "🟩")
        status_text, status_color = self.main_window.get_user_status(f_nick)

        card = QFrame()
        card.setStyleSheet(
            f"background: {card_bg}; border: 1px solid {card_border};"
            " border-radius: 8px; padding: 8px;"
        )
        c_layout = QHBoxLayout(card)

        info_lbl = QLabel(f"{f_avatar}  <b>{f_nick}</b>")
        info_lbl.setStyleSheet(
            f"font-size: 16px; border: none; color: {'white' if dark else 'black'};"
        )

        st_lbl = QLabel(status_text)
        st_lbl.setStyleSheet(
            f"font-size: 13px; font-weight: bold; color: {status_color}; border:"
            " none;"
        )

        remove_btn = QPushButton("Удалить")
        remove_btn.setStyleSheet(
            "background: #ff4444; color: white; border-radius: 4px; padding:"
            " 4px 10px; font-size: 12px;"
        )
        remove_btn.clicked.connect(
            lambda _, fn=f_nick: self.remove_friend(fn)
        )

        c_layout.addWidget(info_lbl)
        c_layout.addSpacing(15)
        c_layout.addWidget(st_lbl)
        c_layout.addStretch()
        c_layout.addWidget(remove_btn)

        self.friends_list_layout.addWidget(card)

    while self.requests_layout.count():
      item = self.requests_layout.takeAt(0)
      if item.widget():
        item.widget().deleteLater()

    if not requests:
      lbl = QLabel("Нет входящих запросов в друзья.")
      lbl.setStyleSheet("font-size: 15px; color: #777; border: none;")
      self.requests_layout.addWidget(lbl)
    else:
      for req_nick in requests:
        r_data = self.main_window.users_db.get(req_nick, {})
        r_avatar = r_data.get("avatar", "🟩")

        card = QFrame()
        card.setStyleSheet(
            f"background: {card_bg}; border: 1px solid {card_border};"
            " border-radius: 8px; padding: 8px;"
        )
        c_layout = QHBoxLayout(card)

        info_lbl = QLabel(f"{r_avatar}  <b>{req_nick}</b> желает подружиться")
        info_lbl.setStyleSheet(
            f"font-size: 15px; border: none; color: {'white' if dark else 'black'};"
        )

        accept_btn = QPushButton("Принять")
        accept_btn.setStyleSheet(
            "background: #4CAF50; color: white; border-radius: 4px; padding:"
            " 4px 10px; font-weight: bold;"
        )
        accept_btn.clicked.connect(
            lambda _, rn=req_nick: self.accept_friend_request(rn)
        )

        decline_btn = QPushButton("Отклонить")
        decline_btn.setStyleSheet(
            "background: #888; color: white; border-radius: 4px; padding: 4px"
            " 10px;"
        )
        decline_btn.clicked.connect(
            lambda _, rn=req_nick: self.decline_friend_request(rn)
        )

        c_layout.addWidget(info_lbl)
        c_layout.addStretch()
        c_layout.addWidget(accept_btn)
        c_layout.addWidget(decline_btn)

        self.requests_layout.addWidget(card)

  def send_friend_request(self):
    target_nick = self.friend_search_input.text().strip()
    me = self.main_window.current_user
    if not target_nick:
      self.friend_req_status.setStyleSheet("color: red; border: none;")
      self.friend_req_status.setText("Введите никнейм!")
      return
    if target_nick == me:
      self.friend_req_status.setStyleSheet("color: red; border: none;")
      self.friend_req_status.setText("Нельзя добавить самого себя!")
      return
    if target_nick not in self.main_window.users_db:
      self.friend_req_status.setStyleSheet("color: red; border: none;")
      self.friend_req_status.setText("Пользователь не найден!")
      return

    target_data = self.main_window.users_db[target_nick]
    my_data = self.main_window.users_db[me]

    if target_nick in my_data.get("friends", []):
      self.friend_req_status.setStyleSheet("color: red; border: none;")
      self.friend_req_status.setText("Вы уже друзья!")
      return
    if me in target_data.get("requests", []):
      self.friend_req_status.setStyleSheet("color: orange; border: none;")
      self.friend_req_status.setText("Запрос уже отправлен!")
      return

    if "requests" not in target_data:
      target_data["requests"] = []
    target_data["requests"].append(me)
    save_users(self.main_window.users_db)

    self.friend_req_status.setStyleSheet("color: green; border: none;")
    self.friend_req_status.setText("Запрос в друзья успешно отправлен!")
    self.friend_search_input.clear()

  def accept_friend_request(self, req_nick):
    me = self.main_window.current_user
    my_data = self.main_window.users_db[me]
    req_data = self.main_window.users_db.get(req_nick)

    if req_nick in my_data.get("requests", []):
      my_data["requests"].remove(req_nick)
      if "friends" not in my_data:
        my_data["friends"] = []
      if req_nick not in my_data["friends"]:
        my_data["friends"].append(req_nick)

      if req_data:
        if "friends" not in req_data:
          req_data["friends"] = []
        if me not in req_data["friends"]:
          req_data["friends"].append(me)

      save_users(self.main_window.users_db)
      self.refresh_friends_view()

  def decline_friend_request(self, req_nick):
    me = self.main_window.current_user
    my_data = self.main_window.users_db[me]
    if req_nick in my_data.get("requests", []):
      my_data["requests"].remove(req_nick)
      save_users(self.main_window.users_db)
      self.refresh_friends_view()

  def remove_friend(self, friend_nick):
    me = self.main_window.current_user
    my_data = self.main_window.users_db[me]
    f_data = self.main_window.users_db.get(friend_nick)

    if friend_nick in my_data.get("friends", []):
      my_data["friends"].remove(friend_nick)
    if f_data and me in f_data.get("friends", []):
      f_data["friends"].remove(me)

    save_users(self.main_window.users_db)
    self.refresh_friends_view()

  def toggle_profile_menu(self):
    if self.menu_is_open:
      if self.menu:
        self.menu.close()
      return
    self.menu_is_open = True
    self.profile_btn.setText(f" {self.current_avatar}  {self.current_name}  ▴")

    self.menu = QMenu(self)
    self.menu.setStyleSheet(
        "QMenu { background-color: white; color: black; border: 1px solid"
        " #ccc; border-radius: 6px; padding: 5px; }"
        "QMenu::item { padding: 8px 20px; font-size: 14px; border-radius:"
        " 4px; }"
        "QMenu::item:selected { background-color: #ff7700; color: white; }"
    )

    settings_action = self.menu.addAction("⚙️ Настройки")
    logout_action = self.menu.addAction("🚪 Выйти")

    self.menu.aboutToHide.connect(self.on_menu_closed)

    global_pos = self.profile_btn.mapToGlobal(
        QPointF(0, self.profile_btn.height()).toPoint()
    )
    self.menu.popup(global_pos)

    settings_action.triggered.connect(self.main_window.open_settings)
    logout_action.triggered.connect(lambda: self.main_window.switch_screen(0))

  def on_menu_closed(self):
    self.menu_is_open = False
    self.profile_btn.setText(f" {self.current_avatar}  {self.current_name}  ▾")
    self.menu = None

  def is_dark_theme(self):
    if not self.main_window.current_user:
      return False
    user_data = self.main_window.users_db.get(self.main_window.current_user, {})
    return user_data.get("dark_theme", False)

  def apply_theme(self):
    dark = self.is_dark_theme()
    if dark:
      self.setStyleSheet("background-color: #121212; color: white;")
      self.top_bar.setStyleSheet("background-color: #1f1f1f;")
      self.about_btn.setStyleSheet(
          "background-color: #333; color: white; font-weight: bold; border: 2px"
          " solid #555; border-radius: 8px; padding: 6px 14px; font-size: 14px;"
      )
      self.games_container.setStyleSheet(
          "background-color: #1e1e1e; border: 3px solid #ff7700; border-radius:"
          " 15px;"
      )
      self.lib_container.setStyleSheet(
          "background-color: #1e1e1e; border: 3px solid #ff7700; border-radius:"
          " 15px;"
      )
      self.friends_container.setStyleSheet(
          "background-color: #1e1e1e; border: 3px solid #ff7700; border-radius:"
          " 15px;"
      )
      for card in self.shop_card_frames:
        card.setStyleSheet(
            "background: #2a2a2a; border: 1px solid #444; border-radius: 12px;"
        )
    else:
      self.setStyleSheet("background-color: white; color: black;")
      self.top_bar.setStyleSheet("background-color: #ff7700;")
      self.about_btn.setStyleSheet(
          "background-color: white; color: black; font-weight: bold; border: 2px"
          " solid #333; border-radius: 8px; padding: 6px 14px; font-size: 14px;"
      )
      self.games_container.setStyleSheet(
          "background-color: #fffaf0; border: 3px solid #ff7700; border-radius:"
          " 15px;"
      )
      self.lib_container.setStyleSheet(
          "background-color: #fffaf0; border: 3px solid #ff7700; border-radius:"
          " 15px;"
      )
      self.friends_container.setStyleSheet(
          "background-color: #fffaf0; border: 3px solid #ff7700; border-radius:"
          " 15px;"
      )
      for card in self.shop_card_frames:
        card.setStyleSheet(
            "background: white; border: 1px solid #ddd; border-radius: 12px;"
        )


class SettingsScreen(QWidget):

  def __init__(self, main_window):
    super().__init__()
    self.main_window = main_window
    self.setStyleSheet("background-color: #121212; color: white;")

    layout = QVBoxLayout()
    layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

    title = QLabel("Настройки профиля")
    title.setStyleSheet("font-size: 24px; font-weight: bold; color: #ffaa00;")
    title.setAlignment(Qt.AlignmentFlag.AlignCenter)

    form_layout = QVBoxLayout()
    form_layout.setSpacing(15)

    row_av = QHBoxLayout()
    lbl_av = QLabel("Аватар (эмодзи):")
    lbl_av.setStyleSheet("font-size: 14px;")
    self.avatar_input = QLineEdit()
    self.avatar_input.setMaxLength(2)
    self.avatar_input.setFixedSize(60, 35)
    self.avatar_input.setStyleSheet("font-size: 18px; text-align: center;")
    row_av.addWidget(lbl_av)
    row_av.addWidget(self.avatar_input)
    row_av.setAlignment(Qt.AlignmentFlag.AlignCenter)

    row_nick = QHBoxLayout()
    lbl_nick = QLabel("Новый никнейм:")
    lbl_nick.setStyleSheet("font-size: 14px;")
    self.nick_input = QLineEdit()
    self.nick_input.setFixedSize(180, 35)
    self.nick_input.setStyleSheet("font-size: 14px; padding: 5px;")
    row_nick.addWidget(lbl_nick)
    row_nick.addWidget(self.nick_input)
    row_nick.setAlignment(Qt.AlignmentFlag.AlignCenter)

    row_theme = QHBoxLayout()
    self.dark_theme_check = QCheckBox("Включить тёмную тему")
    self.dark_theme_check.setStyleSheet("font-size: 14px;")
    row_theme.addWidget(self.dark_theme_check)
    row_theme.setAlignment(Qt.AlignmentFlag.AlignCenter)

    form_layout.addLayout(row_av)
    form_layout.addLayout(row_nick)
    form_layout.addLayout(row_theme)

    self.error_lbl = QLabel("")
    self.error_lbl.setStyleSheet("color: #ff4444; font-size: 13px;")
    self.error_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

    save_btn = QPushButton("Сохранить изменения")
    save_btn.setStyleSheet(
        "background: #ff7700; color: white; font-weight: bold; padding: 10px"
        " 20px; border-radius: 6px; font-size: 14px;"
    )
    save_btn.setFixedSize(220, 40)
    save_btn.clicked.connect(self.save_settings)

    back_btn = QPushButton("Назад в меню")
    back_btn.setStyleSheet(
        "background: #444; color: white; padding: 10px 20px; border-radius:"
        " 6px; font-size: 14px;"
    )
    back_btn.setFixedSize(220, 40)
    back_btn.clicked.connect(self.go_back)

    layout.addWidget(title)
    layout.addSpacing(25)
    layout.addLayout(form_layout)
    layout.addWidget(self.error_lbl)
    layout.addSpacing(15)
    layout.addWidget(save_btn, alignment=Qt.AlignmentFlag.AlignCenter)
    layout.addSpacing(10)
    layout.addWidget(back_btn, alignment=Qt.AlignmentFlag.AlignCenter)

    self.setLayout(layout)

  def load_current_data(self, avatar, nickname, is_dark):
    self.avatar_input.setText(avatar)
    self.nick_input.setText(nickname)
    self.dark_theme_check.setChecked(is_dark)
    self.error_lbl.setText("")
    self.old_nickname = nickname

  def save_settings(self):
    new_nick = self.nick_input.text().strip()
    new_avatar = self.avatar_input.text().strip() or "🟩"
    is_dark = self.dark_theme_check.isChecked()

    if not new_nick:
      self.error_lbl.setText("Никнейм не может быть пустым!")
      return

    self.main_window.update_user_credentials(
        self.old_nickname, new_nick, new_avatar, is_dark
    )

  def go_back(self):
    self.main_window.switch_screen(2)


class AboutScreen(QWidget):

  def __init__(self, main_window):
    super().__init__()
    self.main_window = main_window
    self.setStyleSheet("background-color: #181818; color: white;")

    layout = QVBoxLayout()
    layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.setContentsMargins(40, 40, 40, 40)

    title = QLabel("О платформе Buterkod")
    title.setStyleSheet("font-size: 28px; font-weight: bold; color: #ff7700;")
    title.setAlignment(Qt.AlignmentFlag.AlignCenter)

    desc = QLabel(
        "Buterkod — это уникальная игровая платформа, где каждый\nбутерброд"
        " находит свой путь, а игры приносят радость и веселье!"
    )
    desc.setStyleSheet("font-size: 16px; color: #ccc;")
    desc.setAlignment(Qt.AlignmentFlag.AlignCenter)

    back_btn = QPushButton("Назад")
    back_btn.setStyleSheet(
        "background: #444; color: white; padding: 10px 20px; border-radius:"
        " 5px; font-size: 14px;"
    )
    back_btn.clicked.connect(lambda: self.main_window.switch_screen(2))

    version_lbl = QLabel("Версия 1.0\nРелиз")
    version_lbl.setStyleSheet("font-size: 12px; color: #666;")
    version_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

    layout.addWidget(title)
    layout.addSpacing(15)
    layout.addWidget(desc)
    layout.addSpacing(30)
    layout.addWidget(back_btn, alignment=Qt.AlignmentFlag.AlignCenter)
    layout.addStretch()
    layout.addWidget(version_lbl, alignment=Qt.AlignmentFlag.AlignCenter)
    layout.addSpacing(15)

    self.setLayout(layout)


class MainWindow(QStackedWidget):

  def __init__(self):
    super().__init__()
    self.setWindowTitle("Buterkod - Игровая платформа")
    self.resize(1100, 750)

    self.online_users = set()
    self.user_current_game = {}

    # Надежная инициализация музыки
    self.audio_output = QAudioOutput(self)
    self.audio_output.setVolume(0.5)

    self.player = QMediaPlayer(self)
    self.player.setAudioOutput(self.audio_output)
    self.player.setLoops(QMediaPlayer.Loops.Infinite)

    music_path = os.path.join(BASE_DIR, "Music", "Buterkod_music.mp3")
    if os.path.exists(music_path):
      self.player.setSource(QUrl.fromLocalFile(music_path))
      self.player.play()
    else:
      print(f"Файл фоновой музыки не найден: {music_path}")

    self.users_db = load_users()
    self.current_user = None

    self.login_screen = LoginScreen(self, lambda: self.switch_screen(1))
    self.register_screen = RegisterScreen(self, lambda: self.switch_screen(0))
    self.main_screen = MainScreen(self)
    self.settings_screen = SettingsScreen(self)
    self.about_screen = AboutScreen(self)

    self.addWidget(self.login_screen)
    self.addWidget(self.register_screen)
    self.addWidget(self.main_screen)
    self.addWidget(self.settings_screen)
    self.addWidget(self.about_screen)

    self.switch_screen(0)

  def switch_screen(self, index):
    self.setCurrentIndex(index)
    if index == 2 and self.current_user:
      self.online_users.add(self.current_user)
    elif index != 2 and self.current_user in self.online_users:
      self.online_users.remove(self.current_user)

  def handle_login_attempt(self, username, password):
    if username not in self.users_db:
      self.login_screen.show_error("Такого пользователя не существует!")
      return

    if self.users_db[username]["password"] != password:
      self.login_screen.show_error("Неверный пароль!")
      return

    self.current_user = username
    if self.player.playbackState() != QMediaPlayer.PlaybackState.PlayingState:
      self.player.play()

    user_data = self.users_db[username]
    self.main_screen.update_user_info(
        user_data.get("avatar", "🟩"), username
    )
    self.switch_screen(2)

  def handle_register_attempt(self, username, password):
    if username in self.users_db:
      self.register_screen.show_error("Такой ник уже занят!")
      return

    self.users_db[username] = {
        "password": password,
        "avatar": "🟩",
        "library": {},
        "friends": [],
        "requests": [],
        "dark_theme": False,
    }
    save_users(self.users_db)

    self.current_user = username
    if self.player.playbackState() != QMediaPlayer.PlaybackState.PlayingState:
      self.player.play()

    self.main_screen.update_user_info("🟩", username)
    self.switch_screen(2)

  def get_user_status(self, nick):
    if nick in self.online_users:
      game = self.user_current_game.get(nick)
      if game:
        return f"Играет в {game}", "#4CAF50"
      return "В сети", "#4CAF50"
    return "Не в сети", "#888888"

  def open_settings(self):
    user_data = self.users_db[self.current_user]
    avatar = user_data.get("avatar", "🟩")
    dark = user_data.get("dark_theme", False)
    self.settings_screen.load_current_data(avatar, self.current_user, dark)
    self.switch_screen(3)

  def update_user_credentials(self, old_nick, new_nick, new_avatar, is_dark):
    if new_nick != old_nick and new_nick in self.users_db:
      self.settings_screen.error_lbl.setText("Этот ник уже занят!")
      return

    user_data = self.users_db.pop(old_nick)
    user_data["avatar"] = new_avatar
    user_data["dark_theme"] = is_dark

    for u, data in self.users_db.items():
      if old_nick in data.get("friends", []):
        idx = data["friends"].index(old_nick)
        data["friends"][idx] = new_nick
      if old_nick in data.get("requests", []):
        idx = data["requests"].index(old_nick)
        data["requests"][idx] = new_nick

    self.users_db[new_nick] = user_data
    save_users(self.users_db)

    if old_nick in self.online_users:
      self.online_users.remove(old_nick)
      self.online_users.add(new_nick)

    self.current_user = new_nick
    self.main_screen.update_user_info(new_avatar, new_nick)
    user_data = self.users_db[self.current_user]
    avatar = user_data.get("avatar", "🟩")
    dark = user_data.get("dark_theme", False)
    self.settings_screen.load_current_data(avatar, self.current_user, dark)
    self.switch_screen(3)


if __name__ == "__main__":
  app = QApplication(sys.argv)
  window = MainWindow()
  window.show()
  sys.exit(app.exec())
