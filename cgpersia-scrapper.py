from time import sleep
import dateutil.parser

import requests

import glob
import json
import csv

from bs4 import BeautifulSoup


sleepDuration = 1 # duration in seconds.


def getBeautifulSoup(link:str):
    myCustmHeader = {
        'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'
    }
    req = requests.get(link, headers=myCustmHeader)
    bSoup = BeautifulSoup(req.content, 'html.parser')
    return bSoup


def fetchPageData(firstPageNum, lastPageNum) -> None:
    lastPostUrl = getLastPostURLFromJsonFile()
    for pageNum in range(firstPageNum, lastPageNum+1):
        linksOfPostOnCurrentPage = []
        print(f'------------------------------------------------')
        print(f'Extracting Posts from Page-{pageNum} (Newest-To-Oldest)')
        if pageNum == 1:
            baseUrl = f'https://cgpersia.com/'
        else:
            baseUrl = f'https://cgpersia.com/page/{pageNum}/'
        print(f'Page-{pageNum} Link: {baseUrl}')
        bSoup = getBeautifulSoup(link=baseUrl)
        postsList = bSoup.find_all('article')
        for post in postsList:
            linksOfPost = post.find('a', href=True)['href']
            linksOfPostOnCurrentPage.append(linksOfPost)
        shouldScrappingContinue = fetchPostData(linksOfPostOnCurrentPage=linksOfPostOnCurrentPage, lastPostUrl=lastPostUrl)
        if shouldScrappingContinue:
            pass
        else:
            print(f'Skipped Page-{pageNum} and pages that lies ahead of it.')
            break

