import requests
from bs4 import BeautifulSoup
from bs4 import Comment
import csv
import operator

def convert_time(start_time):
    seperate = start_time.split(':')
    new_hour = int(seperate[0]) + 12 - 3
    rest = seperate[1].rstrip()
    # if new_hour > 23:
    #     new_hour -= 2
    #     rest = list(rest)
    #     rest[2] = 'A'
    #     rest = "".join(rest)
    return (str(new_hour) + ":" + rest)

print_mode = True
reliefdict = {}
leftopsdict = {}
rightopsdict = {}
last7opsdict = {}
wrcdict = {}
abbrevdict = {}
with open('abbrevs.csv','r') as csvfile:
    csvreader = csv.reader(csvfile)
    for line in csvreader:
        brevteam = line[0].split("|")
        abbrevdict[brevteam[0]] = brevteam[1]

rank = 1
with open('relief.csv','r') as csvfile:
    csvreader = csv.reader(csvfile)
    header = next(csvreader)
    sortedlist = sorted(csvreader, key=operator.itemgetter(14), reverse=False)
    for line in sortedlist:
        team_name = line[0]
        if line[0] == "Diamondbacks":
            team_name = "D'backs"
        reliefdict[team_name] = [rank, float(line[14])]
        rank += 1

rank = 1
with open('leftops.csv','r') as csvfile:
    csvreader = csv.reader(csvfile)
    header = next(csvreader)
    sortedlist = sorted(csvreader, key=operator.itemgetter(8), reverse=True)
    for line in sortedlist:
        team_name = line[0]
        if line[0] == "Diamondbacks":
            team_name = "D'backs"
        leftopsdict[team_name] = [rank, float(line[8])]
        rank += 1

rank = 1
with open('rightops.csv','r') as csvfile:
    csvreader = csv.reader(csvfile)
    header = next(csvreader)
    sortedlist = sorted(csvreader, key=operator.itemgetter(8), reverse=True)
    for line in sortedlist:
        team_name = line[0]
        if line[0] == "Diamondbacks":
            team_name = "D'backs"
        rightopsdict[team_name] = [rank, float(line[8])]
        rank += 1

rank = 1
with open('last7ops.csv','r') as csvfile:
    csvreader = csv.reader(csvfile)
    header = next(csvreader)
    sortedlist = sorted(csvreader, key=operator.itemgetter(8), reverse=True)
    for line in sortedlist:
        team_name = line[0]
        if line[0] == "Diamondbacks":
            team_name = "D'backs"
        last7opsdict[team_name] = [rank, float(line[8])]
        rank += 1

rank = 1
with open('wrc.csv','r') as csvfile:
    csvreader = csv.reader(csvfile)
    header = next(csvreader)
    sortedlist = sorted(csvreader, key=lambda row: int(row[18]), reverse=True)
    for line in sortedlist:
        team_name = line[0]
        if line[0] == "Diamondbacks":
            team_name = "D'backs"
        wrcdict[team_name] = rank
        rank += 1

url = "https://www.baseball-reference.com"
doc = requests.get(url + "/previews/")
soup = BeautifulSoup(doc.text, 'html.parser')

