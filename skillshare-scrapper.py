import json
from time import sleep
import requests

def scrapeDetailed() -> None:
    return

def fetchBasic(numOfCourse=1, lastCourseID=""):
    url = "https://www.skillshare.com/api/graphql"
    
    payload = "{\"query\":\"query GetClassesByType {\\n\\tclassListByType(\\n\\t\\ttype: TRENDING_CLASSES\\n\\t\\tfirst: %s\\n\\t\\tafter: \\\"%s\\\"\\n\\t) {\\n\\t\\ttotalCount\\n\\t\\tnodes {\\n\\t\\t\\tid\\n\\t\\t\\ttitle\\n\\t\\t\\tsmallCoverUrl\\n\\t\\t\\tlargeCoverUrl\\n\\t\\t\\turl\\n\\t\\t\\tsku\\n\\t\\t\\tlargeCoverUrl\\n\\t\\t\\tstudentCount\\n\\t\\t\\tdurationInSeconds\\n\\t\\t\\tteacher {\\n\\t\\t\\t\\tid\\n\\t\\t\\t\\tname\\n\\t\\t\\t\\tfirstName\\n\\t\\t\\t\\tlastName\\n\\t\\t\\t\\tusername\\n\\t\\t\\t\\theadline\\n\\t\\t\\t\\tvanityUsername\\n\\t\\t\\t\\tsmallPictureUrl\\n\\t\\t\\t\\tlargePictureUrl\\n\\t\\t\\t\\t__typename\\n\\t\\t\\t}\\n\\t\\t\\tbadges {\\n\\t\\t\\t\\ttype\\n\\t\\t\\t\\t__typename\\n\\t\\t\\t}\\n\\t\\t\\tviewer {\\n\\t\\t\\t\\thasSavedClass\\n\\t\\t\\t\\t__typename\\n\\t\\t\\t}\\n\\t\\t\\t__typename\\n\\t\\t}\\n\\t\\t__typename\\n\\t}\\n}\\n\",\"operationName\":\"GetClassesByType\"}" %(numOfCourse, lastCourseID)
    headers = {
        "cookie": "device_session_id=72c162f4-c0d0-4a3d-8225-a08ea273ab20; __cf_bm=7AXBk1xfgX0b9yqm8NlMmshvrknCnx.irjb9nu3qy48-1666610805-0-AXgkNf9A4bHMTCUjvnJRdUkWg12Kkr0ZQ1ERmxGIFUyHqxy3qPaz4MliQN5uM1dDofV6VJ9tQO2uzuJmnE4txudthUVX0UWjmWCRaZoDhx5F; device_session_id=72c162f4-c0d0-4a3d-8225-a08ea273ab20",
        "Content-Type": "application/json",
        "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36"
    }

    response = requests.request("POST", url=url, data=payload, headers=headers)
    print(json.dumps(json.loads(response.text), indent=4))
    return response.json()

def scrapeBasic() -> None:
    response = fetchBasic(numOfCourse=1000)
    totalCourses = int(response["data"]["classListByType"]["totalCount"])
    lastCourseID = "eyJpZCI6IjI1MDUyMyIsInR5cGUiOiJDbGFzcyJ9"
    for index in range(1, int(totalCourses/1000)+2):
        response = fetchBasic(numOfCourse=1000, lastCourseID=lastCourseID)
        lastCourseID = response["data"]["classListByType"]["nodes"].pop()["id"]
        sleep(3)
    print(f"{totalCourses = }")
    print(f"{lastCourseID = }")

def scrapeIt() -> None:
    print(f"""Choose the desired option from the List:
    1) To scrape basic data only. (course-teacher name, basic data) (ETA: 3-5 minutes)
    2) To scrape detailed data. (about the course, each lecture video thumbnail, etc) (ETA: >1 day)""")
    inp = int(input("Enter your choice (1/2): "))
    if (inp == 1):
        scrapeBasic()
    elif (inp == 2):
        scrapeDetailed()
    else:
        print("Read the Instruction again")
        scrapeIt()

def main():
    scrapeIt()


if __name__ == '__main__':
    main()