postCount = 0
def fetchPostData(linksOfPostOnCurrentPage:list, lastPostUrl:str):
    global postCount
    shouldScrappingContinue = True
    for indvPostLink in linksOfPostOnCurrentPage:
        if indvPostLink == lastPostUrl:
            print(f'This Post is already saved in the last jsonFile: {indvPostLink}\nExiting fetchPostData() ;-(')
            shouldScrappingContinue = False
            break
        else:
            bSoup = getBeautifulSoup(link=indvPostLink)
            if 'nothing found' in bSoup.text.casefold():
                continue
            else:
                # Fetches Post-Date
                postDateTxt = bSoup.find('div', class_='entry-byline').text.strip().split()
                postDate = postDateTxt[len(postDateTxt)-1]
                postDate = dateutil.parser.parse(postDate).strftime("%d-%m-%Y")

                # Fetches Title
                postTitleTxt = bSoup.find('h2', class_='entry-title')
                postTitle = postTitleTxt.text.replace('–', '-')
                
                # Fetches Post-Category
                postCategoryList = []
                postCategoryStr = ''
                postCategoryTxt = bSoup.find('div', class_='entry-meta')
                for index,postCategory in enumerate(postCategoryTxt.find_all('a', href=True)):
                    postCategory = postCategory.text
                    if 'comment' not in postCategory.casefold():
                        postCategoryList.append(postCategory)
                        if index == 0:
                            postCategoryStr = postCategoryStr + postCategory
                        else:
                            postCategoryStr = postCategoryStr + '~' + postCategory
                
                # Fetches Download Links
                rapidgatorLinks = []
                uploadedDotNetLinks = []
                oboomLinks = []
                xerverLinks = []
                nitroflareLinks = []
                alfafileDotNetLinks = []
                
                downloadLinks = bSoup.find_all('pre')
                if len(downloadLinks) != 0: # for Posts that are Recently added, that use <pre> Tag
                    for dlLink in downloadLinks:
                        for tempLinks in dlLink.text.split('\n'):
                            tempLinks = tempLinks.replace('\r', '')
                            if tempLinks != '':
                                if ('rg.to' in tempLinks) or ('rapidgator.net' in tempLinks):
                                    tempLinks = tempLinks.replace('rg.to', 'rapidgator.net')
                                    rapidgatorLinks.append(tempLinks)
                                elif ('nitro.download' in tempLinks) or ('nitroflare.com' in tempLinks):
                                    tempLinks = tempLinks.replace('nitro.download', 'nitroflare.com')
                                    nitroflareLinks.append(tempLinks)
                                elif ('alfafile.net' in tempLinks):
                                    alfafileDotNetLinks.append(tempLinks)
                                elif ('ul.to' in tempLinks) or ('uploaded.net' in tempLinks):
                                    tempLinks = tempLinks.replace('ul.to', 'uploaded.net')
                                    uploadedDotNetLinks.append(tempLinks)


            # Also fetches Download Links, if the above one fails to do so
            downloadLinks = bSoup.find_all('p')
            if len(downloadLinks) != 0: # for older Posts, in the range of pageNum = 1800 and older, that use <p> Tag
                for dlLink in downloadLinks:
                    dlLink = dlLink.text.strip().casefold()
                    for link in dlLink.split('\n'):
                        if ('rapidgator.net' in link) or ('rg.to' in  link):
                            link = link.replace('rg.to', 'rapidgator.net')
                            rapidgatorLinks.append(link)
                        elif ('ul.to' in link) or ('uploaded.net' in link):
                            link = link.replace('ul.to', 'uploaded.net')
                            uploadedDotNetLinks.append(link)
                        elif ('oboom.com' in link):
                            oboomLinks.append(link)
                        elif ('xerver.co' in link):
                            xerverLinks.append(link)
                        elif ('nitroflare.com') in link or 'nitro.download' in link:
                            nitroflareLinks.append(link)

            # Combines urls from above into 1 massive string :)
            furl = ''
            tmpDownloadLinksList = rapidgatorLinks + uploadedDotNetLinks + oboomLinks + xerverLinks + nitroflareLinks + alfafileDotNetLinks
            for index,url in enumerate(tmpDownloadLinksList):
                if url != '' or url != ' ':
                    if index == 0:
                        furl = furl + url
                    else:
                        furl = furl + '~' + url

            # Dictionary-Dictionary time
            indvItemDict = {
                'date': postDate,
                'title': postTitle,
                'details': indvPostLink,
                'category': postCategoryStr,
                'urls': furl,
                'urlseperate': {
                    'rapidgatorLinks': rapidgatorLinks,
                    'uploadedDotNetLinks': uploadedDotNetLinks,
                    'oboomLinks': oboomLinks,
                    'xerverLinks': xerverLinks,
                    'nitroflareLinks': nitroflareLinks,
                    'alfafileDotNetLinks': alfafileDotNetLinks
                }
            }
            if postCount == 0:
                createEmptyListInsideNewJsonFile()
                writeToCSVFile(postDict=indvItemDict, csvAppend=False)
            else:
                writeToCSVFile(postDict=indvItemDict, csvAppend=True)
            print(f'Extracted and Saved: {indvItemDict["title"]}')
            postCount += 1
            sleep(sleepDuration)
    return shouldScrappingContinue
        

def createEmptyListInsideNewJsonFile() -> None:
    CSVFilesList = glob.glob('*.json')
    if len(CSVFilesList) != 0:
        lastFileName = CSVFilesList[len(CSVFilesList)-1]
        lastFileNameIndex = int(lastFileName[-8:-5])
        nextFileName = f'cgpersia-scrapper-{str(lastFileNameIndex+1).zfill(3)}.json'
    else:
        lastFileNameIndex = 0 # meaning -> no Files in the Directory
        nextFileName = f'cgpersia-scrapper-001.json'
    with open(nextFileName, 'w', encoding='UTF-8') as jsonFile:
        emptyList = []
        json.dump(emptyList, jsonFile)
    print(f'Created Empty List inside - {nextFileName}')


def getLastPostURLFromJsonFile() -> str:
    try:
        filesList = glob.glob('*.json')
        filesList.reverse()
        for fileName in filesList:
            if fileName.startswith('cgpersia'):
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


