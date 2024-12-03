from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QLabel, QHBoxLayout, QMessageBox, QTableWidget, QTableWidgetItem
from PyQt5.QtCore import Qt
import os


class ReportView(QDialog):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Отчеты")
        self.setFixedSize(600, 400)

        layout = QVBoxLayout()

        # Выбор отчета
        self.label = QLabel("Выберите отчет:")
        layout.addWidget(self.label)

        self.profit_button = QPushButton("Прибыль за месяц")
        self.profit_button.clicked.connect(self.generate_profit_report)
        layout.addWidget(self.profit_button)

        self.top_items_button = QPushButton("Топ товаров за интервал")
        self.top_items_button.clicked.connect(self.generate_top_items_report)
        layout.addWidget(self.top_items_button)

        # Результаты отчета
        self.result_table = QTableWidget()
        self.result_table.setColumnCount(2)
        self.result_table.setHorizontalHeaderLabels(["Название", "Значение"])
        layout.addWidget(self.result_table)

        self.save_button = QPushButton("Сохранить отчет")
        self.save_button.clicked.connect(self.save_report)
        layout.addWidget(self.save_button)

        self.setLayout(layout)

        self.current_report = []

    def generate_profit_report(self):
        try:
            result = self.db.query("""
                SELECT
                    SUM(s.amount * s.quantity) AS total_sales,
                    SUM(c.amount) AS total_expenses,
                    (SUM(s.amount * s.quantity) - SUM(c.amount)) AS profit
                FROM sales s, charges c
                WHERE EXTRACT(MONTH FROM s.sale_date) = EXTRACT(MONTH FROM CURRENT_DATE)
                AND EXTRACT(YEAR FROM s.sale_date) = EXTRACT(YEAR FROM CURRENT_DATE)
            """)
            self.current_report = [
                ("Общая выручка", result[0]['total_sales'] if result else 0),
                ("Общие расходы", result[0]['total_expenses'] if result else 0),
                ("Прибыль", result[0]['profit'] if result else 0),
            ]
            self.show_report()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сгенерировать отчет: {e}")

    def generate_top_items_report(self):
        try:
            result = self.db.query("""
                SELECT w.name AS item_name, SUM(s.amount * s.quantity) AS total_revenue
                FROM sales s
                JOIN warehouses w ON s.warehouse_id = w.id
                GROUP BY w.name
                ORDER BY total_revenue DESC
                LIMIT 5
            """)
            self.current_report = [(row['item_name'], row['total_revenue']) for row in result]
            self.show_report()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сгенерировать отчет: {e}")

    def show_report(self):
        self.result_table.setRowCount(len(self.current_report))
        for row_idx, (name, value) in enumerate(self.current_report):
            self.result_table.setItem(row_idx, 0, QTableWidgetItem(name))
            self.result_table.setItem(row_idx, 1, QTableWidgetItem(str(value)))

    def save_report(self):
        if not self.current_report:
            QMessageBox.warning(self, "Ошибка", "Нет данных для сохранения.")
            return

        try:
            file_path = "report.txt"
            with open(file_path, "w", encoding="utf-8") as file:
                for name, value in self.current_report:
                    file.write(f"{name}: {value}\n")
            QMessageBox.information(self, "Успех", f"Отчет сохранен в файл: {os.path.abspath(file_path)}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить отчет: {e}")
