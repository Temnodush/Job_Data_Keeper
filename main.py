from core.database.db_handler import initialize_database
from core.services.data_processor import DataProcessor
from core.ui.console_ui import CareerConsoleUI

# Предопределенные ID известных компаний (можно расширять)
PREDEFINED_EMPLOYERS = {
    "yandex": "1740",  # Яндекс
    "sber": "3529",  # Сбер
    "tinkoff": "78638",  # Тинькофф
    "vk": "41862",  # VK
    "alfa": "80",  # Альфа-Банк
    "mts": "15478",  # МТС
    "megafon": "3776",  # МегаФон
    "ozon": "907345",  # Ozon
    "kaspersky": "2180",  # Лаборатория Касперского
    "sbertech": "87021",  # СберТех
}


def load_employers_from_file(filename: str = "employers.txt") -> list:
    """Загружает ID компаний из текстового файла с поддержкой UTF-8"""
    try:
        with open(filename, "r", encoding="utf-8") as f:
            employer_ids = []
            for line in f:
                line = line.strip()
                # Пропускаем пустые строки и комментарии
                if not line or line.startswith("#"):
                    continue
                # Извлекаем ID из строки (разделитель - пробел или табуляция)
                parts = line.split()
                if parts:
                    employer_ids.append(parts[0])
            return employer_ids
    except FileNotFoundError:
        print(f"Файл {filename} не найден. Используются стандартные компании.")
        return list(PREDEFINED_EMPLOYERS.values())
    except UnicodeDecodeError:
        print(f"Ошибка декодирования файла {filename}. Пожалуйста, убедитесь, что файл в кодировке UTF-8.")
        return list(PREDEFINED_EMPLOYERS.values())


def main():
    # Инициализация БД
    db_name = "career_db"
    initialize_database(db_name)
    processor = DataProcessor(db_name)

    print("=== Загрузка данных ===")
    print("1. Использовать предопределенные ID компаний")
    print("2. Загрузить ID из файла")
    print("3. Ввести названия компаний вручную")

    choice = input("Выберите вариант загрузки: ").strip()

    if choice == "1":
        employer_ids = list(PREDEFINED_EMPLOYERS.values())
        print(f"Загружено {len(employer_ids)} предопределенных компаний")
        processor.load_by_ids(employer_ids)

    elif choice == "2":
        filename = input("Введите имя файла (по умолчанию employers.txt): ").strip() or "employers.txt"
        employer_ids = load_employers_from_file(filename)
        print(f"Загружено {len(employer_ids)} компаний из файла")
        processor.load_by_ids(employer_ids)

    elif choice == "3":
        names_input = input("Введите названия компаний через запятую: ").strip()
        if not names_input:
            print("Не введены названия компаний!")
            return
        company_names = [name.strip() for name in names_input.split(",")]
        print(f"Поиск данных для {len(company_names)} компаний...")
        processor.load_by_names(company_names)

    else:
        print("Неверный выбор!")
        return

    # Запуск пользовательского интерфейса
    ui = CareerConsoleUI(db_name)
    ui.show_menu()


if __name__ == "__main__":
    main()
