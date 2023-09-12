from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

SQUARES_PER_COLUMN = 25
url = "https://easyacademy.unitn.it/AgendaStudentiUnitn/index.php?view=easycourse&form-type=corso&include=corso&txtcurr=1+-+Scienze+e+Tecnologie+Informatiche&anno=2023&corso=0514G&anno2%5B%5D=P0405%7C1&date=12-09-2023&periodo_didattico=&_lang=it&list=&week_grid_type=-1&ar_codes_=&ar_select_=&col_cells=0&empty_box=0&only_grid=0&highlighted_date=0&all_events=0&faculty_group=0#"

calculusInEnglish = programmingInEnglish = geometryInEnglish = group2 = False

calculusNames = ["Analisi matematica 1", "Calculus 1"]
geometryNames = ["Geometria e algebra lineare", "Geometry and Linear Algebra"]
programmingNames = ["Programmazione 1 - LEZ", "Computer Programming 1 - LEZ"]
labNames = [["Programmazione 1 - LAB (gruppo 1)", "Programmazione 1 - LAB (gruppo 2)"], 
            ["Computer Programming 1 - LAB", "Computer Programming 1 - LAB"]]
# labNames[programmingInEnglish][group2]
# es. labNames[0][1] -> italiano e gruppo

validNames = []





def main():
    getUserChoices()
    addValidNames()
    
    
    htmlContent = loadHTMLContent(url)
    lessonsPerDay = getNumberOfLessonsPerDay(htmlContent)
    lessonData = getBoxesLessonData(htmlContent)
    
    dayNames = ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì"]
    
    idx = 0
    for i in range(5):  # from monday to friday
        print(f"\n{dayNames[i]}: ")
        for j in range(lessonsPerDay[i]):  # for each lesson of that day
            boxInfo = boxToDict(lessonData[idx])
            if boxInfo is not None:
                name, prof, room, start, end = boxInfo.values()
                print(name, start, end)
            idx += 1



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
    
    return d if userFollowsCourse(d) else None

def userFollowsCourse(d):
    return d["course_name"] in validNames

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

def addValidNames():
    global validNames
    
    validNames.append(calculusNames[calculusInEnglish])
    validNames.append(geometryNames[geometryInEnglish])
    validNames.append(programmingNames[programmingInEnglish])
    validNames.append(labNames[programmingInEnglish][group2])

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

def getUserChoices():
    global calculusInEnglish, programmingInEnglish, geometryInEnglish, group2
    
    calculusInEnglish = input("Do you want to follow Calculus 1 in English? (y/n) ") == "y"
    geometryInEnglish = input("Do you want to follow Geometry and Linear Algebra in English? (y/n) ") == "y"
    programmingInEnglish = input("Do you want to follow Programming 1 in English? (y/n) ") == "y"
    group2 = input("Are you in the second group of the Programming 1 Lab? (or if you follow the lab lessons in english) (y/n) ") == "y"


if __name__ == "__main__":
    main()

