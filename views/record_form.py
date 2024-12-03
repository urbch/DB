from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QLabel, QMessageBox


class RecordForm(QDialog):
    def __init__(self, db, mode, record_id=None):
        super().__init__()
        self.db = db
        self.mode = mode
        self.record_id = record_id
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Добавить запись" if self.mode == "add" else "Изменить запись")
        self.setFixedSize(300, 150)

        layout = QVBoxLayout()

        # Поле ввода для наименования
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Введите наименование")
        layout.addWidget(QLabel("Наименование:"))
        layout.addWidget(self.name_input)

        # Кнопка подтверждения
        self.save_button = QPushButton("Сохранить")
        self.save_button.clicked.connect(self.handle_save)
        layout.addWidget(self.save_button)

        self.setLayout(layout)

        # Если режим редактирования, загрузить данные записи
        if self.mode == "edit" and self.record_id:
            self.load_record()

    def load_record(self):
        try:
            record = self.db.query("SELECT name FROM expense_items WHERE id = %s", (self.record_id,))
            if record:
                self.name_input.setText(record[0]['name'])
            else:
                QMessageBox.warning(self, "Ошибка", "Запись не найдена.")
                self.reject()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить запись: {e}")
            self.reject()

    def handle_save(self):
        name = self.name_input.text().strip()

        if not name:
            QMessageBox.warning(self, "Ошибка", "Наименование не может быть пустым.")
            return

        try:
            if self.mode == "add":
                self.db.execute("INSERT INTO expense_items (name) VALUES (%s)", (name,))
            elif self.mode == "edit" and self.record_id:
                self.db.execute("UPDATE expense_items SET name = %s WHERE id = %s", (name, self.record_id))
            QMessageBox.information(self, "Успех", "Запись успешно сохранена.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить запись: {e}")