game_boxes = soup.find_all('div', class_='game_summary nohover')
for gamebox in game_boxes:
    tables = gamebox.find_all('table')
    if len(tables) < 2:
        continue
    table1 = tables[0] # contains team names and preview link
    table2 = tables[1] # contains abbrevs and pitchers
    brevs = table2.find_all('strong')
    if len(brevs) < 2:
        continue
    awaybrev = brevs[0].get_text()
    homebrev = brevs[1].get_text()
    pitchers = table2.find_all('td')
    if len(pitchers) < 4:
    	continue
    away_pitcher = pitchers[1].get_text()
    home_pitcher = pitchers[3].get_text()
    teams = table1.find_all('a')
    away_team = teams[0].get_text()
    home_team = teams[2].get_text()
    times = table1.find_all('td')
    start_time = convert_time(times[-1].get_text())
    away_team_print = awaybrev + " " + away_team
    home_team_print = homebrev + " " + home_team
    records = table1.find_all('span', class_='pollrank')
    away_record = records[0].get_text()
    home_record = records[1].get_text()

    # print(away_team_print + away_record + "@ " + home_team_print + home_record)

    # off = [[],[]] # away first, home second
    pperfs = [[],[]] # away first, home second
    psummary = [[],[]]
    prev_url_ext = teams[1]['href']
    match_url = url + prev_url_ext
    match_doc = requests.get(match_url)
    match_soup = BeautifulSoup(match_doc.text, 'html.parser')
    team_infos = match_soup.find_all('div', class_='section_wrapper floated')
    team_index = 0
    skip = False
    for section in team_infos:
        commented_tables = section.find_all(string=lambda text: isinstance(text, Comment))
        offense_soup = BeautifulSoup(commented_tables[0], 'html.parser')
        # rows = offense_soup.find_all('tr')
        # for row in rows[1:7]:
        #     datums = row.find_all('td')
        #     runs = int(datums[4].get_text().split('-')[0])
        #     off[team_index].append(runs)
        if len(commented_tables) < 2:
        	skip = True
        	continue
        pitcher_soup = BeautifulSoup(commented_tables[1], 'html.parser')
        rows = pitcher_soup.find_all('tr')

        start_count = 0
        row_count = 0
        reached_spacer = False
        summary_line = [0.0,0,0]
        while True:
            if len(rows) > 0:
                datums = rows[row_count].find_all('td')
                date = rows[row_count].find('th').get_text()
            if len(rows) == 0 or (reached_spacer and date == "") or start_count == 5:
                if start_count != 0:
                    total_ip = round(summary_line[0],1)
                    lastdigit = int(str(total_ip)[-1])
                    added_innings = lastdigit // 3
                    remainder = lastdigit % 3
                    total_ip += added_innings
                    total_ip -= lastdigit/10
                    total_ip += remainder/10
                    avg_ip = round(total_ip/start_count,2)
                    whip = round(summary_line[1]/total_ip,2)
                    era = round(summary_line[2]/total_ip*9,2)
                    print_summary_line = [avg_ip, whip, era]
                    psummary[team_index] = (print_summary_line)
                else:
                    psummary[team_index] = (summary_line)
                break
            if reached_spacer:
                year = date.split('-')[0]
                if year == "2019":
                    opp = datums[0].get_text()
                    if opp[0] == '@':
                        opp = opp[1:]
                    ip = float(datums[2].get_text())
                    hits = int(datums[3].get_text())
                    er = int(datums[5].get_text())
                    bb = int(datums[6].get_text())
                    so = int(datums[7].get_text())
                    wrcrank = wrcdict[abbrevdict[opp]]
                    performance = [date,ip,hits,er,bb,so,opp,wrcrank]
                    summary_line[0] += ip
                    summary_line[1] += hits + bb
                    summary_line[2] += er
                    start_count += 1
                    pperfs[team_index].append(performance)
            if date == "Last 7 GS":
                reached_spacer = True
            row_count += 1

        team_index += 1
    # away_last5avg = round(sum(off[0])/6,1)
    # home_last5avg = round(sum(off[1])/6,1)
    if skip:
    	continue
    if print_mode:
        print("-------------------------------------------------------")
        print(start_time)
        print(away_team_print + away_record + "@ " + home_team_print + home_record)
        print()
        print(away_team_print + " Pitcher: " + away_pitcher)
        print("     Date    | IP | H|ER|BB|SO|  Opp | wRC+")
        for i in pperfs[0]:
            print(i)
        print("Last 5: " + str(psummary[0][0]) + "IP " + str(psummary[0][1]) + "WHIP " + str(psummary[0][2]) + "ERA")
        print(away_team + " Relief ERA: " + str(reliefdict[away_team][1]) + " Rank " + str(reliefdict[away_team][0]))
        away_starter_allowed = round(psummary[0][0]*psummary[0][2]/9,2)
        away_relief_allowed = round(reliefdict[away_team][1]*(9-psummary[0][0])/9,2)
        away_expected_allowed = round(away_starter_allowed + away_relief_allowed,2)
        print("Expected Allowed: " + str(away_starter_allowed) + " + " + str(away_relief_allowed) + " = " + str(away_expected_allowed))
        if away_pitcher.split(",")[2][1] == 'R':
            print(home_team + " OPS against Righties: " + str(rightopsdict[home_team][1]) + " Rank " + str(rightopsdict[home_team][0]))
        else:
            print(home_team + " OPS against Lefties: " + str(leftopsdict[home_team][1]) + " Rank " + str(leftopsdict[home_team][0]))
        # print(' '.join(str(e) for e in off[1]) + " Avg: " + str(home_last5avg))
        print("Last 7 OPS: " + str(last7opsdict[home_team][1]) + " Rank " + str(last7opsdict[home_team][0]) + " wRC+ Rank " + str(wrcdict[home_team]))
        print()
        print(home_team_print + " Pitcher: " + home_pitcher)
        print("     Date    | IP | H|ER|BB|SO|  Opp | wRC+")
        for i in pperfs[1]:
            print(i)
        print("Last 5: " + str(psummary[1][0]) + "IP " + str(psummary[1][1]) + "WHIP " + str(psummary[1][2]) + "ERA")
        print(home_team + " Relief ERA: " + str(reliefdict[home_team][1]) + " Rank " + str(reliefdict[home_team][0]))
        home_starter_allowed = round(psummary[1][0]*psummary[1][2]/9,2)
        home_relief_allowed = round(reliefdict[home_team][1]*(9-psummary[1][0])/9,2)
        home_expected_allowed = round(home_starter_allowed + home_relief_allowed,2)
        print("Expected Allowed: " + str(home_starter_allowed) + " + " + str(home_relief_allowed) + " = " + str(home_expected_allowed))
        if home_pitcher.split(",")[2][1] == 'R':
            print(away_team + " OPS against Righties: " + str(rightopsdict[away_team][1]) + " Rank " + str(rightopsdict[away_team][0]))
        else:
            print(away_team + " OPS against Lefties: " + str(leftopsdict[away_team][1]) + " Rank " + str(leftopsdict[away_team][0]))
        print("Last 7 OPS: " + str(last7opsdict[away_team][1]) + " Rank " + str(last7opsdict[away_team][0])+ " wRC+ Rank " + str(wrcdict[away_team]))
        print()
        away_predict = round(home_expected_allowed + 10 * (last7opsdict[away_team][1] - 0.72),2)
        home_predict = round(away_expected_allowed + 10 * (last7opsdict[home_team][1] - 0.72),2)
        print("Predicted Score: " + away_team_print + " " + str(away_predict) + " - " + str(home_predict) + " " + home_team_print)
        diff = round(away_predict - home_predict,2)
        total_pred = round(away_predict+home_predict,2)
        if diff > 0:
            print("Prediction: " + away_team + " by " + str(diff) + " | Total: " + str(total_pred))
        else:
            print("Prediction: " + home_team + " by " + str(-diff) + " | Total: " + str(total_pred))



