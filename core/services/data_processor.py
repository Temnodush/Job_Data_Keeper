import time
import traceback
from core.data_models.employer import Employer
from core.data_models.vacancy import Vacancy
from core.database.db_manager import DBManager
from core.services.api import HeadHunterAPI


class DataProcessor:
    """Обработчик данных: API → База данных"""

    def __init__(self, db_name: str = "career_db"):
        self.api = HeadHunterAPI()
        self.db_name = db_name
        self.vacancies_per_employer = 20

    def load_by_names(self, company_names: list) -> bool:
        """Загружает данные по списку названий компаний"""
        if not self.api.test_connection():
            print("❌ Ошибка подключения к API HeadHunter")
            return False

        try:
            db = DBManager(self.db_name)
            if not db.connect():
                print("❌ Не удалось подключиться к базе данных")
                return False

            for name in company_names:
                print(f"\n🔍 Обработка компании: {name}")

                # Поиск ID компании
                employer_id = self.api.get_employer_id_by_name(name)
                if not employer_id:
                    print(f"⚠️ Не найден ID для компании: {name}")
                    continue
                print(f"✅ Найден ID компании: {employer_id}")

                # Получение информации о компании
                employer_info = self.api.get_employer_info(employer_id)
                if not employer_info:
                    print(f"⚠️ Не удалось получить информацию о компании: {name} ({employer_id})")
                    continue
                print(f"📄 Получена информация о компании: {employer_info.get('name')}")

                # Создание и сохранение работодателя
                employer = Employer.from_api_response(employer_info)
                if not db.save_employer(employer):
                    print(f"❌ Ошибка сохранения работодателя: {name}")
                    continue
                print(f"💾 Работодатель сохранен: {employer.name}")

                # Получение вакансий
                vacancies_data = self.api.get_vacancies_by_employer_id(
                    employer_id, per_page=self.vacancies_per_employer
                )
                print(f"📋 Получено вакансий: {len(vacancies_data)}")

                # Сохранение вакансий
                saved_count = 0
                for vacancy_data in vacancies_data:
                    vacancy = Vacancy.from_api_response(vacancy_data)
                    if db.save_vacancy(vacancy):
                        saved_count += 1

                print(f"💾 Сохранено вакансий: {saved_count}/{len(vacancies_data)}")
                time.sleep(0.5)

            return True
        except Exception as e:
            print(f"⛔ Критическая ошибка в DataProcessor: {e}")
            traceback.print_exc()
            return False
        finally:
            if db:
                db.disconnect()

    def load_by_ids(self, employer_ids: list) -> bool | None:
        """Загружает данные по списку ID компаний"""
        if not self.api.test_connection():
            print("❌ Ошибка подключения к API")
            return False

        try:
            db = DBManager(self.db_name)
            if not db.connect():
                print("❌ Критическая ошибка: не удалось подключиться к БД")
                return False

            for employer_id in employer_ids:
                print(f"\n🔍 Обработка компании с ID: {employer_id}")

                # Получаем информацию о компании
                employer_info = self.api.get_employer_info(employer_id)
                if not employer_info:
                    print(f"⚠️ Не удалось получить информацию о компании с ID: {employer_id}")
                    continue

                # Создаем объект работодателя
                employer = Employer.from_api_response(employer_info)
                if not db.save_employer(employer):
                    print(f"❌ Ошибка сохранения работодателя: {employer.name} ({employer_id})")
                    continue
                print(f"💾 Работодатель сохранен: {employer.name}")

                # Получаем вакансии компании
                vacancies_data = self.api.get_vacancies_by_employer_id(
                    employer_id, per_page=self.vacancies_per_employer
                )
                print(f"📋 Получено вакансий: {len(vacancies_data)}")

                # Сохраняем вакансии
                saved_count = 0
                for vacancy_data in vacancies_data:
                    vacancy = Vacancy.from_api_response(vacancy_data)
                    if db.save_vacancy(vacancy):
                        saved_count += 1

                print(f"💾 Сохранено вакансий: {saved_count}/{len(vacancies_data)}")
                time.sleep(0.5)

            return True
        except Exception as e:
            print(f"⛔ Критическая ошибка при обработке: {e}")
            traceback.print_exc()
            return False
        finally:
            if db:
                db.disconnect()
