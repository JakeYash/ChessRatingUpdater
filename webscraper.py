import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests
from bs4 import BeautifulSoup
import re
import vars # type: ignore

# Define the scope
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Add your credentials to the account
# creds = ServiceAccountCredentials.from_json_keyfile_name('./bchessratings-fc5c5b0d5548.json', scope)
creds = ServiceAccountCredentials.from_json_keyfile_name(vars.gsheets_api_key_file, scope)


# Authorize the clientsheet 
client = gspread.authorize(creds)

# Open your Google Sheet 
sourceSheet = client.open("BC - Students for Website").sheet1
targetSheet = client.open("RATINGS").sheet1


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

updater = []

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
            # level_start = text.find('"level":')
            # if level_start != -1:
            #     # Limit the search to the next ~200 characters to stay inside the ratings block
            #     snippet = text[level_start:level_start + 200]
                
            #     #search for fastchess in shortened block
            #     matchP = re.search(r'"piece":"(\w+)"', snippet)
            #     matchN = re.search(r'"number":"(\w+)"', snippet)
            #     if matchP and matchN:
            #         ckidll = matchP.group(1) + " " + matchN.group(1)

    # Write data to sheet
    updater.append([n,uscfr,lichessrapid,lichesspuzzleR,lichesspuzzleS,ckidpr,ckidfr])

targetSheet.resize(rows=2)
rsizes = len(updater)
targetSheet.update(range_name = f'A{2}:G{rsizes+1}',values = updater)
