import requests
from bs4 import BeautifulSoup
import csv
from selenium import webdriver
from time import sleep
from selenium.webdriver.common.keys import Keys
import datetime
from random import randint
import re


def randSleep():
    sleep(0.1)
    sleep(randint(0, 2))
    return None


def getSearchURLs(searchTerms):
    res = []
    driver = webdriver.Chrome()
    driver.get('https://www.glassdoor.ca/Job/google-jobs-SRCH_KE0,6.htm')
    randSleep()

    for searchTerm in searchTerms:
        randSleep()
        randSleep()
        randSleep()
        inputElement = driver.find_element_by_id("sc.keyword")
        inputElement.clear()
        inputElement.send_keys(searchTerm)
        inputElement.send_keys(Keys.ENTER)
        randSleep()
        res.append(driver.current_url)

    return res


def downloadCSV(result, file):
    keys = result[0].keys()
    with open('D:/Python Projects/Job Finder/jobCSVs/' + file, 'w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(result)


def extractJobs(URL):
    try:
        # Navigate to the URL and pull all the jobs on it
        print(URL)
        if "_IP" in URL:
            currentPage = int(re.search("_IP([\d]*)", URL).group(1))
        else:
            currentPage = 1
        jobListPage = requests.get(URL, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'})
        randSleep()
        soupJobListPage = BeautifulSoup(jobListPage.text, "html.parser")

        allJobMetaData = soupJobListPage.find_all(name="div", attrs={"class": "jobContainer"})

        # Get the max number of pages we can search through
        PageHTML = soupJobListPage.find(name="div", attrs={"class": "cell middle hideMob padVertSm"}).get_text()
        splitPages = PageHTML.split()
        nextPage = currentPage + 1
        totalPages = int(splitPages[3])

        # For every job on the page, do this loop
        for j, div in enumerate(allJobMetaData, start=0):
            while True:
                try:
                    company = div.find_all(name="a", attrs={"class": "jobTitle"})[0].get_text()
                    jobLink = "https://www.glassdoor.ca" + str(div.find_all(name="a", attrs={"class": "jobTitle"})[1]["href"])
                    # Get job  details and a link to the job application page
                    jobMetaData = {
                        "companyName": company,
                        "jobTitle": str(div.find_all(name="a", attrs={"class": "jobTitle"})[1].get_text()).lower(),
                        "location": div.find(name="span", attrs={"class": "loc"}).get_text(),
                        "applicationLink": jobLink
                    }

                    if ("paid" not in jobMetaData["companyName"]) and (jobMetaData["companyName"] in companyList) and any(inputTerm.lower() in jobMetaData["jobTitle"] for inputTerm in inputList):
                        if any(storedJob["companyName"] == jobMetaData["companyName"] for storedJob in jobDict):
                            if any(((storedJob["companyName"] == jobMetaData["companyName"]) and (storedJob["jobTitle"] == jobMetaData["jobTitle"])) for storedJob in jobDict):
                                break
                            else:
                                jobDict.append(jobMetaData)
                        else:
                            jobDict.append(jobMetaData)
                    break
                except Exception as ex1:
                    print("Error 1: ", ex1)
                    sleep(1)
                    continue

        # These statements control moving to the next page
        if (currentPage < totalPages) and (currentPage < NoOfPagesToSearch):
            if "_IP" not in URL:
                insertPosition = URL.find(".htm")
                newURL = URL[:insertPosition] + "_IP" + str(nextPage) + URL[insertPosition:]
                extractJobs(newURL)
            elif "_IP" in URL and currentPage < 10:
                insertPosition = URL.find("_IP") + 3
                newURL = URL[:insertPosition] + str(nextPage) + URL[1 + insertPosition:]
                extractJobs(newURL)
            elif "_IP" in URL and currentPage >= 10:
                insertPosition = URL.find("_IP") + 3
                newURL = URL[:insertPosition] + str(nextPage) + URL[2 + insertPosition:]
                extractJobs(newURL)
        return
    except Exception as ex2:
        print("Error 2: ", ex2)
        return


inputList = [
    "engineer",
    "specialist",
    "technical",
    "cloud",
    "python",
    "customer",
    "pre-sales",
    "presales",
    "sales",
    "solution"
]

companyList = [
    "Google",
    "MuleSoft",
    "Microsoft",
    "Salesforce",
    "Cisco Systems",
    "Apple",
    "DocuSign",
    "LinkedIn",
    "Facebook",
    "VMware",
    "Adobe",
    "SAP",
    "Slack",
    "Intel Corporation",
    "Oracle",
    "IBM",
    "Shopify",
    "Ceridian",
    "Wealthsimple",
    "Zoom Video Communications",
    "PagerDuty"
]

NoOfPagesToSearch = 9

timeNow = datetime.datetime.now()
formattedTime = timeNow.strftime("%d") + "-" + timeNow.strftime("%b") + "-" + timeNow.strftime("%Y")
fileName = 'JobsByCompanyWithFilter-' + formattedTime + '.csv'

jobDict = []

URLList = getSearchURLs(companyList)
for jobURL in URLList:
    extractJobs(jobURL)

downloadCSV(jobDict, fileName)
