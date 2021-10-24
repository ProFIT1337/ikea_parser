import os
import pickle
from datetime import datetime

from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

from xls_handler import parse, save_data_to_file


def get_cookies(driver, vendor_code):
    """Получает куки от сайта и устанавливает их в драйвер"""
    driver.get(url + vendor_code)
    driver.implicitly_wait(3)

    # Одобряем куки
    driver.find_element(By.XPATH, '/html/body/div[8]/div/div[2]/button/span').click()

    # Нажимаем на ссылку, чтобы узнать о наличии
    link = driver.find_element(By.CLASS_NAME, 'range-revamp-stockcheck__available-for-delivery-link')
    actions = ActionChains(driver)
    actions.move_to_element(link).perform()
    link.click()
    driver.implicitly_wait(3)

    # Выбираем магазин
    driver.find_element(By.XPATH,
                        '/html/body/main/div/div[2]/div/div[4]/div/div[2]/div/div/div/div[4]/div[7]/div[2]/label/div/input'
                        ).click()
    pickle.dump(driver.get_cookies(), open(f"cookies", "wb"))
    driver.implicitly_wait(3)

    # Одобряем выбор магазина
    driver.find_element(By.XPATH, '/html/body/main/div/div[2]/div/div[4]/div/div[3]/button/span').click()
    driver.implicitly_wait(3)


# options
options = webdriver.ChromeOptions()

# user-agent
options.add_argument("user-agent=Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:84.0) Gecko/20100101 Firefox/84.0")

# for ChromeDriver version 79.0.3945.16 or over
options.add_argument("--disable-blink-features=AutomationControlled")

options.add_argument("--no-sandbox")

# headless mode
options.headless = True

url = 'https://www.ikea.com/ru/ru/p/-'
driver_root = os.path.join(os.getcwd(), 'chromedriver')

service = Service(driver_root)
driver = webdriver.Chrome(
    service=service,
    options=options
)


def try_get_info_about_delivery_time(driver):
    """Проверяет есть ли данные о сроке поставки, возвращает сроки, иначе None"""
    try:
        start_data = driver.find_element(
            By.XPATH,
            '/html/body/main/div/div[2]/div/div[4]/div/div[2]/div/div/div[3]/div/div[2]/p/span/span[1]'
        ).text

        final_data = driver.find_element(
            By.XPATH,
            '/html/body/main/div/div[2]/div/div[4]/div/div[2]/div/div/div[3]/div/div[2]/p/span/span[2]'
        ).text

        return f"{start_data} - {final_data}"

    except Exception as e:
        return None


def try_get_info_about_quantity(driver):
    """Проверяет есть ли в наличии товар и возвращает количество, иначе None"""
    try:
        quantity = driver.find_element(
            By.XPATH,
            '/html/body/main/div/div[2]/div/div[4]/div/div[2]/div/div/div[3]/div/div[1]/div[2]/span/span/span[1]'
        ).text
        return f'В наличии {quantity}шт'
    except Exception as e:
        return None


def get_info_about_availability(driver, vendor_code):
    driver.get(url + vendor_code)
    if driver.current_url == 'https://www.ikea.com/ru/ru/cat/tovary-products/':
        return 'Error'
    try:
        # Возвращаем данные о количестве товаров
        driver.find_element(By.CLASS_NAME, 'range-revamp-indicator__no-wrap').click()
        info = try_get_info_about_quantity(driver)
        if info:
            return info

        # Возвращаем данные о сроках поставках, если они есть
        info = try_get_info_about_delivery_time(driver)
        if info:
            return info

        driver.find_element(By.CLASS_NAME, 'range-revamp-modal-body')
        return 'Нет в наличии' # Нет только в Новосибирске
    except Exception as e:
        return 'Нет в наличии' # Нет во всех магазинах


def add_availability_information(driver, data_list):
    """Добавляет к каждой записи информацию о наличии"""
    number_of_records = len(data_list)
    data_dict = {}

    for i in range(0, number_of_records):
        if i == 0:
            info_about_availability = 'Статус'
            data_list[i].append(info_about_availability)
        else:

            if data_dict.get(data_list[i][1]):
                info_about_availability = data_dict.get(data_list[i][1])
            else:
                info_about_availability = get_info_about_availability(driver, data_list[i][1])
                data_dict[data_list[i][1]] = info_about_availability

            data_list[i].append(info_about_availability)
        print(f'Выполняется {i}/{number_of_records - 1} |  {data_list[i][2]} - {info_about_availability}')

    return data_list


if __name__ == '__main__':

    start_time = datetime.now()

    data_list = parse()

    try:
        get_cookies(driver, data_list[1][1])

        final_data_list = add_availability_information(driver, data_list)

        save_data_to_file(final_data_list)

    except Exception as ex:
        print(ex)
    finally:
        driver.close()
        driver.quit()
        finish_time = datetime.now()
        print(f'Завершено за {finish_time - start_time}')
