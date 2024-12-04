from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QHBoxLayout, QComboBox, QDateEdit, QMessageBox, QLabel, QLineEdit
from PyQt5.QtCore import Qt
from datetime import datetime

class JournalView(QDialog):
    def __init__(self, db, journal_type, user_role):
        """
        Инициализация окна. journal_type указывает, какой тип журнала:
        'sales' для журнала продаж и 'charges' для журнала расходов.
        """
        super().__init__()
        self.db = db
        self.journal_type = journal_type  # Тип журнала ('sales' или 'charges')
        self.user_role = user_role
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Журнал")
        self.setFixedSize(800, 600)

        layout = QVBoxLayout()

        # Таблица
        self.table = QTableWidget()
        if self.journal_type == "sales":
            self.table.setColumnCount(5)
            self.table.setHorizontalHeaderLabels(["ID", "Товар", "Дата продажи", "Количество", "Цена за единицу"])
        elif self.journal_type == "charges":
            self.table.setColumnCount(4)
            self.table.setHorizontalHeaderLabels(["ID", "Статья расхода", "Дата", "Сумма"])

        self.table.setEditTriggers(QTableWidget.NoEditTriggers)  # Только просмотр
        layout.addWidget(self.table)

        # Кнопки управления
        button_layout = QHBoxLayout()
        if self.user_role == "admin":
            self.add_button = QPushButton("Добавить")
            self.add_button.clicked.connect(self.add_record)
            button_layout.addWidget(self.add_button)

            self.edit_button = QPushButton("Изменить")
            self.edit_button.clicked.connect(self.edit_record)
            button_layout.addWidget(self.edit_button)

            self.delete_button = QPushButton("Удалить")
            self.delete_button.clicked.connect(self.delete_record)
            button_layout.addWidget(self.delete_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

        # Загрузка данных
        self.load_data()

    def load_data(self):
        try:
            if self.journal_type == "sales":
                # Загрузка данных о продажах
                data = self.db.query("""
                    SELECT s.id, w.name AS warehouse_name, s.sale_date, s.quantity, s.amount
                    FROM sales s
                    JOIN warehouses w ON s.warehouse_id = w.id
                    ORDER BY s.sale_date DESC
                """)
                self.table.setRowCount(len(data))
                for row_idx, row in enumerate(data):
                    self.table.setItem(row_idx, 0, QTableWidgetItem(str(row['id'])))
                    self.table.setItem(row_idx, 1, QTableWidgetItem(row['warehouse_name']))
                    self.table.setItem(row_idx, 2, QTableWidgetItem(row['sale_date'].strftime('%Y-%m-%d %H:%M:%S')))
                    self.table.setItem(row_idx, 3, QTableWidgetItem(str(row['quantity'])))
                    self.table.setItem(row_idx, 4, QTableWidgetItem(str(row['amount'])))

            elif self.journal_type == "charges":
                # Загрузка данных о расходах
                data = self.db.query("""
                    SELECT c.id, e.name AS expense_item, c.charge_date, c.amount
                    FROM charges c
                    JOIN expense_items e ON c.expense_item_id = e.id
                    ORDER BY c.charge_date DESC
                """)
                self.table.setRowCount(len(data))
                for row_idx, row in enumerate(data):
                    self.table.setItem(row_idx, 0, QTableWidgetItem(str(row['id'])))
                    self.table.setItem(row_idx, 1, QTableWidgetItem(row['expense_item']))
                    self.table.setItem(row_idx, 2, QTableWidgetItem(row['charge_date'].strftime('%Y-%m-%d')))
                    self.table.setItem(row_idx, 3, QTableWidgetItem(str(row['amount'])))
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить данные: {e}")

    def add_record(self):
        # В зависимости от типа журнала, создаем соответствующую форму для добавления
        if self.journal_type == "sales":
            form = SalesForm(self.db, mode="add")
        elif self.journal_type == "charges":
            form = ChargesForm(self.db, mode="add")
        if form.exec_():
            self.load_data()

    def edit_record(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите запись для изменения.")
            return

        record_id = self.table.item(selected_row, 0).text()
        if self.journal_type == "sales":
            form = SalesForm(self.db, mode="edit", record_id=record_id)
        elif self.journal_type == "charges":
            form = ChargesForm(self.db, mode="edit", record_id=record_id)
        if form.exec_():
            self.load_data()

    def delete_record(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите запись для удаления.")
            return

        record_id = self.table.item(selected_row, 0).text()
        confirm = QMessageBox.question(
            self, "Удаление", "Вы уверены, что хотите удалить запись?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            try:
                if self.journal_type == "sales":
                    self.db.execute("DELETE FROM sales WHERE id = %s", (record_id,))
                elif self.journal_type == "charges":
                    self.db.execute("DELETE FROM charges WHERE id = %s", (record_id,))
                self.load_data()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось удалить запись: {e}")


class SalesForm(QDialog):
    def __init__(self, db, mode, record_id=None):
        super().__init__()
        self.db = db
        self.mode = mode
        self.record_id = record_id
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Добавить запись в журнал продаж" if self.mode == "add" else "Изменить запись в журнале продаж")
        self.setFixedSize(300, 250)

        layout = QVBoxLayout()

        # Поля для продажи
        self.warehouse_combo = QComboBox()
        warehouses = self.db.query("SELECT id, name FROM warehouses")
        for warehouse in warehouses:
            self.warehouse_combo.addItem(warehouse['name'], warehouse['id'])
        layout.addWidget(QLabel("Товар:"))
        layout.addWidget(self.warehouse_combo)

        self.date_input = QDateEdit()
        self.date_input.setDate(datetime.today())
        layout.addWidget(QLabel("Дата продажи:"))
        layout.addWidget(self.date_input)

        self.quantity_input = QLineEdit()
        self.quantity_input.setPlaceholderText("Количество")
        layout.addWidget(QLabel("Количество:"))
        layout.addWidget(self.quantity_input)

        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Цена за единицу")
        layout.addWidget(QLabel("Цена за единицу:"))
        layout.addWidget(self.amount_input)

        self.save_button = QPushButton("Сохранить")
        self.save_button.clicked.connect(self.handle_save)
        layout.addWidget(self.save_button)

        self.setLayout(layout)

        if self.mode == "edit" and self.record_id:
            self.load_record()

    def load_record(self):
        try:
            record = self.db.query("SELECT warehouse_id, sale_date, quantity, amount FROM sales WHERE id = %s", (self.record_id,))
            if record:
                self.warehouse_combo.setCurrentIndex(self.warehouse_combo.findData(record[0]['warehouse_id']))
                self.date_input.setDate(record[0]['sale_date'])
                self.quantity_input.setText(str(record[0]['quantity']))
                self.amount_input.setText(str(record[0]['amount']))
            else:
                QMessageBox.warning(self, "Ошибка", "Запись не найдена.")
                self.reject()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить запись: {e}")
            self.reject()

    def handle_save(self):
        warehouse_id = self.warehouse_combo.currentData()
        sale_date = self.date_input.date().toPyDate()
        quantity = self.quantity_input.text().strip()
        amount = self.amount_input.text().strip()

        if not warehouse_id or not sale_date or not quantity or not amount:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, заполните все поля.")
            return

        try:
            if self.mode == "add":
                self.db.execute("INSERT INTO sales (warehouse_id, sale_date, quantity, amount) VALUES (%s, %s, %s, %s)",
                                 (warehouse_id, sale_date, quantity, amount))
            elif self.mode == "edit" and self.record_id:
                self.db.execute("UPDATE sales SET warehouse_id = %s, sale_date = %s, quantity = %s, amount = %s WHERE id = %s",
                                 (warehouse_id, sale_date, quantity, amount, self.record_id))
            QMessageBox.information(self, "Успех", "Запись успешно сохранена.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить запись: {e}")


class ChargesForm(QDialog):
    def __init__(self, db, mode, record_id=None):
        super().__init__()
        self.db = db
        self.mode = mode
        self.record_id = record_id
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Добавить запись в журнал расходов" if self.mode == "add" else "Изменить запись в журнале расходов")
        self.setFixedSize(300, 200)

        layout = QVBoxLayout()

        # Поля для расхода
        self.expense_item_combo = QComboBox()
        expense_items = self.db.query("SELECT id, name FROM expense_items")
        for item in expense_items:
            self.expense_item_combo.addItem(item['name'], item['id'])
        layout.addWidget(QLabel("Статья расхода:"))
        layout.addWidget(self.expense_item_combo)

        self.date_input = QDateEdit()
        self.date_input.setDate(datetime.today())
        layout.addWidget(QLabel("Дата расхода:"))
        layout.addWidget(self.date_input)

        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Сумма")
        layout.addWidget(QLabel("Сумма:"))
        layout.addWidget(self.amount_input)

        self.save_button = QPushButton("Сохранить")
        self.save_button.clicked.connect(self.handle_save)
        layout.addWidget(self.save_button)

        self.setLayout(layout)

        if self.mode == "edit" and self.record_id:
            self.load_record()

    def load_record(self):
        try:
            record = self.db.query("SELECT expense_item_id, charge_date, amount FROM charges WHERE id = %s", (self.record_id,))
            if record:
                self.expense_item_combo.setCurrentIndex(self.expense_item_combo.findData(record[0]['expense_item_id']))
                self.date_input.setDate(record[0]['charge_date'])
                self.amount_input.setText(str(record[0]['amount']))
            else:
                QMessageBox.warning(self, "Ошибка", "Запись не найдена.")
                self.reject()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить запись: {e}")
            self.reject()

    def handle_save(self):
        expense_item_id = self.expense_item_combo.currentData()
        charge_date = self.date_input.date().toPyDate()
        amount = self.amount_input.text().strip()

        if not expense_item_id or not charge_date or not amount:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, заполните все поля.")
            return

        try:
            if self.mode == "add":
                self.db.execute("INSERT INTO charges (expense_item_id, charge_date, amount) VALUES (%s, %s, %s)",
                                 (expense_item_id, charge_date, amount))
            elif self.mode == "edit" and self.record_id:
                self.db.execute("UPDATE charges SET expense_item_id = %s, charge_date = %s, amount = %s WHERE id = %s",
                                 (expense_item_id, charge_date, amount, self.record_id))
            QMessageBox.information(self, "Успех", "Запись успешно сохранена.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить запись: {e}")
