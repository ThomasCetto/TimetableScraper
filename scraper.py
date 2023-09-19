# TODO check if the ride is on train or bus, and also if it is a festivity




from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import tabula
import datetime
from datetime import date


url = "https://easyacademy.unitn.it/AgendaStudentiUnitn/index.php?view=easycourse&form-type=corso&include=corso&txtcurr=1+-+Scienze+e+Tecnologie+Informatiche&anno=2023&corso=0514G&anno2%5B%5D=P0405%7C1&date=12-09-2023&periodo_didattico=&_lang=it&list=&week_grid_type=-1&ar_codes_=&ar_select_=&col_cells=0&empty_box=0&only_grid=0&highlighted_date=0&all_events=0&faculty_group=0#"
trainTablePath = "TrainTable.pdf"
MINUTES_TOLERANCE = 15

calculusInEnglish = programmingInEnglish = geometryInEnglish = group2 = False

calculusNames = ["Analisi matematica 1", "Calculus 1"]
geometryNames = ["Geometria e algebra lineare", "Geometry and Linear Algebra"]
programmingNames = ["Programmazione 1 - LEZ", "Computer Programming 1 - LEZ"]
labNames = [["Programmazione 1 - LAB (gruppo 1)", "Programmazione 1 - LAB (gruppo 2)"], 
            ["Computer Programming 1 - LAB", "Computer Programming 1 - LAB"]]
# labNames[programmingInEnglish][group2]
# es. labNames[0][1] -> italiano e gruppo 2

validLessonNames = []
stationNames = ["Trento", "Trento S. Chiara", "Trento S. Bartolameo", "Villazzano", "Mesiano", "Pergine Valsugana", ""]
stationTimes = []


def main():

    today = date.today()
    split = str(today).split("-")
    today = f"{split[2]}-{split[1]}-{split[0]}"
    
    global url
    url = "https://easyacademy.unitn.it/AgendaStudentiUnitn/index.php?view=easycourse&form-type=corso&include=corso&txtcurr=1+-+Scienze+e+Tecnologie+Informatiche&anno=" + split[0] + "&corso=0514G&anno2%5B%5D=P0405%7C1&date=" + today + "&periodo_didattico=&_lang=it&list=&week_grid_type=-1&ar_codes_=&ar_select_=&col_cells=0&empty_box=0&only_grid=0&highlighted_date=0&all_events=0&faculty_group=0#"
    print(url)

    stationTimes = getStationsTimes("Mesiano", "Strigno")
    
    if(not getReferencesSaved()):
        print("There are no preferences saved yet")
        askForUserChoices()
        savePreferences()
    addValidLessonNames()
    
    print(f"Valid lessons: {validLessonNames}\n")
    
    
    dayOfWeek = datetime.date.today().weekday()
    if dayOfWeek >= 5:
        print("This program works only from Monday to Friday. Bye")
        return
    
    
    htmlContent = loadHTMLContent(url)
    lessonsPerDay = getNumberOfLessonsPerDay(htmlContent)
    lessonData = getBoxesLessonData(htmlContent)
    
    dayNames = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    
    lastLessonHour = 0
    lastLessonMinute = 0
    
    idx = 0
    for i in range(5):  # from monday to friday
        for j in range(lessonsPerDay[i]):  # for each lesson of that day
            boxInfo = boxToDict(lessonData[idx])
            idx += 1
            if boxInfo is not None:
                name, prof, room, start, end = boxInfo.values()
                
                if i == dayOfWeek:
                    lastLessonHour = int(end[:2])
                    lastLessonMinute = int(end[3:])
                    totalMinutes = lastLessonHour * 60 + lastLessonMinute
                    
    print(f"\nLast lesson ends at {lastLessonHour}:{lastLessonMinute}")


    # find the first train after the last lesson

    rightTrainTime = []
    for start, end in zip(stationTimes[0], stationTimes[1]):
        if start in ["-", ""]:
            continue 


        split = start.split(":")
        hour = int(split[0])
        minute = int(split[1])
        if totalMinutes - MINUTES_TOLERANCE < hour * 60 + minute:
            if end not in ["-", ""]:
                rightTrainTime.append(f"{hour}:{minute}")



    
    print(f"There are trains from Mesiano to Strigno at: {list(rightTrainTime)[:3]}")




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
    return d["course_name"] in validLessonNames

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

def addValidLessonNames():
    global validLessonNames
    
    validLessonNames.append(calculusNames[calculusInEnglish])
    validLessonNames.append(geometryNames[geometryInEnglish])
    validLessonNames.append(programmingNames[programmingInEnglish])
    validLessonNames.append(labNames[programmingInEnglish][group2])

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

def askForUserChoices():
    global calculusInEnglish, programmingInEnglish, geometryInEnglish, group2
    
    calculusInEnglish = input("Do you want to follow Calculus 1 in English? (y/n) ").lower() == "y"
    geometryInEnglish = input("Do you want to follow Geometry and Linear Algebra in English? (y/n) ").lower() == "y"
    programmingInEnglish = input("Do you want to follow Programming 1 in English? (y/n) ").lower() == "y"
    group2 = input("Are you in the second group of the Programming 1 Lab? (or if you follow the lab lessons in english) (y/n) ").lower() == "y"

def savePreferences():
    with open("user_preferences.txt", "w") as file:
        file.write(f"{int(calculusInEnglish)}\n{int(geometryInEnglish)}\n{int(programmingInEnglish)}\n{int(group2)}")

def getReferencesSaved():
    try:
        with open("user_preferences.txt", "r") as file:
            print("Preferences already saved, loading them...")

            global calculusInEnglish, programmingInEnglish, geometryInEnglish, group2

            calculusInEnglish = int(file.readline())
            geometryInEnglish = int(file.readline())
            programmingInEnglish = int(file.readline())
            group2 = int(file.readline())

            # all lines are written and no errors occurred
        return True
    except:
        print("Preferences not saved, will be asked to the user")
        return False
    

def loadCSV():
    import os
    if os.path.exists("TrainTable.csv"): 
        print("File of train timetable already exists, and it will not get loaded again")
        return
    
    tables = tabula.read_pdf(trainTablePath, pages='all')
    for i, table in enumerate(tables):
        if i == 1: # second table 
            table.to_csv(f'TrainTable.csv', index=False)

    
def getStationsTimes(stationName1, stationName2):
    loadCSV()
    times = []
    found1, found2 = False, False
    with open("TrainTable.csv", "r") as file:
        lines = file.readlines()
        for line in lines:
            if not found1 and stationName1 in line:
                split = line.split(",")
                times.append([x.replace("\n", "") for x in split if ":" in x or x in ["", "-"]])
            if not found2 and stationName2 in line:
                split = line.split(",")
                times.append([x.replace("\n", "") for x in split if ":" in x or x in ["", "-"]])
    
    return times
            
                
                
    
    
    
    
    
    
    
    
    
    

if __name__ == "__main__":
    main()

