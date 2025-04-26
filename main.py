import sys
import random
import string
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton,
    QLineEdit, QStackedWidget, QGraphicsOpacityEffect
)
from PyQt5.QtCore import QTimer, Qt, QPropertyAnimation
from PyQt5.QtGui import QFont

class MemoryGame(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🧠 Игра на память")
        self.setGeometry(100, 100, 500, 400)
        self.setStyleSheet("background-color: #46466d;")

        self.level_mode = 1
        self.score = 0
        self.level = 1
        self.sequence = ""
        self.display_time = 1500

        self.setStyleSheet("""
            QWidget {
                background-color: #46466d;
                color: #ffffff;
                font-family: 'Segoe UI', sans-serif;
            }
            
            QLabel {
                color: #e0e0f0;
                font-size: 25px;
            }
            
            QPushButton {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                                  stop:0 #3e3e70, stop:1 #5c5cb0);
                border: none;
                border-radius: 12px;
                padding: 10px 24px;
                color: #ffffff;
                font-size: 15px;
                font-weight: bold;
                box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.3);
                transition: all 0.3s ease;
            }
            
            QPushButton:hover {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                                  stop:0 #5c5cb0, stop:1 #7878d1);
                transform: scale(1.02);
            }
            
            QPushButton:pressed {
                background-color: #4b4b8d;
                transform: scale(0.98);
            }
            
            QLineEdit {
                background-color: #2a2a4a;
                border: 2px solid #44446b;
                border-radius: 10px;
                padding: 10px;
                color: #ffffff;
                font-size: 16px;
                selection-background-color: #5c5cb0;
                transition: border-color 0.2s ease;
            }
            
            QLineEdit:focus {
                border: 2px solid #7878d1;
            }

        """)

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self.menu_screen = self.create_menu_screen()
        self.sequence_screen = self.create_sequence_screen()
        self.input_screen = self.create_input_screen()

        self.stacked_widget.addWidget(self.menu_screen)
        self.stacked_widget.addWidget(self.sequence_screen)
        self.stacked_widget.addWidget(self.input_screen)

        self.show_menu()

        self.seq_anim = None
        self.feedback_anim = None

    def create_menu_screen(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignCenter)

        title = QLabel("Выберите уровень сложности")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #ffffff;")
        layout.addWidget(title)

        for text, mode in (("1 — Только цифры", 1),
                           ("2 — Цифры и буквы", 2),
                           ("3 — Все символы", 3)):
            btn = QPushButton(text)
            btn.setFont(QFont("Segoe UI", 14))
            btn.setStyleSheet("""color: #ffffff;""")
            btn.setFixedWidth(250)
            btn.clicked.connect(lambda checked, m=mode: self.start_game(m))
            layout.addWidget(btn, alignment=Qt.AlignCenter)

        return widget

    def create_sequence_screen(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignCenter)

        self.info_label = QLabel()
        self.info_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        self.info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.info_label)

        self.sequence_label = QLabel()
        self.sequence_label.setFont(QFont("Courier", 36, QFont.Bold))
        self.sequence_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.sequence_label)

        self.opacity_effect = QGraphicsOpacityEffect()
        self.sequence_label.setGraphicsEffect(self.opacity_effect)

        return widget

    def create_input_screen(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignCenter)

        self.level_info_label = QLabel()
        self.level_info_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        self.level_info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.level_info_label)

        self.input_prompt = QLabel()
        self.input_prompt.setFont(QFont("Segoe UI", 14))
        self.input_prompt.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.input_prompt)

        self.input_line = QLineEdit()
        self.input_line.setFont(QFont("Courier", 20))
        self.input_line.setAlignment(Qt.AlignCenter)
        self.input_line.setFixedWidth(300)
        layout.addWidget(self.input_line, alignment=Qt.AlignCenter)

        submit_btn = QPushButton("Проверить")
        submit_btn.setFont(QFont("Segoe UI", 14))
        submit_btn.setFixedWidth(200)
        submit_btn.clicked.connect(self.check_input)
        layout.addWidget(submit_btn, alignment=Qt.AlignCenter)

        self.feedback_label = QLabel("")
        self.feedback_label.setFont(QFont("Segoe UI", 14))
        self.feedback_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.feedback_label)
        return widget

    def show_menu(self):
        self.stacked_widget.setCurrentWidget(self.menu_screen)

    def start_game(self, mode):
        self.level_mode = mode
        self.score = 0
        self.level = 1
        self.next_level()

    def generate_sequence(self, length):
        if self.level_mode == 1:
            characters = string.digits
        elif self.level_mode == 2:
            characters = string.ascii_letters + string.digits
        else:
            characters = string.ascii_letters + string.digits + string.punctuation
        return ''.join(random.choice(characters) for _ in range(length))

    def next_level(self):
        self.sequence = self.generate_sequence(self.level)
        self.update_sequence_screen()
        self.stacked_widget.setCurrentWidget(self.sequence_screen)
        self.opacity_effect.setOpacity(1.0)
        QTimer.singleShot(self.display_time, self.fade_out_sequence)

    def update_sequence_screen(self):
        self.info_label.setText(f"Уровень {self.level}   |   Очки: {self.score}")
        self.sequence_label.setText(self.sequence)

    def fade_out_sequence(self):
        self.seq_anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.seq_anim.setDuration(1000)
        self.seq_anim.setStartValue(1.0)
        self.seq_anim.setEndValue(0.0)
        self.seq_anim.finished.connect(self.show_input_screen)
        self.seq_anim.start()

    def show_input_screen(self):
        self.level_info_label.setText(f"Уровень {self.level}   |   Очки: {self.score}")
        self.input_prompt.setText(f"Введите {self.level} символ(а/ов):")
        self.input_line.clear()
        self.feedback_label.setText("")
        self.stacked_widget.setCurrentWidget(self.input_screen)
        self.input_line.setFocus()

    def check_input(self):
        user_input = self.input_line.text()
        if len(user_input) != self.level:
            self.show_feedback(f"Введите ровно {self.level} символ(а/ов)!", "warning")
            return

        if user_input == self.sequence:
            self.score += 1
            self.level += 1
            self.show_feedback("Правильно! Переходим на следующий уровень", "correct")
            QTimer.singleShot(1500, self.next_level)
        else:
            wrong_text = (f"Неправильно!\nПравильная последовательность: {self.sequence}\n"
                          f"Ваш счёт: {self.score}")
            self.show_feedback(wrong_text, "wrong")
            QTimer.singleShot(2500, self.show_menu)

    def show_feedback(self, text, fb_type):
        self.feedback_label.setText(text)
        if fb_type == "correct":
            self.feedback_label.setStyleSheet("color: #34d399;")
        elif fb_type == "wrong":
            self.feedback_label.setStyleSheet("color: #f87171;")
        elif fb_type == "warning":
            self.feedback_label.setStyleSheet("color: #facc15;")

        effect = QGraphicsOpacityEffect()
        self.feedback_label.setGraphicsEffect(effect)
        effect.setOpacity(1.0)
        self.feedback_anim = QPropertyAnimation(effect, b"opacity")
        self.feedback_anim.setDuration(2000)
        self.feedback_anim.setStartValue(1.0)
        self.feedback_anim.setEndValue(0.0)
        self.feedback_anim.start()
        QTimer.singleShot(1000, lambda: self.feedback_label.setText(""))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    game = MemoryGame()
    game.show()
    sys.exit(app.exec_())