import requests
from bs4 import BeautifulSoup
from datetime import date
import timestring



def generateCaptionsFile():
    # for all pages, get urls of all parties on or before Dec 1st, 2014
    # for each party, go to that web page and scrape all captions
    # store all the captions in captions.txt

    captionsFile = open('captions.txt', 'w')

    # ~~~~~~~~~~~~~~~~~~~~~~~ for pages 6 to 30 get urls of all parties ~~~~~~~~~~~~~~~~~~~~~~~ #

    pageNumbers = [str(i) for i in range(0, 31)]
    pageURLs = []
    for page in pageNumbers:
        urlString = "http://www.newyorksocialdiary.com/party-pictures?page=" + page
        pageURLs.append(urlString)

    partyEndURLs = []
    cutOffDate = date(2014, 12, 1)

    for pageURL in pageURLs:
        # get urls of parties
        party = requests.get(pageURL)
        partySoup = BeautifulSoup(party.text, "html.parser")
        partyLinks = partySoup.find_all('span', class_='field-content')
        dates = partySoup.find_all('span', class_='views-field views-field-created')

        tempPartyEndURLs = []

        for i in range(0, len(partyLinks)):
            if i % 2 == 0:
                partyLink = partyLinks[i]
                tempPartyEndURLs.append(partyLink.a.attrs['href'])

        for i in range(0, len(tempPartyEndURLs)):
            day = dates[i].span.text
            dateString = timestring.Date(day)
            actualDate = date(dateString.year, dateString.month, dateString.day)

            if actualDate < cutOffDate:
                addPartyLink = tempPartyEndURLs[i]
                partyEndURLs.append(addPartyLink)


    # ~~~~~~~~~~~~~~~~~~~~~~~ get captions from all party web pages ~~~~~~~~~~~~~~~~~~~~~~~ #
    partyURLs = []
    for partyEndURL in partyEndURLs:
        partyURL = "http://www.newyorksocialdiary.com" + partyEndURL
        partyURLs.append(partyURL)

    captionsList = []

    for url in partyURLs:
        captn = requests.get(url)
        soup = BeautifulSoup(captn.text, "html.parser")
        captions = soup.find_all('div', class_='photocaption')

        if len(captions) <= 1:
            captions = soup.find_all('font')

        if len(captions) <= 1:
            captions = soup.find_all("td", {"class" : "photocaption"})

        for caption in captions:
            if ("Photograph" not in caption.text):
                captionsList.append(caption.text)
                writeCaption = caption.text.encode('utf8')
                captionsFile.write(writeCaption)
                captionsFile.write("*@CAPTION@*")


    captionsFile.close()



def removeSpecialCaptions():
    """ Remove Special Captions such as captions that contain 'photo' and 'by'

    """

def removeLongCaptions(captions):
    """ Remove captions from list if longer than 250 characters

    """
    returnMe = []
    for c in captions:
        if len(c) <= 250:
            returnMe.append(c)

    return returnMe

def removeWhiteSpace(captions):
    """ Remove endline '\n' and unneeded tabs and extra spaces from all entries

    """
    returnMe = []
    for c in captions:
        newC = c.replace('\n', '')
        newC = newC.replace('\t', '')
        newC = newC.strip()
        newC = ' '.join(newC.split())
        returnMe.append(newC)

    return returnMe


def splitByDelimeter(captions, delimeter):
    """ Split each caption by given delimeter into separate entries

    """
    returnMe = []
    for c in captions:
        splitList = c.split(delimeter)
        returnMe.extend(splitList)

    return returnMe

def solveAndCases(captions):
    """ Solve 'and' cases such as 'John and Mary Smith' --> 'John Smith' 'Mary Smith' by creating
        more than one caption for the two names, each with the correct first and last name

    """
    returnMe = []
    listOfNoAndLists = []

    for c in captions:
        if " and " in c:
            listOfNoAndLists.append(c.split(" and "))
        else:
            returnMe.append(c)

    for captn in listOfNoAndLists:
        captnList = []
        for name in captn:
            splitNameList = name.split()
            captnList.append(splitNameList)

        # case 1:
        # " and Christopher Roselli")
        # ["", "Christopher Roselli"]
        # [[], ['Christopher', 'Roselli']]
        if (len(captnList[0]) == 0):
            for i in range(1, len(captn)):
                returnMe.append(captn[i])
        # case 2:
        # "David and Nicole Diehl")
        # ["David", "Nicole Diehl"]
        # [['David'], ['Nicole', 'Diehl']]
        elif len(captnList[0]) == 1:
            try:
                firstAndLastName = captnList[0][0] + " " + captnList[1][1]
                returnMe.append(firstAndLastName)
                for i in range(1, len(captn)):
                    returnMe.append(captn[i])
            except:
                for i in range(0, len(captn)):
                    returnMe.append(captn[i])
        # case 3:
        # "Lizzie Rudnick Tisch and Jonathan Tisch")
        # ["Lizzie Rudnick Tisch", "Jonathan Tisch"]
        # [['Lizzie','Rudnick', 'Tisch'], ['Jonathan', 'Tisch']]
        else:
            for i in range(0, len(captn)):
                returnMe.append(captn[i])

    return returnMe


