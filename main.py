import pickle
import time

from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

from xls_handler import parse


def get_cookies(driver, vendor_code):
    """Получает куки от сайта и устанавливает их в драйвер"""
    driver.get(url + vendor_code)
    driver.implicitly_wait(5)

    # Одобряем куки
    driver.find_element(By.XPATH, '/html/body/div[8]/div/div[2]/button/span').click()

    # Нажимаем на ссылку, чтобы узнать о наличии
    link = driver.find_element(By.CLASS_NAME, 'range-revamp-stockcheck__available-for-delivery-link')
    actions = ActionChains(driver)
    actions.move_to_element(link).perform()
    link.click()
    driver.implicitly_wait(5)

    # Выбираем магазин
    driver.find_element(By.XPATH,
                        '/html/body/main/div/div[2]/div/div[4]/div/div[2]/div/div/div/div[4]/div[7]/div[2]/label/div/input').click()
    pickle.dump(driver.get_cookies(), open(f"cookies", "wb"))
    driver.implicitly_wait(5)

    # Одобряем выбор магазина
    driver.find_element(By.XPATH, '/html/body/main/div/div[2]/div/div[4]/div/div[3]/button/span').click()
    driver.implicitly_wait(5)


# options
options = webdriver.ChromeOptions()

# user-agent
options.add_argument("user-agent=Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:84.0) Gecko/20100101 Firefox/84.0")

# for ChromeDriver version 79.0.3945.16 or over
options.add_argument("--disable-blink-features=AutomationControlled")

options.add_argument("--no-sandbox")

# headless mode
# options.add_argument("--headless")
# options.headless = True


url = 'https://www.ikea.com/ru/ru/p/-'

service = Service('/home/hozyain/parser/sonya/chromedriver')
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

        return f"Поступление ожидается с {start_data}, до {final_data}"

    except Exception as e:
        return None


# def try_get_info_about_absence(driver):
#     """Проверяет отсутсвует ли товар, возвращает строку, иначе None"""
#     try:
#         driver.find_element(By.CLASS_NAME, 'range-revamp-indicator__no-wrap').click()
#         driver.implicitly_wait(3)
#
#         start_data = driver.find_element(
#             By.XPATH,
#             '/html/body/main/div/div[2]/div/div[4]/div/div[2]/div/div/div[3]/div/div[2]/p/span/span[1]'
#         ).text
#
#         final_data = driver.find_element(
#             By.XPATH,
#             '/html/body/main/div/div[2]/div/div[4]/div/div[2]/div/div/div[3]/div/div[2]/p/span/span[2]'
#         ).text
#
#         return f"Поступление ожидается с {start_data}, до {final_data}"
#
#     except Exception as e:
#         return None

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

    # Возвращаем данные о количестве товаров
    try:
        driver.find_element(By.CLASS_NAME, 'range-revamp-indicator__no-wrap').click()
        driver.implicitly_wait(3)
    except Exception as e:
        pass
    info = try_get_info_about_quantity(driver)
    if info:
        return info

    # Нажимаем на ссылку для отображения информации
    try:
        driver.find_element(
            By.XPATH,
            '/html/body/main/div/div/div/div[2]/div[3]/div/div[4]/div[2]/div[1]/span/div/span/a/span'
        ).click()
        driver.implicitly_wait(3)
    except Exception as e:
        return 'Нет в наличии во всех магазинах'


    # Возвращаем данные о сроках поставках, если они есть
    info = try_get_info_about_delivery_time(driver)
    if info:
        return info

    driver.find_element(By.CLASS_NAME, 'range-revamp-status--red')
    return 'Нет в наличии в Новосибирске'


def add_availability_information(driver, data_list):
    """Добавляет к каждой записи информацию о наличии"""
    number_of_records = len(data_list)
    # for i in range(0, number_of_records):
    for i in range(15, 25):
        if i == 0:
            data_list[i].append('Статус')
        else:
            info_about_availability = get_info_about_availability(driver, data_list[i][1])
            data_list[i].append(info_about_availability)

    # get_info_about_availability(driver)
    return data_list


if __name__ == '__main__':
    data_list = parse()

    try:
        get_cookies(driver, data_list[1][1])

        final_data_list = add_availability_information(driver, data_list)

        for i in range(15, 25):
            print(final_data_list[i])

    except Exception as ex:
        print(ex)
    finally:
        driver.close()
        driver.quit()
