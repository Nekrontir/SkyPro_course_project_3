from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import requests


class HeadHunterAPIBase(ABC):
    """Абстрактный класс для работы с API сервиса с вакансиями."""

    def __init__(self) -> None:
        self.session = requests.Session()

    @abstractmethod
    def get_employers(self, employer_ids: List[int]) -> List[Dict[str, Any]]:
        """Получить информацию о работодателях по их ID."""
        pass

    @abstractmethod
    def get_vacancies_by_employer(self, employer_id: int) -> List[Dict[str, Any]]:
        """Получить вакансии конкретного работодателя."""
        pass

    def _request(self, url: str, params: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Выполнить HTTP-запрос."""
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Ошибка сети: {e}")
            return None
        except Exception as e:
            print(f"Ошибка обработки: {e}")
            return None


class HeadHunterAPI(HeadHunterAPIBase):
    """Класс для работы с API HeadHunter."""

    BASE_URL_EMPLOYERS = "https://api.hh.ru/employers"
    BASE_URL_VACANCIES = "https://api.hh.ru/vacancies"

    def get_employers(self, employer_ids: List[int]) -> List[Dict[str, Any]]:
        """Получить данные о работодателях по списку ID."""
        employers = []
        for emp_id in employer_ids:
            url = f"{self.BASE_URL_EMPLOYERS}/{emp_id}"
            data = self._request(url)
            if data:
                employers.append(data)
            else:
                print(f"Не удалось получить данные по работодателю {emp_id}")
        return employers

    def get_vacancies_by_employer(self, employer_id: int) -> List[Dict[str, Any]]:
        """Получить все вакансии работодателя (учитываем пагинацию)."""
        vacancies = []
        page = 0
        per_page = 100
        while True:
            params = {
                'employer_id': employer_id,
                'page': page,
                'per_page': per_page
            }
            data = self._request(self.BASE_URL_VACANCIES, params)
            if not data or 'items' not in data:
                break
            items = data['items']
            vacancies.extend(items)
            if page >= data.get('pages', 0) - 1:
                break
            page += 1
        return vacancies