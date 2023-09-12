from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

SQUARES_PER_COLUMN = 25
url = "https://easyacademy.unitn.it/AgendaStudentiUnitn/index.php?view=easycourse&form-type=corso&include=corso&txtcurr=1+-+Scienze+e+Tecnologie+Informatiche&anno=2023&corso=0514G&anno2%5B%5D=P0405%7C1&date=12-09-2023&periodo_didattico=&_lang=it&list=&week_grid_type=-1&ar_codes_=&ar_select_=&col_cells=0&empty_box=0&only_grid=0&highlighted_date=0&all_events=0&faculty_group=0#"

calculusInEnglish = programmingInEnglish = geometryInEnglish = group2 = False

calculusNames = ["Analisi Matematica 1", "Calculus 1"]
geometryNames = ["Geometria e algebra lineare", "Geometry and Linear Algebra"]
programmingNames = ["Programmazione 1 - LEZ", "Computer Programming 1 - LEZ"]
labNames = [["Programmazione 1 - LAB (gruppo 1)", "Programmazione 1 - LAB (gruppo 2)"], 
            ["Computer Programming 1 - LAB (gruppo1)", "Computer Programming 1 - LAB (gruppo2)"]]
# labNames[programmingInEnglish][group2]
# es. labNames[0][1] -> italiano e gruppo





def main():
    htmlContent = loadHTMLContent(url)
    lessonsPerDay = getNumberOfLessonsPerDay(htmlContent)
    lessonData = getBoxesLessonData(htmlContent)
    
    for i in range(5):  # from monday to friday
        print("Day of week: ", (i+1))
        for j in range(lessonsPerDay[i]):
            boxInfo = boxToDict(lessonData[i*j + j])
            name, prof, room, start, end = boxInfo.values()
            print(name)



def boxToDict(box):
    d = {}
    soup = BeautifulSoup(str(box), 'html.parser')
    ps = soup.find_all('p')
    absentProfName = len(ps) != 4
    
    d["course_name"] = ps[0].text
    d["prof_name"] =  "No prof" if absentProfName else ps[1].text
    d["room_name"] = ps[2 - absentProfName].text
    d["start"] = ps[3 - absentProfName].text[:5]
    d["end"] = ps[3 - absentProfName].text[8:13]
    
    return d

def getTableClasses(htmlContent):
    soup = BeautifulSoup(str(htmlContent), 'html.parser')
    return soup.find_all('div', class_='rTableClass')

def getBoxesLessonData(htmlContent):
    soup = BeautifulSoup(str(htmlContent), 'html.parser')
    return soup.find_all('div', class_='rClassContent')

def getCellsContent(boxContent):
    soup = BeautifulSoup(boxContent, 'html.parser')
    return soup.find_all('div', class_='rTableCell')

def getNumberOfLessonsPerDay(htmlContent):
    numberOfLessonsPerDay = [0] * 5
    tableClass = getTableClasses(htmlContent)
    for cl in tableClass:
        s = str(cl)
        day = s.find("day-")
        dayIdx = int(s[day+4])
        numberOfLessonsPerDay[dayIdx - 1] += 1
    return numberOfLessonsPerDay

def loadHTMLContent(url):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)

    driver.get(url)

    # Wait for an element with a specific class to become present
    wait = WebDriverWait(driver, 10)
    element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'rClassContent')))
    htmlContent = driver.page_source

    driver.quit()
    return htmlContent


if __name__ == "__main__":
    main()

