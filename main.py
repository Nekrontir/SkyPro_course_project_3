from src.utils import load_data_to_db, print_vacancies
from src.db_manager import DBManager

def main():
    """Основная функция взаимодействия с пользователем."""
    db_manager = DBManager()

    while True:
        print("\n--- Меню ---")
        print("1. Загрузить данные о компаниях и вакансиях в БД")
        print("2. Список всех компаний и количество вакансий")
        print("3. Список всех вакансий")
        print("4. Средняя зарплата по вакансиям")
        print("5. Вакансии с зарплатой выше средней")
        print("6. Поиск вакансий по ключевому слову")
        print("0. Выход")

        choice = input("Выберите пункт: ").strip()

        if choice == '1':
            load_data_to_db()
        elif choice == '2':
            companies = db_manager.get_companies_and_vacancies_count()
            if companies:
                for name, count in companies:
                    print(f"{name}: {count} вакансий")
            else:
                print("Нет данных.")
        elif choice == '3':
            vacancies = db_manager.get_all_vacancies()
            print_vacancies(vacancies)
        elif choice == '4':
            avg = db_manager.get_avg_salary()
            print(f"Средняя зарплата (по полю 'от'): {avg:.2f}")
        elif choice == '5':
            vacancies = db_manager.get_vacancies_with_higher_salary()
            if vacancies:
                print("Вакансии с зарплатой выше средней:")
                print_vacancies(vacancies)
            else:
                print("Нет вакансий с зарплатой выше средней (или данные отсутствуют).")
        elif choice == '6':
            keyword = input("Введите ключевое слово для поиска: ").strip()
            if keyword:
                vacancies = db_manager.get_vacancies_with_keyword(keyword)
                if vacancies:
                    print(f"Вакансии, содержащие '{keyword}':")
                    print_vacancies(vacancies)
                else:
                    print("Ничего не найдено.")
        elif choice == '0':
            print("Выход из программы.")
            break
        else:
            print("Неверный ввод, попробуйте снова.")


if __name__ == "__main__":
    main()