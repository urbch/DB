import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QMenuBar, QAction, QMessageBox, QDialog
from configparser import ConfigParser
from db_utils import Database
from auth import LoginWindow
from views.reference_view import ReferenceView
from views.journal_view import JournalView
from views.report_view import ReportView


class MainApp(QMainWindow):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Магазин - Управление")
        self.setGeometry(100, 100, 800, 600)

        # Меню
        menubar = self.menuBar()

        # Справочники
        references_menu = menubar.addMenu("Справочники")
        self.add_action(references_menu, "Товары", self.open_warehouses)
        self.add_action(references_menu, "Статьи расходов", self.open_expense_items)

        # Журналы
        journals_menu = menubar.addMenu("Журналы")
        self.add_action(journals_menu, "Продажи", self.open_sales)
        self.add_action(journals_menu, "Расходы", self.open_charges)

        # Отчеты
        reports_menu = menubar.addMenu("Отчеты")
        self.add_action(reports_menu, "Прибыль за месяц", self.open_report_view)
        self.add_action(reports_menu, "Топ товаров", self.open_report_view)

    def add_action(self, menu, title, callback):
        action = QAction(title, self)
        action.triggered.connect(callback)
        menu.addAction(action)

    # Методы открытия форм
    def open_expense_items(self):
        # Открыть справочник статей расходов
        reference_view = ReferenceView(self.db, "expense_items")  # Передаем 'expense_items' для статей расходов
        reference_view.exec_()

    def open_warehouses(self):
        # Открыть справочник товаров
        reference_view = ReferenceView(self.db, "warehouses")  # Передаем 'warehouses' для товаров
        reference_view.exec_()

    def open_sales(self):
        view = JournalView(self.db, "sales")
        view.exec_()

    def open_charges(self):
        view = JournalView(self.db, "charges")
        view.exec_()

    def open_report_view(self):
        view = ReportView(self.db)
        view.exec_()


def load_config(file_path='config.ini'):
    config = ConfigParser()
    config.read(file_path)
    if 'database' not in config:
        raise Exception("Конфигурация базы данных не найдена в config.ini.")
    return config['database']


def main():
    try:
        config = load_config()
        db = Database(
            host=config['host'],
            port=config['port'],
            dbname=config['dbname'],
            user=config['user'],
            password=config['password']
        )
    except Exception as e:
        QMessageBox.critical(None, "Ошибка", f"Не удалось подключиться к базе данных: {str(e)}")
        sys.exit(1)

    app = QApplication(sys.argv)

    login_window = LoginWindow(db)
    if login_window.exec_() == QDialog.Accepted:
        main_app = MainApp(db)
        main_app.show()
        sys.exit(app.exec_())
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
