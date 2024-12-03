from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QHBoxLayout, QMessageBox
from PyQt5.QtCore import Qt
from views.record_form import RecordForm


class JournalView(QDialog):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Журналы")
        self.setFixedSize(800, 500)

        layout = QVBoxLayout()

        # Таблица
        self.table = QTableWidget()
        self.table.setColumnCount(5)  # Количество столбцов зависит от текущего журнала
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)  # Только просмотр
        layout.addWidget(self.table)

        # Кнопки управления
        button_layout = QHBoxLayout()
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
            # Загрузка данных зависит от контекста журнала (например, продажи или расходы)
            # Пример для журнала расходов:
            data = self.db.query("""
                SELECT c.id, e.name AS expense_item, c.amount, c.charge_date
                FROM charges c
                JOIN expense_items e ON c.expense_item_id = e.id
                ORDER BY c.charge_date DESC
            """)
            self.table.setColumnCount(4)
            self.table.setHorizontalHeaderLabels(["ID", "Статья расхода", "Сумма", "Дата"])
            self.table.setRowCount(len(data))
            for row_idx, row in enumerate(data):
                self.table.setItem(row_idx, 0, QTableWidgetItem(str(row['id'])))
                self.table.setItem(row_idx, 1, QTableWidgetItem(row['expense_item']))
                self.table.setItem(row_idx, 2, QTableWidgetItem(str(row['amount'])))
                self.table.setItem(row_idx, 3, QTableWidgetItem(row['charge_date']))
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить данные: {e}")

    def add_record(self):
        form = RecordForm(self.db, mode="add")
        if form.exec_():
            self.load_data()

    def edit_record(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите запись для изменения.")
            return

        record_id = self.table.item(selected_row, 0).text()
        form = RecordForm(self.db, mode="edit", record_id=record_id)
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
                self.db.execute("DELETE FROM charges WHERE id = %s", (record_id,))
                self.load_data()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось удалить запись: {e}")
