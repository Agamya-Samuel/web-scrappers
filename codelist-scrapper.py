from time import sleep
from datetime import datetime, timedelta
import dateutil.parser

import requests

import glob
import json
import csv

from bs4 import BeautifulSoup


sleepDuration = 1 # duration in seconds.


def fetchPageData(firstPageNum:int, lastPageNum:int) -> None:
    lastPostUrl = getLastPostURLFromJsonFile()
    finalList = []
    myCustmHeader = {
        'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'
    }
    for pageNum in range(firstPageNum, lastPageNum+1):
        linksOfPostOnCurrentPage = []
        baseUrl = f'https://www.codelist.cc/pag/{pageNum}/'
        print(f'------------------------------------------------')
        print(f'Extracting Posts from Page-{pageNum} (Newest-To-Oldest)')
        print(f'Page-{pageNum} Link: {baseUrl}')
        req = requests.get(baseUrl, headers=myCustmHeader)
        bSoup = BeautifulSoup(req.content, 'html.parser')
        postsList = bSoup.find_all('div', class_='news-title')
        for post in postsList:
            for postLink in post.find_all('a', href=True):
                linksOfPostOnCurrentPage.append(postLink['href'])
        responseList, shouldScrappingContinue = fetchPostData(linksOfPostOnCurrentPage=linksOfPostOnCurrentPage, lastPostUrl=lastPostUrl)
        for post in responseList:
            finalList.append(post)
        if shouldScrappingContinue:
            pass
        else:
            print(f'Skipped Page-{pageNum} and pages that lies ahead of it.')
            break
    if len(finalList) != 0:
        writeToCSVFile(postsList=finalList)


def fetchPostData(linksOfPostOnCurrentPage:list, lastPostUrl:str):
    myCustmHeader = {
        'User-Agent' : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36"
    }
    finalList = []
    shouldScrappingContinue = True
    for indvPostLink in linksOfPostOnCurrentPage:
        if indvPostLink == lastPostUrl:
            print(f'This Post is already saved in the last jsonFile: {indvPostLink}\nExiting fetchPostData() ;-(')
            shouldScrappingContinue = False
            break
        else:
            req = requests.get(indvPostLink, headers=myCustmHeader)
            bSoup = BeautifulSoup(req.content, 'html.parser')
            postDate = bSoup.find('div', class_="full").find('div', class_="categfull").text.split()[3:6]
            postDate[1] = postDate[1].replace(",", "")
            fdate = (postDate[1] + "-" + postDate[0] + "-" + postDate[2])
            if "today" in fdate.casefold():
                today = datetime.now()
                fdate = today.strftime('%d-%m-%Y')
            elif "yesterday" in fdate.casefold():
                today = datetime.today()
                yesterdayDate = today - timedelta(days = 1)
                fdate = yesterdayDate.strftime('%d-%m-%Y')
            fdate = dateutil.parser.parse(fdate).strftime("%d-%m-%Y")
            title = bSoup.find('div', class_="full").find('h1').text.strip()
            demo = bSoup.find('div', class_="full").find('div', class_="full-news none").find('a', href=True).text
            if demo == "\n\n":
                demo = None
            urls = str(bSoup.find('div', class_="full").
                find('div', class_="full-news none").
                find('div', class_="quote")).replace('<div class="quote"><!--QuoteEBegin-->', "").split("<br/>")[:-1]
            furls = ""
            for index,url in enumerate(urls):
                if index == 0:
                    furls = furls+url
                else:
                    furls = furls+"~"+url
            description = str(bSoup.find('div', class_="full").find('div', class_="full-news none")).split("<br/>")[2].strip('\n')
            indvItemDict = {
                'date': fdate,
                'title': title,
                'details': indvPostLink,
                'demo': demo,
                'urls': furls,
                'description': description
            }
            finalList.append(indvItemDict)
            print(f'Extracted: {indvItemDict["title"]}')
            sleep(sleepDuration)
    return finalList, shouldScrappingContinue


def getLastPostURLFromJsonFile() -> str:
    try:
        filesList = glob.glob('*.json')
        filesList.reverse()
        for fileName in filesList:
            if fileName.startswith('codelist'):
                lastJSONFilePath = fileName
                break
        with open(lastJSONFilePath, 'r', encoding='UTF-8') as jsonFile:
            jsonContent = json.load(jsonFile)
            lastPost = jsonContent[0]
            lastPostUrl = lastPost['details']
            print(f'Last Post-URL saved in JSON File is:\n{lastPostUrl}')
            return lastPostUrl
    except UnboundLocalError:
        print(f'No json file found.')
        return None


