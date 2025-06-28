import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests
from bs4 import BeautifulSoup
import re
import vars #type: ignore
import xml.etree.ElementTree as ET


#Recursive function to traverse the rss for a dictionary with last 7 day stats
def traverse_rss(url, dict):
    response = requests.get(url)
    root = ET.fromstring(response.content)
    for child in root:
        if (child.tag == 'next'):
            traverse_rss(child.text, dict)
        else:
            name = child[0] #username
            lessonlevel = child[4] #lessonlevel
            last7 = child[9]
            lesscount = last7[3] #lessoncount
            workcount = last7[4] #workoutcount
            puzzlestats = last7[2]
            puzzlecorrect = puzzlestats[0] #puzzles correct
            puzzlerchange = puzzlestats[2] #puzzle rating change
            dict.update({name.text : [lessonlevel.text, int(puzzlecorrect.text),int(puzzlerchange.text), int(lesscount.text),int(workcount.text)]})

#function to make lists from the dictionary
def buildListsFromDict(uList,dict, lessLevList, puzzleCorrectList, puzzleRChangeList,lessCountList,workCountList):
    for i in uList:
        if i in dict:
            lessLevList.append(dict[i][0])
            puzzleCorrectList.append(dict[i][1])
            puzzleRChangeList.append(dict[i][2])
            lessCountList.append(dict[i][3])
            workCountList.append(dict[i][4])
        else:
            lessLevList.append(filler)
            puzzleCorrectList.append(filler)
            puzzleRChangeList.append(filler)
            lessCountList.append(filler)
            workCountList.append(filler)

def fail_Check(updater, list_of_lists):
    for i in range(1,len(list_of_lists)): #start one to skip headers
        og_list = list_of_lists[i]
        up_list = updater[i-1]

        #this makes sure the name matches (just in case new ones added or old ones removed), and makes it so if the new data were to
        # be empty, it wouldn't be filled with old data previously on that row, it would just stay new data
        if (og_list[0] != up_list[0]):
            foundMatch = False
            for p in list_of_lists:
                if (p[0] == up_list[0]):
                    og_list = p
                    foundMatch = True
                    break
            if (foundMatch == False):
                continue
            
        for j in range(1,len(og_list)): #start one to skip names
            if (up_list[j] == filler) and (og_list[j] != filler):
                updater[i-1][j] = og_list[j]



# Define the scope
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Add your credentials to the account
creds = ServiceAccountCredentials.from_json_keyfile_name(vars.gsheets_api_key_file, scope)


# Authorize the clientsheet 
client = gspread.authorize(creds)

# Open your Google Sheet 
sourceSheet = client.open("BC - Students for Website").sheet1
targetSheet = client.open("RATINGS").sheet1

#Make dictionary off of rss
dict = {}
traverse_rss(vars.rss_url, dict)

#build lists off of input sheet
fNameList = []
uscfList = []
lichessList = []
ckidList = []
filler = "---"

gList = sourceSheet.get_all_values()
for row in gList[1:]:
    fNameList.append(row[0])

    if (row[1] == ''): uscfList.append(filler)
    else: uscfList.append(row[1])

    if (row[2] == ''): lichessList.append(filler)
    else: lichessList.append(row[2])

    if (row[3] == ''): ckidList.append(filler)
    else: ckidList.append(row[3])

#make lists off of rss dictionary
lessLevList = []
puzzleCorrectList = []
puzzleRChangeList = []
lessCountList = []
workCountList = [] 
buildListsFromDict(ckidList,dict,lessLevList,puzzleCorrectList,puzzleRChangeList,lessCountList,workCountList)
#initialize updating list and counting variable to iterate and add
updater = []

count = 0


#iterate through all the lists, adding stats for each student to the end of the updater list
for i,j,k,n in zip(uscfList,lichessList,ckidList,fNameList):
    # USCF Ratings part
    uscfr = filler


    if (i != filler):
        try:
            url = f'https://www.uschess.org/msa/MbrDtlTnmtHst.php?{i}'

            # Fetch the page content
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')


                # Search for the first match of the rating pattern USCF
            match = re.search(r'=>\s*(\d{2,4})', soup.get_text())
            if (match): uscfr = int(match.group(1))
        except:
            pass
        

    #Lichess Ratings Part
    lichessrapid = filler
    lichesspuzzleR = filler
    lichesspuzzleS = filler

    if (j != filler):
        url = f"https://lichess.org/api/user/{j}"
        try:
            response = requests.get(url)
            data = response.json()


            lichessrapid = int(data["perfs"]["rapid"]["rating"])
            lichesspuzzleR = int(data["perfs"]["puzzle"]["rating"])
            lichesspuzzleS = int(data["perfs"]["puzzle"]["games"])
        except:
            pass

    #ChessKid Ratings Part
    # ckidll = filler
    ckidpr = filler
    ckidfr = filler

    if (k != filler):
        url = f"https://www.chesskid.com/callback/page/users/{k}/profile"
        
        try:
            response = requests.get(url)
            text = response.text


            # Find the "ratings" block first
            ratings_start = text.find('"ratings":')
            if ratings_start != -1:
                # Limit the search to the next ~200 characters to stay inside the ratings block
                snippet = text[ratings_start:ratings_start + 200]
                
                #search for fastchess in shortened block
                match = re.search(r'"fastChess":(\d+)', snippet)
                if match:
                    ckidfr = int(match.group(1))

                # Now search for the puzzles rating
                match = re.search(r'"puzzles":(\d+)', snippet)
                if match:
                    ckidpr = int(match.group(1))
        except:
            pass

    # Write data to sheet
    updater.append([n,uscfr,ckidpr,lessLevList[count],puzzleCorrectList[count],puzzleRChangeList[count],lessCountList[count],workCountList[count],ckidfr,lichessrapid,lichesspuzzleR,lichesspuzzleS])
    count = count + 1

#check for fillers not getting new values
list_of_lists = targetSheet.get_all_values()
fail_Check(updater, list_of_lists)

#using the updater list, add in all the necessary values to the target sheet
targetSheet.resize(rows=2)
rsizes = len(updater)
targetSheet.update(range_name = f'A{2}:L{rsizes+1}',values = updater)

