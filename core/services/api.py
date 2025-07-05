import requests
from typing import List, Optional, Dict
from core.utils.config_loader import get_api_config


class HeadHunterAPI:
    """Класс для работы с API HeadHunter"""

    def __init__(self):
        self.base_url = "https://api.hh.ru"
        self.headers = {"User-Agent": get_api_config().get("user_agent")}
        self.session = requests.Session()

    def test_connection(self) -> bool:
        """Проверяет доступность API"""
        try:
            response = self.session.get(f"{self.base_url}/vacancies", headers=self.headers)
            return response.status_code == 200
        except requests.RequestException:
            return False

    def get_employer_id_by_name(self, name: str) -> Optional[str]:
        """Ищет ID работодателя по названию с улучшенным поиском"""
        # Сначала проверяем известные компании
        known_id = self.get_known_employer_id(name)
        if known_id:
            return known_id

        # Если не найдено в известных, ищем через API
        try:
            # Пробуем разные варианты написания названия
            search_queries = [name, name + " компания", name + " группа"]

            for query in search_queries:
                params = {"text": query, "per_page": 1, "only_with_vacancies": True}
                response = self.session.get(
                    f"{self.base_url}/employers", params=params, headers=self.headers, timeout=10
                )
                response.raise_for_status()
                data = response.json()
                items = data.get("items", [])

                if items:
                    # Берем первый результат
                    employer = items[0]
                    # Проверяем, что название хотя бы частично совпадает
                    if name.lower() in employer.get("name", "").lower():
                        return employer.get("id")

            return None
        except Exception as e:
            print(f"Ошибка поиска работодателя {name}: {e}")
            return None

    def get_vacancies_by_employer_id(self, employer_id: str, per_page: int = 20) -> List[Dict]:
        """Получает вакансии работодателя по ID"""
        try:
            params = {"employer_id": employer_id, "per_page": per_page}
            if employer_id == "39305":
                params["host"] = "hh.ru"

            response = self.session.get(f"{self.base_url}/vacancies", params=params, headers=self.headers, timeout=15)
            response.raise_for_status()
            data = response.json()
            return data.get("items", [])
        except Exception as e:
            print(f"Ошибка получения вакансий для работодателя {employer_id}: {e}")
            return []

    def get_employer_info(self, employer_id: str) -> Optional[Dict]:
        """Получает информацию о работодателе по ID"""
        try:
            response = self.session.get(f"{self.base_url}/employers/{employer_id}", headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Ошибка получения информации о работодателе {employer_id}: {e}")
            return None

    def get_known_employer_id(self, name: str) -> Optional[str]:
        """Возвращает ID для известных компаний по предопределенному списку"""
        known_companies = {
            "яндекс": "1740",
            "yandex": "1740",
            "сбербанк": "3529",
            "sberbank": "3529",
            "sber": "3529",
            "газпром": "39305",
            "gazprom": "39305",
            "x5": "6093775",
            "x5 group": "6093775",
            "лср": "1473868",
            "lsr": "1473868",
            "vk": "15478",
            "вконтакте": "15478",
        }

        # Ищем в разных вариантах написания
        for key, value in known_companies.items():
            if key in name.lower():
                return value

        return None
