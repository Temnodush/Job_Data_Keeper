import psycopg2
from typing import List, Tuple, Optional
from core.utils.config_loader import get_db_config


class DBManager:
    """Управление взаимодействием с базой данных"""

    def __init__(self, db_name: str = "career_db"):
        self.params = get_db_config()
        self.params["dbname"] = db_name
        self.connection = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

    def connect(self):
        """Устанавливает соединение с БД"""
        try:
            self.connection = psycopg2.connect(**self.params)
            return True
        except Exception as e:
            print(f"Ошибка подключения к БД: {e}")
            return False

    def disconnect(self):
        """Закрывает соединение с БД"""
        if self.connection:
            self.connection.close()

    def save_employer(self, employer) -> bool:
        """Сохраняет работодателя в БД"""
        try:
            with self.connection.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO employers (id, name, location, website)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (id) DO NOTHING
                    """,
                    employer.to_db_format(),
                )
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Ошибка сохранения работодателя: {e}")
            return False

    def save_vacancy(self, vacancy) -> bool:
        """Сохраняет вакансию в БД"""
        try:
            with self.connection.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO vacancies 
                    (id, employer_id, title, min_salary, max_salary, currency, url, description)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO NOTHING
                    """,
                    (
                        vacancy.id,
                        vacancy.employer_id,
                        vacancy.title,
                        vacancy.min_salary,
                        vacancy.max_salary,
                        vacancy.currency,
                        vacancy.url,
                        vacancy.description,
                    ),
                )
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Ошибка сохранения вакансии: {e}")
            return False

    def get_companies_and_vacancies_count(self) -> List[Tuple]:
        """Возвращает список работодателей с количеством вакансий"""
        try:
            with self.connection.cursor() as cur:
                cur.execute(
                    """
                    SELECT e.name, COUNT(v.id) 
                    FROM employers e
                    LEFT JOIN vacancies v ON e.id = v.employer_id
                    GROUP BY e.name
                    ORDER BY COUNT(v.id) DESC
                """
                )
                return cur.fetchall()
        except Exception as e:
            print(f"Ошибка получения данных: {e}")
            return []

    def get_avg_salary(self) -> Optional[float]:
        """Рассчитывает среднюю зарплату"""
        try:
            with self.connection.cursor() as cur:
                cur.execute(
                    """
                    SELECT AVG((min_salary + max_salary) / 2)
                    FROM vacancies
                    WHERE min_salary IS NOT NULL 
                      AND max_salary IS NOT NULL
                """
                )
                result = cur.fetchone()
                return result[0] if result else None
        except Exception as e:
            print(f"Ошибка расчёта зарплаты: {e}")
            return None

    def get_all_vacancies(self) -> List[Tuple]:
        """Возвращает список всех вакансий"""
        try:
            with self.connection.cursor() as cur:
                cur.execute(
                    """
                    SELECT e.name, v.title, v.min_salary, v.max_salary, v.currency, v.url
                    FROM vacancies v
                    JOIN employers e ON v.employer_id = e.id
                """
                )
                return cur.fetchall()
        except Exception as e:
            print(f"Ошибка получения вакансий: {e}")
            return []

    def get_vacancies_with_higher_salary(self) -> List[Tuple]:
        """Возвращает вакансии с зарплатой выше средней"""
        avg_salary = self.get_avg_salary()
        if not avg_salary:
            return []

        try:
            with self.connection.cursor() as cur:
                cur.execute(
                    """
                    SELECT e.name, v.title, v.min_salary, v.max_salary, v.currency, v.url
                    FROM vacancies v
                    JOIN employers e ON v.employer_id = e.id
                    WHERE (v.min_salary + v.max_salary) / 2 > %s
                """,
                    (avg_salary,),
                )
                return cur.fetchall()
        except Exception as e:
            print(f"Ошибка получения вакансий: {e}")
            return []

    def get_vacancies_with_keyword(self, keyword: str) -> List[Tuple]:
        """Возвращает вакансии по ключевому слову"""
        try:
            with self.connection.cursor() as cur:
                cur.execute(
                    """
                    SELECT e.name, v.title, v.min_salary, v.max_salary, v.currency, v.url
                    FROM vacancies v
                    JOIN employers e ON v.employer_id = e.id
                    WHERE v.title ILIKE %s
                """,
                    (f"%{keyword}%",),
                )
                return cur.fetchall()
        except Exception as e:
            print(f"Ошибка поиска вакансий: {e}")
            return []
