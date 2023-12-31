import json
import os
import time
from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist
from selenium.common.exceptions import NoSuchElementException
import openpyxl
import selenium
from webdriver_manager.chrome import ChromeDriverManager
from openpyxl import Workbook
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementNotInteractableException

from parser.models import Questionnaire


def parse_vacancies():
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.append(['Название вакансии', 'Компания', 'Адрес', 'Опыт', 'контакты'])

    chrome_options = Options()
    driver = webdriver.Chrome(options=chrome_options)

    driver.get('https://spb.hh.ru/account/login?backurl=%2Femployer')
    time.sleep(40)
    # all_vacancies = []
    for page_number in range(1, 11):
        driver.get(f'https://spb.hh.ru/vacancies/sistemnyy_administrator?page={page_number}')
        buttons = driver.find_elements(By.CSS_SELECTOR, 'div.serp-item-controls')

        # time.sleep(30)
        for btn in buttons:
            # check = False
            time.sleep(1)
            if btn.text.startswith('Откликнуться\nПоказать контакты'):
                div = btn.find_element(By.XPATH, '..')
                vacancy_data = div.text.split('\n')
                button = btn.find_element(By.TAG_NAME, "button")

                if not button.is_displayed():
                    # Если элемент не видим, прокрутим страницу, чтобы сделать его видимым
                    driver.execute_script("arguments[0].scrollIntoView();", button)

                button.click()
                time.sleep(2)
                try:
                    try:
                        f_e = driver.find_element(By.CSS_SELECTOR, 'div.vacancy-contacts-call-tracking__phones')

                                                  # 'bloko-button bloko-button_kind-success bloko-button_scale-small bloko-button_collapsible bloko-button_appearance-outlined')
                        # contact_div = driver.find_element(By.CSS_SELECTOR, "div.vacancy-contacts_search")
                        # print(contact_div)
                        print(vacancy_data)
                        sheet.append([vacancy_data[0], vacancy_data[1], vacancy_data[2], vacancy_data[4], f_e.text])
                        print(f_e.text, vacancy_data, '58')
                    except NoSuchElementException:
                        f_e = driver.find_element(By.CSS_SELECTOR, 'div.bloko-drop')
                        sheet.append([vacancy_data[0], vacancy_data[1], vacancy_data[2], vacancy_data[4], f_e.text])
                        print(f_e.text, vacancy_data, '61')
                except NoSuchElementException:
                    print('63 строка')
                    f_e = None
    file_path = "company_who_search_sys_admin.xlsx"
    workbook.save(file_path)
    driver.quit()
    return workbook



def parse_sys_admin_who_work_in_real_time(vacancy, area_id, access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.append(['Название вакансии', 'ссылка на анкету', 'Название компании', 'Город'])
    for counter in range(100):

        params = {
            "text": vacancy,
            "area": area_id,  # Код региона для Санкт-Петербурга
            "employment": "full",  # Работает на данный момент
        }

        url = "https://api.hh.ru/resumes"

        response = requests.get(url, headers=headers, params=params)
        resume_list = response.json()

        try:
            for resume_dict in resume_list['items']:
                try:
                    if resume_dict['experience'][0]['end'] is None and resume_dict['title'] == vacancy or resume_dict['title'].lower() == vacancy.lower():
                        sheet.append([resume_dict['title'], resume_dict.get('alternate_url'), resume_dict['experience'][0]['company'], resume_dict['area']['name']])

                except IndexError as e:
                    print(e)
                    continue
            # counter += 1
        except KeyError as e:
            print(e)
            break
    file_path = "result_admin.xlsx"
    workbook.save(file_path)
    return workbook


def parse_vacancies_sys_admin(vacancy, area_id, access_token, page_number):
    url = "https://api.hh.ru/vacancies"

    params = {
        "text": "Системный администратор",
        "area": "2",  # Код региона для Санкт-Петербурга
        "page": page_number
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        vacancies = response.json()
        for vacancy in vacancies["items"]:
            print(vacancy["name"], vacancy['area']['name'], vacancy['alternate_url'], vacancy['contacts'])
            # print(vacancy, end='\n\n')
    else:
        print("Ошибка при запросе:", response.status_code)


