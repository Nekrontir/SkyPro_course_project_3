import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from src.config import DB_HOST, DB_NAME, DB_PASSWORD, DB_PORT, DB_USER


def create_database() -> None:
    """Создание базы данных, если она не существует."""
    conn = None
    try:
        conn = psycopg2.connect(host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD, database="postgres")
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()

        cur.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s", (DB_NAME,))
        exists = cur.fetchone()
        if not exists:
            cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(DB_NAME)))
            print(f"База данных {DB_NAME} создана.")
        else:
            print(f"База данных {DB_NAME} уже существует.")

        cur.close()
    except Exception as e:
        print(f"Ошибка при создании БД: {e}")
    finally:
        if conn:
            conn.close()


def create_tables() -> None:
    """Создание таблиц employers и vacancies."""
    conn = None
    try:
        conn = psycopg2.connect(host=DB_HOST, port=DB_PORT, database=DB_NAME, user=DB_USER, password=DB_PASSWORD)
        conn.autocommit = True
        cur = conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS employers (
                employer_id INTEGER PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                url VARCHAR(255),
                open_vacancies INTEGER
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS vacancies (
                vacancy_id INTEGER PRIMARY KEY,
                employer_id INTEGER NOT NULL REFERENCES employers(employer_id) ON DELETE CASCADE,
                name VARCHAR(255) NOT NULL,
                salary_from INTEGER,
                salary_to INTEGER,
                salary_currency VARCHAR(3),
                url VARCHAR(255),
                published_at TIMESTAMP
            )
        """)

        print("Таблицы успешно созданы (или уже существовали).")
        cur.close()
    except Exception as e:
        print(f"Ошибка при создании таблиц: {e}")
    finally:
        if conn:
            conn.close()


def insert_data(employers_data: list, vacancies_data: dict) -> None:
    """
    Заполнение таблиц данными.
    employers_data: список словарей с данными компаний (как от API hh.ru).
    vacancies_data: словарь {employer_id: list[vacancy_dict]}.
    """
    conn = None
    try:
        conn = psycopg2.connect(host=DB_HOST, port=DB_PORT, database=DB_NAME, user=DB_USER, password=DB_PASSWORD)
        conn.autocommit = False
        cur = conn.cursor()

        # Вставка работодателей
        for emp in employers_data:
            cur.execute(
                """
                INSERT INTO employers (employer_id, name, url, open_vacancies)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (employer_id) DO UPDATE SET
                    name = EXCLUDED.name,
                    url = EXCLUDED.url,
                    open_vacancies = EXCLUDED.open_vacancies
            """,
                (emp["id"], emp["name"], emp.get("alternate_url"), emp.get("open_vacancies", 0)),
            )

        # Вставка вакансий
        for emp_id, vacancies in vacancies_data.items():
            for vac in vacancies:
                salary = vac.get("salary")
                salary_from = None
                salary_to = None
                salary_currency = None
                if salary:
                    salary_from = salary.get("from")
                    salary_to = salary.get("to")
                    salary_currency = salary.get("currency")

                published_at = vac.get("published_at")

                cur.execute(
                    """
                    INSERT INTO vacancies (
                        vacancy_id, employer_id, name, salary_from, salary_to,
                        salary_currency, url, published_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (vacancy_id) DO UPDATE SET
                        name = EXCLUDED.name,
                        salary_from = EXCLUDED.salary_from,
                        salary_to = EXCLUDED.salary_to,
                        salary_currency = EXCLUDED.salary_currency,
                        url = EXCLUDED.url,
                        published_at = EXCLUDED.published_at
                """,
                    (
                        vac["id"],
                        emp_id,
                        vac["name"],
                        salary_from,
                        salary_to,
                        salary_currency,
                        vac.get("alternate_url"),
                        published_at,
                    ),
                )

        conn.commit()
        print("Данные успешно загружены в БД.")
    except Exception as e:
        print(f"Ошибка при вставке данных: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()