def remove1WordCaptions(captions):
    """ Remove all captions containing 1 or 0 words

    """
    returnMe = []
    for c in captions:
        splitList = c.split()
        if len(splitList) > 1:
            returnMe.append(c)
    print "\n\n\n\n\n"
    return returnMe

def removeLowerCaseWords(captions):
    """ Remove all fully lowercase words from captions

    """
    lowerCaseExceptions = ["de", "la"]

    returnMe = []
    for c in captions:
        noLowerCaseList = []
        splitList = c.split()
        for word in splitList:
            if (not word.islower()) and (not word in lowerCaseExceptions):
                noLowerCaseList.append(word)

        newCaption = ' '.join(noLowerCaseList)
        returnMe.append(newCaption)
    return returnMe

def removeUpperCaseWords(captions):
    """ Remove all fully uppercase words from captions

    """
    returnMe = []
    for c in captions:
        noUpperCaseList = []
        splitList = c.split()
        for word in splitList:
            if not word.isupper():
                noUpperCaseList.append(word)

        newCaption = ' '.join(noUpperCaseList)
        returnMe.append(newCaption)
    return returnMe

def removeTitles(captions):
    """ Remove prefixes, suffixes, and titles

    """
    titles = ["Dr.", "Mr.", "Mrs.", "Mayor", "Jr.", "Sister", "Brother", "III", "I", "II", "President", "Princess",
              "King", "Prince", "Queen", "Dutch", "Dutchess", "Judge", "Chef", "Honoree", "Co-chair", "Co-chairs",
              "Sir", "General", "Board", "Member", "Chair", "Department", "Trustee", "Trustees", "Chairman",
              "Executive", "Director", "The", "Magician", "Senior", "Junior", "Doctor", "Actor", "Actress",
              "Violinist", "Musician", "Guest", "Guests", "Staff", "Sergeant"
              ]

    returnMe = []
    for c in captions:
        noTitlesList = []
        splitList = c.split()
        for word in splitList:
            if not word in titles:
                noTitlesList.append(word)

        newCaption = ' '.join(noTitlesList)
        returnMe.append(newCaption)
    return returnMe

def removeMoreThan4Words(captions):
    """ Remove caption from list if it contains more than 4 words

    """
    returnMe = []
    for c in captions:
        splitList = c.split()
        if len(splitList) <= 4:
            newCaption = ' '.join(splitList)
            returnMe.append(newCaption)

    return returnMe


outFile = open('numberOfNames.txt', 'w')

#if len(readFile) <= 0:
generateCaptionsFile()

readCaptionsFile = open("captions.txt", 'r')
readFile = readCaptionsFile.read()

captions = readFile.split("*@CAPTION@*")

# remove long captions
captions = removeLongCaptions(captions)

# remove endlines
captions = removeWhiteSpace(captions)

# split by comma
captions = splitByDelimeter(captions, ",")

# split by semi colon
captions =  splitByDelimeter(captions, ";")

# split by 'with'
captions =  splitByDelimeter(captions, "with")

# solve and cases such as 'John and Mary Smith' --> 'John Smith' 'Mary Smith'
captions = solveAndCases(captions)

# remove all lowercase words in captions
captions = removeLowerCaseWords(captions)

# remove all uppercase words in captions
captions = removeUpperCaseWords(captions)

# remove prefixes / suffixes / titles
captions = removeTitles(captions)

# remove captions with more than 4 words
captions = removeMoreThan4Words(captions)

# remove captions with only 1 word
captions = remove1WordCaptions(captions)

outFile.write(str(len(captions)))
outFile.write("\n\n\n")

for c in captions:
    outFile.write(c)
    outFile.write("\n")


readCaptionsFile.close()
outFile.close()
