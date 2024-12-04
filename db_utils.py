import psycopg2
from psycopg2.extras import RealDictCursor
import hashlib


class Database:
    def __init__(self, host, port, dbname, user, password):
        try:
            self.conn = psycopg2.connect(
                host=host,
                port=port,
                dbname=dbname,
                user=user,
                password=password
            )
            self.conn.autocommit = True
        except Exception as e:
            raise Exception(f"Ошибка подключения к базе данных: {e}")

    def query(self, sql, params=None):
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(sql, params)
                if cursor.description:  # Если запрос возвращает результат
                    return cursor.fetchall()
        except Exception as e:
            raise Exception(f"Ошибка выполнения запроса: {e}")

    def execute(self, sql, params=None):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(sql, params)
                self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            raise Exception(f"Ошибка выполнения команды: {e}")


    def close(self):
        if self.conn:
            self.conn.close()

    # Методы для авторизации
    def get_user(self, username):
        sql = "SELECT * FROM users WHERE username = %s"
        result = self.query(sql, (username,))
        return result[0] if result else None

    def verify_password(self, username, password):
        user = self.get_user(username)
        if user and hashlib.sha256(user['password_hash'].encode('utf-8')).hexdigest():
            return user
        return None

    def calculate_monthly_profit(self):
        try:
            # Вызов хранимой процедуры для расчета прибыли за месяц
            result = self.query("SELECT * FROM calculate_monthly_profit()")
            return result[0] if result else None
        except Exception as e:
            raise Exception(f"Не удалось рассчитать прибыль: {e}")

    def get_top_5_revenue_items(self, start_date, end_date):
        try:
            # Вызов хранимой процедуры для получения топ-5 товаров по выручке
            result = self.query("SELECT * FROM top_5_revenue_items(%s, %s)", (start_date, end_date))
            return result
        except Exception as e:
            raise Exception(f"Не удалось получить топ-5 товаров: {e}")