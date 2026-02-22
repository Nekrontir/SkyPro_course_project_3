from src.api_hh import HeadHunterAPI
from src.config import COMPANY_IDS
from src.database import create_database, create_tables, insert_data


def load_data_to_db() -> None:
    """Загрузка данных с hh.ru и заполнение БД."""
    print("Начинаем загрузку данных с hh.ru...")
    hh_api = HeadHunterAPI()

    # Используем COMPANY_IDS из конфига
    employers = hh_api.get_employers(COMPANY_IDS)
    if not employers:
        print("Не удалось получить данные о работодателях.")
        return

    all_vacancies = {}
    for emp in employers:
        emp_id = emp["id"]
        print(f"Загружаем вакансии для {emp['name']}...")
        vacancies = hh_api.get_vacancies_by_employer(emp_id)
        all_vacancies[emp_id] = vacancies
        print(f"  Найдено {len(vacancies)} вакансий.")

    create_database()
    create_tables()
    insert_data(employers, all_vacancies)
    print("Загрузка завершена.")


def print_vacancies(vacancies_list: list) -> None:
    """Красивый вывод списка вакансий."""
    if not vacancies_list:
        print("Нет данных.")
        return
    for comp, name, salary, url in vacancies_list:
        print(f"Компания: {comp}")
        print(f"Вакансия: {name}")
        print(f"Зарплата: {salary}")
        print(f"Ссылка: {url}")
        print("-" * 40)
