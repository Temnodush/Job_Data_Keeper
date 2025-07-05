from configparser import ConfigParser
import os


def get_db_config(section: str = "postgresql") -> dict:
    """Возвращает конфигурацию базы данных с указанием кодировки"""
    config = ConfigParser()
    config_path = os.path.join(os.path.dirname(__file__), "..", "..", "database.ini")

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config.read_file(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Файл конфигурации не найден: {config_path}")
    except UnicodeDecodeError:
        # Попробуем альтернативные кодировки
        try:
            with open(config_path, "r", encoding="cp1251") as f:
                config.read_file(f)
        except Exception as e:
            raise Exception(f"Ошибка чтения файла конфигурации: {e}")

    if not config.has_section(section):
        raise ValueError(f"Секция {section} не найдена в файле конфигурации")

    return dict(config[section])


def get_api_config() -> dict:
    """Возвращает конфигурацию API"""
    return {
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
    }
