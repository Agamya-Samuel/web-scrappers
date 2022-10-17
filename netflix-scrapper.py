import requests
import json
import glob

from bs4 import BeautifulSoup


def createEmptyListInJsonFile() -> None:
    respnse = getDataFromJsonFile()
    if respnse is None:
        with open('nf-ripper.json', 'w', encoding='UTF-8') as jsonFile:
            emptyList = []
            json.dump(emptyList, jsonFile)


def writeToJsonFile(inputDictnry:dict, jsonObj, jsonFileName:str) -> None:
    with open(jsonFileName, 'w', encoding='UTF-8') as jsonFile:
        jsonObjList = jsonObj.append(inputDictnry)
        json.dump(jsonObj, jsonFile, indent=4)
    

def getDataFromJsonFile() -> dict|str|None:
    jsonFilesList = glob.glob('nf-ripper.json')
    try:
        jsonFileName = jsonFilesList[0]
        with open(jsonFileName, 'r', encoding='UTF-8') as jsonFile:
            jsonObj = json.load(jsonFile)
            return jsonObj, jsonFileName
    except IndexError:
        return None # returns None when no content inside nf-ripper.json, that is, an empty List inside nf-ripper.json


def fetchPosterURl(bSoup):
    tmpPosterURL = bSoup.find('div', class_='hero-image-container')
    desktopPosterURL = str(tmpPosterURL.find('div', class_='hero-image hero-image-desktop'))
    desktopPosterURL = desktopPosterURL[(desktopPosterURL.find('url(')+5):(desktopPosterURL.find('")'))]
    mobilePosterURL = str(tmpPosterURL.find('div', class_='hero-image hero-image-mobile'))
    mobilePosterURL = mobilePosterURL[(mobilePosterURL.find('url(')+5):(mobilePosterURL.find('")'))]
    return desktopPosterURL, mobilePosterURL


def isAlreadySavedIntoJson(NFtitle:str):
    jsonObj, jsonFileName = getDataFromJsonFile()
    if (jsonObj is None) or (jsonFileName is None):
        return False
    jsonObjLength = len(jsonObj)
    for index in range(0,jsonObjLength):    
        jsonObjTitle = jsonObj[index]['NFtitle']
        if jsonObjTitle.casefold() == NFtitle.casefold():
            return True
    return False



def fetchMetadata(bSoup, UID:int, url:str):
    jsonObj, jsonFileName = getDataFromJsonFile()
    desktopPosterURL, mobilePosterURL = fetchPosterURl(bSoup=bSoup)
    metadata = bSoup.find('script', type='application/ld+json').contents[0]
    metadataJson = json.loads(metadata)
    NFtitle = metadataJson['name']
    if not isAlreadySavedIntoJson(NFtitle=NFtitle):
        NFcontentType = metadataJson['@type']
        NFcontentRating = metadataJson['contentRating']
        NFdescription = metadataJson['description']
        NFgenre = metadataJson['genre']
        NFimage = metadataJson['image']
        NFtrailersList = []
        try:
            for trailer in metadataJson['trailer']:
                NFtrailerName = trailer['name']
                NFtrailerThumbnailURL = trailer['thumbnailUrl']
                NFtrailerVideoURL = trailer['contentUrl']
                NFtrailerDict = {
                    'NFtrailerName': NFtrailerName,
                    'NFtrailerThumbnailURL': NFtrailerThumbnailURL,
                    'NFtrailerVideoURL': NFtrailerVideoURL
                }
                NFtrailersList.append(NFtrailerDict)
        except KeyError:
            NFtrailersList = None
        NFactorsList = []
        for actor in metadataJson['actors']:
            NFactorName = actor['name']
            NFactorsList.append(NFactorName)
        finalMetadata = {
            'NF-UID': UID,
            'NF-url': url,
            'NFdesktopPosterURL': desktopPosterURL,
            'NFmobilePosterURL': mobilePosterURL,
            'NFcontentType': NFcontentType,
            'NFcontentRating': NFcontentRating,
            'NFtitle': NFtitle,
            'NFdescription': NFdescription,
            'NFgenre': NFgenre,
            'NFimage': NFimage,
            'NFtrailersList': NFtrailersList,
            'NFactorsList': NFactorsList
        }
        writeToJsonFile(inputDictnry=finalMetadata, jsonObj=jsonObj, jsonFileName=jsonFileName)
    else:
        print(f'{url} - already saved in the List with same Name, {NFtitle}')


def getBeautifulSoup(url:str):
    myCustmHeader = {
        'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'
    }
    req = requests.get(url, headers=myCustmHeader)
    bSoup = BeautifulSoup(req.content, 'html.parser')
    return bSoup


def checkNFLink(url:str) -> bool|None:
    myCustmHeader = {
        'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'
    }
    req = requests.get(url, headers=myCustmHeader) 
    print(f'{url} - {req.status_code}')
    if req.status_code == 200:
        return True
    elif req.status_code == 404:
        return False
    else:
        return None  

def looperUID():
    for urlID in range(1, 90_000_000):
        urlIDstr = "7" + (str(urlID).zfill(7))
        url = f'https://www.netflix.com/in/title/{urlIDstr}'
        isLinkValid = checkNFLink(url=url)
        if isLinkValid is None:   # None => status_code != 200 & 404
            print(f'None')
        if isLinkValid: #True => status_code = 200
            bSoup = getBeautifulSoup(url=url)
            fetchMetadata(bSoup=bSoup, UID=int(urlIDstr), url=url)
        else:
            print(f'404, not found')


def main():
    createEmptyListInJsonFile()
    looperUID()


if __name__ == '__main__':
    main()