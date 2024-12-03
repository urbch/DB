from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QLabel, QMessageBox


class RecordForm(QDialog):
    def __init__(self, db, mode, record_id=None, table_type=None):
        super().__init__()
        self.db = db
        self.mode = mode
        self.record_id = record_id
        self.table_type = table_type
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Добавить запись" if self.mode == "add" else "Изменить запись")
        self.setFixedSize(300, 200)

        layout = QVBoxLayout()

        if self.table_type == "expense_items":
            # Поле ввода для наименования статьи расхода
            self.name_input = QLineEdit()
            self.name_input.setPlaceholderText("Введите наименование статьи расхода")
            layout.addWidget(QLabel("Наименование статьи:"))
            layout.addWidget(self.name_input)

        elif self.table_type == "warehouses":
            # Поля ввода для товара
            self.name_input = QLineEdit()
            self.name_input.setPlaceholderText("Введите наименование товара")
            layout.addWidget(QLabel("Наименование товара:"))
            layout.addWidget(self.name_input)

            self.quantity_input = QLineEdit()
            self.quantity_input.setPlaceholderText("Введите количество")
            layout.addWidget(QLabel("Количество:"))
            layout.addWidget(self.quantity_input)

            self.amount_input = QLineEdit()
            self.amount_input.setPlaceholderText("Введите стоимость товара")
            layout.addWidget(QLabel("Стоимость:"))
            layout.addWidget(self.amount_input)

        # Кнопка сохранения
        self.save_button = QPushButton("Сохранить")
        self.save_button.clicked.connect(self.handle_save)
        layout.addWidget(self.save_button)

        self.setLayout(layout)

        if self.mode == "edit" and self.record_id:
            self.load_record()

    def load_record(self):
        try:
            if self.table_type == "expense_items":
                record = self.db.query("SELECT name FROM expense_items WHERE id = %s", (self.record_id,))
                if record:
                    self.name_input.setText(record[0]['name'])
                else:
                    QMessageBox.warning(self, "Ошибка", "Запись не найдена.")
                    self.reject()

            elif self.table_type == "warehouses":
                record = self.db.query("SELECT name, quantity, amount FROM warehouses WHERE id = %s", (self.record_id,))
                if record:
                    self.name_input.setText(record[0]['name'])
                    self.quantity_input.setText(str(record[0]['quantity']))
                    self.amount_input.setText(str(record[0]['amount']))
                else:
                    QMessageBox.warning(self, "Ошибка", "Запись не найдена.")
                    self.reject()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить запись: {e}")
            self.reject()

    def handle_save(self):
        name = self.name_input.text().strip()

        if self.table_type == "expense_items":
            if not name:
                QMessageBox.warning(self, "Ошибка", "Наименование статьи расхода не может быть пустым.")
                return
        elif self.table_type == "warehouses":
            quantity = self.quantity_input.text().strip()
            amount = self.amount_input.text().strip()
            if not name or not quantity or not amount:
                QMessageBox.warning(self, "Ошибка", "Все поля должны быть заполнены.")
                return

        try:
            if self.mode == "add":
                if self.table_type == "expense_items":
                    self.db.execute("INSERT INTO expense_items (name) VALUES (%s)", (name,))
                elif self.table_type == "warehouses":
                    self.db.execute("INSERT INTO warehouses (name, quantity, amount) VALUES (%s, %s, %s)",
                                    (name, quantity, amount))
            elif self.mode == "edit" and self.record_id:
                if self.table_type == "expense_items":
                    self.db.execute("UPDATE expense_items SET name = %s WHERE id = %s", (name, self.record_id))
                elif self.table_type == "warehouses":
                    self.db.execute("UPDATE warehouses SET name = %s, quantity = %s, amount = %s WHERE id = %s",
                                    (name, quantity, amount, self.record_id))

            QMessageBox.information(self, "Успех", "Запись успешно сохранена.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить запись: {e}")
