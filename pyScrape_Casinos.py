##*********************HEADER*********************##
##Developer     : Justin Suelflow
##Date          : 12/28/2016
##Program Name  : pyScrape_Casinos
##Description   : Loop through all Leafly dispensary websites to find phone number, business name
##                  address, city, state, zip code, and url of leafly link
##Python Version: 2.7.11
##Prereqs Knowledge: Python, HTML, CSS, XPath
##Prereqs Hardware: Any computer that has a C++ compiler (libxml2 uses C++)
##Prereqs Software: Python, pip
##Python Libraries: LXML, requests, csv, json, re, libxml2, os, libxslt, datetime
##Static variables: header row in CSV, mainURL, mainXPath, paraXPath
##-----------------------------------------------------------------------------
## Version  | mm/dd/yyyy  |  User           |                Changes
##    1       12/28/2016    Justin Suelflow   Tested version of production code
##-----------------------------------------------------------------------------
##*********************END HEADER*********************##

##*********************IMPORT*********************##
##  Import needed python libraries
##  Libraries must be installed using 'pip install'
##  pyTimer.py file is found at https://github.com/Test-BMOHB/Media-Monitoring/blob/master/pyTimer.py
from lxml import html
from lxml.etree import tostring
from datetime import datetime
import requests, csv, re, json, pyTimer, os.path
##*********************END IMPORT*********************##

##*********************FUNCTIONS*********************##
##  Function	: scrapeInfo
##  Description	: Scrapes name, phone number, address, city, state, zip code and url from all links on mainURL
##  Parameters	: mainURL = string type, mainContent = string type, mainXPath = string type, paraXPath = string type
##  Returns	: list
def scrapeInfo(mainURL, mainContent, mainXPath, paraXPath):
    li = []
    mainLinksXPath = mainContent.xpath(mainXPath)
##  Creates a set of mainLinksXPath which takes out the duplicates and then format the set back to a list
    mainLinksXPath = list(set(mainLinksXPath))
##  Loop through elements in mainLinksXPath
    for mainLinksElements in mainLinksXPath:
##  Find all anchor tags in HTML element
        link = mainLinksElements.find('a')
##  Get the href parameter from the anchor tags
        link = link.get('href')
        link = 'http://www.americancasinoguide.com' + link
##  Send a http request to the link
        linkRequest = requests.get(link)
##  Translate the content from the request to HTML
        linkContent = html.fromstring(linkRequest.content)
##  Use xpath to find the elements in the HTML
        linkXPath = linkContent.xpath(paraXPath)
        finList = []
        writeToLog("Scraping " + link + "\n")
##  Loop through elements in linkXPath
        for linkXElement in linkXPath:
##  Find all li tags in HTML element
            listElements = linkXElement.xpath('.//li[not(@class) or not(@style)]')
            for listElement in listElements:
##  Find all anchor tags in HTML element
                link2 = listElement.find('a')
                if link2 is not None:
##  Get the href parameter from the anchor tags
                    link2 = link2.get('href')
##            text = tostring(link2)
                    if re.search("http", link2) is not None or re.search("/casinos-by-state/", link2) is not None:
                        continue
                    elif link2 in ['/casino-news', '/online-casino-promotions.html', '/contact-us.html', '/about-the-author.html', '/privacy-policy.html', '/terms-and-conditions.html']:
                        continue
                    finList.append(link2)
##  Loop through finList to translate elements and add to list
        for i in finList:
            casinoLink = 'http://www.americancasinoguide.com' + i
            casinoRequest = requests.get(casinoLink)
            casinoContent = html.fromstring(casinoRequest.content)
            casinoNameElement = casinoContent.xpath('//*[@itemprop="name"]')
            casinoPhoneElement = casinoContent.xpath('//*[@class="jrFieldRow jrPhone"]/div[@class="jrFieldValue "]')
            casinoAddrElement = casinoContent.xpath('//*[@class="jrFieldRow jrAddress"]/div[@class="jrFieldValue "]')
            casinoCityElement = casinoContent.xpath('//*[@class="jrFieldRow jrCity"]/div[@class="jrFieldValue "]')
            casinoStateElement = casinoContent.xpath('//*[@class="jrFieldRow jrState"]/div[@class="jrFieldValue "]')
            casinoZipElement = casinoContent.xpath('//*[@class="jrFieldRow jrZipcode"]/div[@class="jrFieldValue "]')
            casinoURLElement = casinoContent.xpath('//*[@class="jrFieldRow jrWebsite"]/div[@class="jrFieldValue "]/a')
