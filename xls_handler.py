import pandas
import xlrd


def get_file_name():
    """Просит у пользователя указать имя или путь файла, возвращает полученное значение"""
    name = input('Введите название или путь к файлу (Оставьте поле пустым, для Zayavka.xls\n')
    if not name:
        name = 'Zayavka.xls'
    return name


def get_data_from_file(name):
    """Парсит xls файл и возвращает полученные данные"""
    workbook = xlrd.open_workbook(name, encoding_override='cp1251', formatting_info=True)
    data = pandas.read_excel(workbook)
    return data


def get_record(data, upper_indent, i):
    """Возвращает одну запись из data в виде списка"""
    return [
        i - upper_indent + 1,  # Порядковый номер
        data['Unnamed: 3'][i],  # Артикуль
        data['Unnamed: 6'][i],  # Товар
        data['Unnamed: 20'][i],  # Заказчик
        data['Unnamed: 23'][i],  # Количество
        data['Unnamed: 26'][i],  # Цена
        data['Unnamed: 30'][i],  # Сумма
    ]


def make_list_from_dataframe(data):
    """Парсит DataFrame данные, возвращает список из полученных записей"""
    # Отступ сверху
    upper_indent = 4
    # Отступ снизу
    bottom_indent = 1
    # Количество пустых строк
    rows_indent = upper_indent + bottom_indent
    # Количество строк
    rows_count = len(data[data.keys()[1]]) - rows_indent

    data_list = [['№', 'Артикул', 'Товар', 'Заказчик', 'К-во', 'Цена', 'Сумма']]

    for i in range(upper_indent, upper_indent + rows_count):
        record = get_record(data, upper_indent, i)
        data_list.append(record)

    return data_list


def parse():
    """Парсит указанный пользователем файл и возвращает список из записей"""
    name = get_file_name()
    data = get_data_from_file(name)
    data_list = make_list_from_dataframe(data)
    return data_list


def save_data_to_file(final_data_list):
    """Сохраняет полученные данные в файл result.xls"""
    data_df = pandas.DataFrame(final_data_list)
    data_df.to_excel('result.xls')


if __name__ == '__main__':
    parse()