def writeToCSVFile(postsList:list) -> None:
    filesList = glob.glob('*.csv')
    if len(filesList) != 0:
        lastFileName = filesList[len(filesList)-1]
        lastFileNameIndex = int(lastFileName[-7:-4])
        nextFileName = f"codelist-scrapper-{str(lastFileNameIndex+1).zfill(3)}.csv"
    else:
        lastFileNameIndex = 0 # meaning -> no Files in the Directory
        nextFileName = f"codelist-scrapper-001.csv"
    with open(nextFileName, 'w', encoding='UTF-8') as csvFile:
        csvWriter = csv.writer(csvFile)
        count = 0
        for post in postsList:
            if count == 0:
                columnHeadings = post.keys()
                capitalizeRowHeading = []
                for clmns in columnHeadings: 
                    capitalizeRowHeading.append(clmns.capitalize())
                csvWriter.writerow(capitalizeRowHeading)
                count += 1
            csvWriter.writerow(post.values())
    writeToJSONFile(postsList=postsList, lastFileNameIndex=lastFileNameIndex)


def writeToJSONFile(postsList:list, lastFileNameIndex:int) -> None:
    if lastFileNameIndex != 0:
        nextJsonFileName = f'codelist-scrapper-{str(lastFileNameIndex+1).zfill(3)}.json'
    else:
        nextJsonFileName = f'codelist-scrapper-001.json'
    with open(nextJsonFileName, 'w', encoding='UTF-8') as jsonFile:
        json.dump(postsList, jsonFile, indent=4)


def getLastPageNumber() -> int:
    myCustmHeader = {
        'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'
    }
    baseUrl = f'https://www.codelist.cc/'
    req = requests.get(baseUrl, headers=myCustmHeader)
    bSoup = BeautifulSoup(req.content, 'html.parser')
    x = bSoup.find('div', style='text-align:center').find_all('a', href=True)
    lastPageNum = int(x[len(x)-2].text.strip())
    return lastPageNum


def takeSecondaryInput() -> int:
    firstPageNum = input('Enter First Page Number. Or Press Enter for default value -> 1\nfirstPageNum> ')
    lastPageNum = input('Enter Last Page Number. Or Press Enter for default value -> 1\nlastPageNum> ')
    return firstPageNum, lastPageNum


def takeMainInput():
    lastPageNumber = getLastPageNumber()
    displyMsg = f'Enter "a" to Extract Data from all ({lastPageNumber} Pages OR {lastPageNumber*12} Posts)\n'\
                f'Enter "s" to Extract Data from a Range of Selected Pages.\n'\
                f'Enter "x" To Exit.\n'\
                f'Response> '
    inpt = input(displyMsg)
    if inpt.casefold() == 'a':
        print(f'Extracting data from all ({lastPageNumber*12} Posts):')
        print(f'------------------------------------------------')
        fetchPageData(firstPageNum=1, lastPageNum=lastPageNumber)
    elif inpt.casefold() == 's':
        firstPageNum, lastPageNum = takeSecondaryInput()
        try:
            fetchPageData(int(firstPageNum), int(lastPageNum))
        except ValueError:
            fetchPageData(firstPageNum=1, lastPageNum=1)
    elif inpt.casefold() == 'x':
        print(f'Exiting...')
        return
    else:
        print(f'You sure you Entered the correct Input ?')


def welcomeUser()-> None:
    welcomeMsg = f'''
 _    _      _                            _          _____           _      _     _     _               _____                                      
| |  | |    | |                          | |        /  __ \         | |    | |   (_)   | |             /  ___|                                     
| |  | | ___| | ___ ___  _ __ ___   ___  | |_ ___   | /  \/ ___   __| | ___| |    _ ___| |_   ___ ___  \ `--.  ___ _ __ __ _ _ __  _ __   ___ _ __ 
| |/\| |/ _ \ |/ __/ _ \| '_ ` _ \ / _ \ | __/ _ \  | |    / _ \ / _` |/ _ \ |   | / __| __| / __/ __|  `--. \/ __| '__/ _` | '_ \| '_ \ / _ \ '__|
\  /\  /  __/ | (_| (_) | | | | | |  __/ | || (_) | | \__/\ (_) | (_| |  __/ |___| \__ \ |_ | (_| (__  /\__/ / (__| | | (_| | |_) | |_) |  __/ |   
 \/  \/ \___|_|\___\___/|_| |_| |_|\___|  \__\___/   \____/\___/ \__,_|\___\_____/_|___/\__(_)___\___| \____/ \___|_|  \__,_| .__/| .__/ \___|_|   
                                                                                                                            | |   | |              
                                                                                                                            |_|   |_|    © 2022           
                '''
    print(welcomeMsg)


def main() -> None:
    welcomeUser()
    takeMainInput()


if __name__ == '__main__':
    main()