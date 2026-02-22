from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, cast

import requests


class HeadHunterAPIBase(ABC):
    """
    Абстрактный класс для работы с API сервиса с вакансиями.
    """

    def __init__(self) -> None:
        """Инициализация HTTP-сессии для запросов к API."""
        self.session = requests.Session()

    @abstractmethod
    def get_vacancies(self, query: str, **kwargs: Any) -> List[Dict[str, Any]]:
        """
        Абстрактный метод для получения вакансий по запросу.

        Args:
            query: Поисковый запрос
            **kwargs: Дополнительные параметры

        Returns:
            Список словарей с данными о вакансиях
        """
        pass

    def _request(self, endpoint: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Выполняет HTTP-запрос к API сервиса.

        Args:
            endpoint: URL endpoint API
            params: Параметры запроса

        Returns:
            Ответ API в виде словаря или None в случае ошибки
        """
        try:
            response = self.session.get(endpoint, params=params, timeout=10)
            response.raise_for_status()

            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict):
                    return cast(Dict[str, Any], data)
                return None
            return None

        except requests.exceptions.RequestException as e:
            print(f"Ошибка сети при запросе к {endpoint}: {e}")
            return None
        except Exception as e:
            print(f"Ошибка при обработке ответа: {e}")
            return None


class HeadHunterAPI(HeadHunterAPIBase):
    """
    Класс для работы с API HeadHunter.
    """

    BASE_URL = "https://api.hh.ru/vacancies"

    def __init__(self) -> None:
        """Инициализация API HH.ru."""
        super().__init__()

    def get_vacancies(self, query: str, **kwargs: Any) -> List[Dict[str, Any]]:
        """
        Получает вакансии с HH.ru по поисковому запросу.

        Args:
            query: Поисковый запрос
            **kwargs: Дополнительные параметры
                area: Код региона (по умолчанию 113 - Россия)
                per_page: Количество вакансий на странице
                pages: Количество страниц для загрузки

        Returns:
            Список словарей с данными о вакансиях
        """
        area: int = kwargs.get("area", 113)  # 113 - Россия
        per_page: int = kwargs.get("per_page", 100)  # Максимум 100

        params: Dict[str, Any] = {"text": query, "area": area, "per_page": per_page, "page": 0}

        all_vacancies: List[Dict[str, Any]] = []
        max_pages: int = kwargs.get("pages", 1)

        for page in range(max_pages):
            params["page"] = page
            data = self._request(self.BASE_URL, params)

            if not data:
                break

            items = data.get("items", [])
            all_vacancies.extend(items)

            pages = data.get("pages", 0)
            if page >= pages - 1:
                break

        return all_vacancies
