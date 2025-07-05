from core.database.db_manager import DBManager


class CareerConsoleUI:
    """Консольный интерфейс для работы с данными о карьере"""

    def __init__(self, db_name: str = "career_db"):
        self.db_name = db_name

    def show_menu(self):
        """Отображает главное меню"""
        while True:
            print("\n=== Карьерный навигатор ===")
            print("1. Показать компании и количество вакансий")
            print("2. Показать все вакансии")
            print("3. Показать среднюю зарплату")
            print("4. Показать вакансии с зарплатой выше средней")
            print("5. Поиск вакансий по ключевому слову")
            print("0. Выход")

            choice = input("Выберите действие: ").strip()

            if choice == "1":
                self.show_companies()
            elif choice == "2":
                self.show_all_vacancies()
            elif choice == "3":
                self.show_avg_salary()
            elif choice == "4":
                self.show_high_salary_vacancies()
            elif choice == "5":
                self.search_vacancies()
            elif choice == "0":
                print("До свидания!")
                break
            else:
                print("Неверный ввод, попробуйте снова")

    def show_companies(self):
        """Показывает список компаний и количество вакансий"""
        with DBManager(self.db_name) as db:
            companies = db.get_companies_and_vacancies_count()

            if not companies:
                print("Нет данных о компаниях")
                return

            print("\nКомпании и количество вакансий:")
            for name, count in companies:
                print(f"- {name}: {count} вакансий")

    def show_all_vacancies(self):
        """Показывает все вакансии"""
        with DBManager(self.db_name) as db:
            vacancies = db.get_all_vacancies()

            if not vacancies:
                print("Нет данных о вакансиях")
                return

            print("\nВсе вакансии:")
            for company, title, min_sal, max_sal, currency, url in vacancies:
                salary_info = self.format_salary(min_sal, max_sal, currency)
                print(f"Компания: {company}, Вакансия: {title}")
                print(f"Зарплата: {salary_info}")
                print(f"Ссылка: {url}\n")

    def show_avg_salary(self):
        """Показывает среднюю зарплату"""
        with DBManager(self.db_name) as db:
            avg_salary = db.get_avg_salary()

            if avg_salary:
                print(f"\nСредняя зарплата: {avg_salary:.2f} RUB")
            else:
                print("\nНедостаточно данных для расчёта зарплаты")

    def show_high_salary_vacancies(self):
        """Показывает вакансии с зарплатой выше средней"""
        with DBManager(self.db_name) as db:
            vacancies = db.get_vacancies_with_higher_salary()

            if not vacancies:
                print("Нет вакансий с зарплатой выше средней")
                return

            print("\nВакансии с зарплатой выше средней:")
            for company, title, min_sal, max_sal, currency, url in vacancies:
                salary_info = self.format_salary(min_sal, max_sal, currency)
                print(f"Компания: {company}, Вакансия: {title}")
                print(f"Зарплата: {salary_info}")
                print(f"Ссылка: {url}\n")

    def search_vacancies(self):
        """Ищет вакансии по ключевому слову"""
        keyword = input("Введите ключевое слово: ").strip()
        if not keyword:
            print("Ключевое слово не может быть пустым")
            return

        with DBManager(self.db_name) as db:
            vacancies = db.get_vacancies_with_keyword(keyword)

            if not vacancies:
                print(f"По запросу '{keyword}' вакансий не найдено")
                return

            print(f"\nРезультаты поиска по '{keyword}':")
            for company, title, min_sal, max_sal, currency, url in vacancies:
                salary_info = self.format_salary(min_sal, max_sal, currency)
                print(f"Компания: {company}, Вакансия: {title}")
                print(f"Зарплата: {salary_info}")
                print(f"Ссылка: {url}\n")

    @staticmethod
    def format_salary(min_sal: int, max_sal: int, currency: str) -> str:
        """Форматирует информацию о зарплате"""
        if min_sal and max_sal:
            return f"{min_sal}-{max_sal} {currency}"
        elif min_sal:
            return f"от {min_sal} {currency}"
        elif max_sal:
            return f"до {max_sal} {currency}"
        return "не указана"
