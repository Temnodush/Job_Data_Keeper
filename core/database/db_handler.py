import psycopg2
from core.utils.config_loader import get_db_config


def initialize_database(db_name: str = "career_db") -> None:
    """Создаёт базу данных и таблицы при первом запуске"""
    params = get_db_config()
    admin_params = params.copy()
    admin_params["dbname"] = "postgres"

    try:
        # Подключение к системной БД
        conn = psycopg2.connect(**admin_params)
        conn.autocommit = True
        cur = conn.cursor()

        # Проверка существования БД
        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
        exists = cur.fetchone()

        if not exists:
            cur.execute(f"CREATE DATABASE {db_name}")
            print(f"База данных {db_name} создана")
        else:
            print(f"База данных {db_name} уже существует")

        cur.close()
        conn.close()

        # Подключение к новой БД для создания таблиц
        params["dbname"] = db_name
        conn = psycopg2.connect(**params)
        cur = conn.cursor()

        # Создание таблицы работодателей
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS employers (
                id VARCHAR(20) PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                location VARCHAR(100),
                website TEXT
            )
        """
        )

        # Создание таблицы вакансий
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS vacancies (
                id VARCHAR(20) PRIMARY KEY,
                employer_id VARCHAR(20) NOT NULL REFERENCES employers(id) ON DELETE CASCADE,
                title VARCHAR(255) NOT NULL,
                min_salary INTEGER,
                max_salary INTEGER,
                currency VARCHAR(10),
                url TEXT NOT NULL,
                description TEXT
            )
        """
        )

        conn.commit()
        print("Таблицы созданы успешно")

    except psycopg2.errors.DuplicateDatabase:
        print(f"База данных {db_name} уже существует")
    except Exception as e:
        print(f"Ошибка инициализации БД: {e}")
    finally:
        if "cur" in locals() and cur:
            cur.close()
        if "conn" in locals() and conn:
            conn.close()
