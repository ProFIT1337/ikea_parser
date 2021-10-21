import pickle
import time

from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By



def get_cookies(driver):
    """Получает куки от сайта и устанавливает их в драйвер"""
    driver.get(url + '40482596')
    driver.implicitly_wait(5)

    #Одобряем куки
    driver.find_element(By.XPATH, '/html/body/div[8]/div/div[2]/button/span').click()

    #Нажимаем на ссылку, чтобы узнать о наличии
    link = driver.find_element(By.CLASS_NAME, 'range-revamp-stockcheck__available-for-delivery-link')
    actions = ActionChains(driver)
    actions.move_to_element(link).perform()
    link.click()
    driver.implicitly_wait(5)

    #Выбираем магазин
    driver.find_element(By.XPATH, '/html/body/main/div/div[2]/div/div[4]/div/div[2]/div/div/div/div[4]/div[7]/div[2]/label/div/input').click()
    pickle.dump(driver.get_cookies(), open(f"cookies", "wb"))
    driver.implicitly_wait(5)

    #Одобряем выбор магазина
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

service = Service('/home/hozyain/parser/sonya/chromedriver')
driver = webdriver.Chrome(
    service=service,
    options=options
)

url = 'https://www.ikea.com/ru/ru/p/-'

try:

    get_cookies(driver)
    driver.get(url + '90483881')
    time.sleep(5)



except Exception as ex:
    print(ex)
finally:
    driver.close()
    driver.quit()


if __name__ == '__main__':
    parse