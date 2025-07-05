class Employer:
    """Класс для представления работодателя"""

    __slots__ = ["id", "name", "location", "website"]

    def __init__(self, employer_id: str, name: str, location: str = None, website: str = None):
        self.id = employer_id
        self.name = name
        self.location = location
        self.website = website

    def to_db_format(self) -> tuple:
        """Возвращает данные в формате для вставки в БД"""
        return (self.id, self.name, self.location, self.website)

    @classmethod
    def from_api_response(cls, data: dict) -> "Employer":
        """Создаёт объект из данных API"""
        return cls(
            employer_id=data.get("id", ""),
            name=data.get("name", ""),
            location=data.get("area", {}).get("name"),
            website=data.get("site_url") or data.get("alternate_url"),
        )
