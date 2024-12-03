from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QLabel, QMessageBox
from PyQt5.QtCore import Qt


class LoginWindow(QDialog):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Авторизация")
        self.setFixedSize(300, 200)

        layout = QVBoxLayout()

        self.label = QLabel("Введите логин и пароль:")
        layout.addWidget(self.label)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Логин")
        layout.addWidget(self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Пароль")
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        self.login_button = QPushButton("Войти")
        self.login_button.clicked.connect(self.handle_login)
        layout.addWidget(self.login_button)

        self.setLayout(layout)

    def handle_login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if not username or not password:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, заполните все поля.")
            return

        try:
            user = self.db.verify_password(username, password)
            if user:
                QMessageBox.information(self, "Успех", "Вы успешно вошли в систему.")
                self.accept()  # Успешная авторизация
            else:
                QMessageBox.warning(self, "Ошибка", "Неверный логин или пароль.")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось выполнить вход: {e}")