def writeToCSVFile(postDict:dict, csvAppend:bool) -> None:
    CSVFilesList = glob.glob('*.csv')
    if len(CSVFilesList) != 0:
        lastFileName = CSVFilesList[len(CSVFilesList)-1]
        lastFileNameIndex = int(lastFileName[-7:-4])
        nextFileName = f'cgpersia-scrapper-{str(lastFileNameIndex+1).zfill(3)}.csv'
    else:
        lastFileNameIndex = 0 # meaning -> no Files in the Directory
        nextFileName = f'cgpersia-scrapper-001.csv'
    if csvAppend:
        lastFileName = CSVFilesList[len(CSVFilesList)-1]
        lastFileNameIndex = int(lastFileName[-7:-4])
        nextFileName = f'cgpersia-scrapper-{str(lastFileNameIndex).zfill(3)}.csv'
    with open(nextFileName, 'a', encoding='UTF-8') as csvFile:
        csvWriter = csv.writer(csvFile)
        if csvAppend:
            pass
        else: # creates Column headings
            columnHeadings = postDict.keys()
            capitalizeRowHeading = []
            for clmns in columnHeadings: 
                capitalizeRowHeading.append(clmns.capitalize())
            csvWriter.writerow(capitalizeRowHeading)
        csvWriter.writerow(postDict.values())
    writeToJSONFile(postDict=postDict, lastFileNameIndex=lastFileNameIndex, csvAppend=csvAppend)


def writeToJSONFile(postDict:dict, lastFileNameIndex:int, csvAppend:bool) -> None:
    if lastFileNameIndex != 0:
        nextJsonFileName = f'cgpersia-scrapper-{str(lastFileNameIndex+1).zfill(3)}.json'
    else:
        nextJsonFileName = f'cgpersia-scrapper-001.json'
    if csvAppend:
        nextJsonFileName = f'cgpersia-scrapper-{str(lastFileNameIndex).zfill(3)}.json'
    with open(nextJsonFileName, 'r', encoding='UTF-8') as jsonFile:
        jsonObj = json.load(jsonFile)
    with open(nextJsonFileName, 'w', encoding='UTF-8') as jsonFile:
        jsonObjList = jsonObj.append(postDict)
        json.dump(jsonObj, jsonFile, indent=4)


def checkRapidgatorLink() -> bool:
    baseUrl = f'http://rg.to/file/c48c562c8f7cbcc7834426091cc5e299/TSPSCCSel.part2.rar.html'
    bSoup = getBeautifulSoup(link=baseUrl)
    pageNotFoundDiv = bSoup.find('div', class_='btm', style='text-align: center;')
    pageNotFoundText = (pageNotFoundDiv.text.strip().split('\n')[0].strip())
    if pageNotFoundText.casefold() == 'page not found':
        print(f'{baseUrl} - Dead Link')
        return False
    else:
        return True


def getLastPageNumber() -> int:
    baseUrl = f'https://cgpersia.com/'
    bSoup = getBeautifulSoup(link=baseUrl)
    x = bSoup.find('span', class_='pages')
    lastPageNum = int(x.text[9:].replace(",", "").strip())
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
 _    _      _                            _          _____ _____ ______             _                              _____                                      
| |  | |    | |                          | |        /  __ \  __ \| ___ \           (_)                            /  ___|                                     
| |  | | ___| | ___ ___  _ __ ___   ___  | |_ ___   | /  \/ |  \/| |_/ /__ _ __ ___ _  __ _   ___ ___  _ __ ___   \ `--.  ___ _ __ __ _ _ __  _ __   ___ _ __ 
| |/\| |/ _ \ |/ __/ _ \| '_ ` _ \ / _ \ | __/ _ \  | |   | | __ |  __/ _ \ '__/ __| |/ _` | / __/ _ \| '_ ` _ \   `--. \/ __| '__/ _` | '_ \| '_ \ / _ \ '__|
\  /\  /  __/ | (_| (_) | | | | | |  __/ | || (_) | | \__/\ |_\ \| | |  __/ |  \__ \ | (_| || (_| (_) | | | | | | /\__/ / (__| | | (_| | |_) | |_) |  __/ |   
 \/  \/ \___|_|\___\___/|_| |_| |_|\___|  \__\___/   \____/\____/\_|  \___|_|  |___/_|\__,_(_)___\___/|_| |_| |_| \____/ \___|_|  \__,_| .__/| .__/ \___|_|   
                                                                                                                                       | |   | |              
                                                                                                                                       |_|   |_|    © 2022           
                '''
    print(welcomeMsg)


def main() -> None:
    welcomeUser()
    takeMainInput()


if __name__ == '__main__':
    main()