#################### Need to trim for leading spaces
            name = ''
            phone = ''
            address = ''
            city = ''
            state = ''
            zipcode = ''
            url = ''
            if len(casinoNameElement) > 0:
                name = casinoNameElement[0].text
            if len(casinoPhoneElement) > 0:
                phone = casinoPhoneElement[0].text
            if len(casinoAddrElement) > 0:
                address = casinoAddrElement[0].text
            if len(casinoCityElement) > 0:
                city = casinoCityElement[0].text
            if len(casinoStateElement) > 0:
                state = casinoStateElement[0].text
            if len(casinoZipElement) > 0:
                zipcode = casinoZipElement[0].text
            if len(casinoURLElement) > 0:
                url = casinoURLElement[0].text
            li.append([name,phone,address,city,state,zipcode,url])
    return li

##  Function	: removeDuplicates
##  Description	: Remove exact duplicate list entries
##  Parameters	: dedup = list type
##  Returns	: list
def removeDuplicates(dedup):
    finalList = []
    for x in dedup:
        if x not in finalList:
            finalList.append(x)
    return finalList

##  Function	: writeToLog
##  Description	: Write text to log
##  Parameters	: text = string type
##  Returns	:
def writeToLog(text):
##  Open a log file and append to the end of the log
    logFile = open('/Logs/pylog_Casinos.txt','a')
    logFile.write(text)
##  Close log file
    logFile.close()

##  Function	: createCSV
##  Description	: Writes list to a CSV file
##  Parameters	: liCSV = list type, f1 = file type
##  Returns	:
def createCSV(liCSV, f1):
    writeToLog("Writing to CSV\n")
##  Use the ^ as a delimiter because the data on Leafly has lots of other special characters including commas
##  Needed to find a special character that was not used by the data
    writer = csv.writer(f1, delimiter=',', quoting=csv.QUOTE_NONE, escapechar=' ')
##  Add a header row to the CSV
    writer.writerow(["Casino","PhoneNumber","Address","City","State","ZipCode","Website"])
##  Loop through all elements in the list
    for i in liCSV:
        rowStr = ''
##  Some elements are lists so it is needed to loop through each element again
        for e in i:
            rowStr = rowStr + e.encode('utf-8')
            rowStr = rowStr + ','
##  Take the last , off of the rowStr to finish the row
        rowStr = rowStr[:-1]
##  Write the row to the CSV file
        writer.writerow([rowStr])

##*********************MAIN FUNCTION*********************##
##  Function	: main
##  Description	: Opens file, http request mainURL and call other functions
##  Parameters	: mainURLList = list type
##  Returns	:
def main(mainURL, mainXPath, linkXPath, fileName):
    liData = []
    writeToLog('***********************************************************************\n')
##  Open a file and overwrite the existing file or create a new file if needed
    with open(fileName,'w') as scrapeFile:
##  Http request the mainURL
        mainRequest = requests.get(mainURL)
##  Translate the request content to HTML
        mainContent = html.fromstring(mainRequest.content)
##  Add the information that comes from the scrapeInfo function to a list
##  scrapeInfo needs the url, content and 2 xpath variables to call the function
##  scrapeInfo returns a list when completed
        liData.extend(scrapeInfo(mainURL, mainContent, mainXPath, linkXPath))
##  Call function removeDuplicates
        beforeDedup = len(liData)
        liData = removeDuplicates(liData)
        writeToLog(str(len(liData)) + " records of " + str(beforeDedup) + " left after deduplication\n")
##  Call createCSV function to write the list data to the scrapeFile
##  createCSV needs a list and an open file to run
        createCSV(liData, scrapeFile)
##*********************END MAIN FUNCTION*********************##

##*********************END FUNCTIONS*********************##

##*********************PROGRAM*********************##
##  If statement makes this program standalone
##  Do not need this if statement if another program will be calling above functions
if __name__ == "__main__":
##  Create start time
    startTime = pyTimer.startTimer()
    currDate = datetime.now()
    fileDate = currDate.strftime('%m%d%Y')
    currDate = currDate.strftime('%Y-%m-%d')
    fileName = '/Scrapes/' + fileDate + '_Casino_Scrape.csv'
    main('http://www.americancasinoguide.com/casinos-by-state.html', '//*[@class="list-title"]', './/ul[not(@class) or not(@style)]', fileName)
##  Find total time in seconds of program run
    pName = os.path.basename(__file__)
    endTime = pyTimer.endTimer(startTime, pName)
    writeToLog("Program took " + endTime + " to complete.\n")

##*********************END PROGRAM*********************##
