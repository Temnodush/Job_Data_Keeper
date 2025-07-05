class Vacancy:
    """Класс для представления вакансии"""

    __slots__ = ["id", "title", "employer_id", "min_salary", "max_salary", "currency", "url", "description"]

    def __init__(
        self,
        position_id: str,
        title: str,
        employer_id: str,
        min_salary: int = None,
        max_salary: int = None,
        currency: str = None,
        url: str = None,
        description: str = None,
    ):
        self.id = position_id
        self.title = title
        self.employer_id = employer_id
        self.min_salary = min_salary
        self.max_salary = max_salary
        self.currency = currency
        self.url = url
        self.description = description

    def get_avg_salary(self) -> float:
        """Рассчитывает среднюю зарплату"""
        if self.min_salary and self.max_salary:
            return (self.min_salary + self.max_salary) / 2
        return self.min_salary or self.max_salary or 0

    @classmethod
    def from_api_response(cls, data: dict) -> "Vacancy":
        """Создаёт объект из данных API"""
        salary = data.get("salary") or {}
        snippet = data.get("snippet") or {}

        return cls(
            position_id=data.get("id", ""),
            title=data.get("name", "Без названия"),
            employer_id=data.get("employer", {}).get("id", ""),
            min_salary=salary.get("from"),
            max_salary=salary.get("to"),
            currency=salary.get("currency"),
            url=data.get("alternate_url", ""),
            description=snippet.get("requirement", "") or snippet.get("responsibility", ""),
        )
