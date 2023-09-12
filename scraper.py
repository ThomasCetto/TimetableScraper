from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import requests


# Specify the path to the ChromeDriver executable
chromedriver_path = '/path/to/chromedriver'

options = webdriver.ChromeOptions()
options.add_argument("--headless")
driver = webdriver.Chrome(options=options)

url = "https://easyacademy.unitn.it/AgendaStudentiUnitn/index.php?view=easycourse&form-type=corso&include=corso&txtcurr=1+-+Scienze+e+Tecnologie+Informatiche&anno=2023&corso=0514G&anno2%5B%5D=P0405%7C1&date=12-09-2023&periodo_didattico=&_lang=it&list=&week_grid_type=-1&ar_codes_=&ar_select_=&col_cells=0&empty_box=0&only_grid=0&highlighted_date=0&all_events=0&faculty_group=0#"

driver.get(url)

# Wait for an element with a specific class to become present (you can customize the selector)
wait = WebDriverWait(driver, 10)
element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'rClassContent')))

# Get the page source after the element is present
html_content = driver.page_source

driver.quit()

soup = BeautifulSoup(html_content, 'html.parser')
classContents = soup.find_all('div', class_='rClassContent')

print(len(classContents))