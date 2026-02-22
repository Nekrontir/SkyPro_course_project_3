from typing import Any, List, Tuple

import psycopg2

from src.config import DB_HOST, DB_NAME, DB_PASSWORD, DB_PORT, DB_USER


class DBManager:
    """Класс для управления данными в БД."""

    def __init__(self):
        """Инициализация параметров подключения."""
        self.conn_params = {
            "host": DB_HOST,
            "port": DB_PORT,
            "database": DB_NAME,
            "user": DB_USER,
            "password": DB_PASSWORD,
        }

    def _execute_query(self, query: str, params: tuple = ()) -> List[Tuple[Any, ...]]:
        """Выполнить SQL-запрос и вернуть результат."""
        conn = None
        try:
            conn = psycopg2.connect(**self.conn_params)
            with conn.cursor() as cur:
                cur.execute(query, params)
                result = cur.fetchall()
            return result
        except Exception as e:
            print(f"Ошибка выполнения запроса: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def get_companies_and_vacancies_count(self) -> List[Tuple[str, int]]:
        """Получает список всех компаний и количество вакансий у каждой."""
        query = """
            SELECT e.name, COUNT(v.vacancy_id) AS vacancies_count
            FROM employers e
            LEFT JOIN vacancies v ON e.employer_id = v.employer_id
            GROUP BY e.employer_id, e.name
            ORDER BY vacancies_count DESC
        """
        return self._execute_query(query)

    def get_all_vacancies(self) -> List[Tuple[str, str, str, str]]:
        """
        Получает список всех вакансий с указанием названия компании,
        названия вакансии, зарплаты и ссылки на вакансию.
        """
        query = """
            SELECT
                e.name AS company_name,
                v.name AS vacancy_name,
                CASE
                    WHEN v.salary_from IS NOT NULL THEN CONCAT('от ', v.salary_from)
                    ELSE 'не указана'
                END AS salary,
                v.url
            FROM vacancies v
            JOIN employers e ON v.employer_id = e.employer_id
            ORDER BY e.name, v.name
        """
        return self._execute_query(query)

    def get_avg_salary(self) -> float:
        """Получает среднюю зарплату по вакансиям (учитываются только salary_from)."""
        query = """
            SELECT AVG(salary_from)::numeric(10,2)
            FROM vacancies
            WHERE salary_from IS NOT NULL
        """
        result = self._execute_query(query)
        if result and result[0][0]:
            return float(result[0][0])
        return 0.0

    def get_vacancies_with_higher_salary(self) -> List[Tuple[str, str, str, str]]:
        """Получает список всех вакансий, у которых зарплата выше средней."""
        avg_salary = self.get_avg_salary()
        if avg_salary == 0:
            return []
        query = """
            SELECT
                e.name AS company_name,
                v.name AS vacancy_name,
                CONCAT('от ', v.salary_from) AS salary,
                v.url
            FROM vacancies v
            JOIN employers e ON v.employer_id = e.employer_id
            WHERE v.salary_from > %s
            ORDER BY v.salary_from DESC
        """
        return self._execute_query(query, (avg_salary,))

    def get_vacancies_with_keyword(self, keyword: str) -> List[Tuple[str, str, str, str]]:
        """Получает список всех вакансий, в названии которых содержится keyword."""
        query = """
            SELECT
                e.name AS company_name,
                v.name AS vacancy_name,
                CASE
                    WHEN v.salary_from IS NOT NULL THEN CONCAT('от ', v.salary_from)
                    ELSE 'не указана'
                END AS salary,
                v.url
            FROM vacancies v
            JOIN employers e ON v.employer_id = e.employer_id
            WHERE v.name ILIKE %s
            ORDER BY e.name, v.name
        """
        pattern = f"%{keyword}%"
        return self._execute_query(query, (pattern,))
