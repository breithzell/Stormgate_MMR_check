# importing the requests library
import requests
import pandas
import time
import matplotlib.pyplot as plt
import datetime
import numpy

# api-endpoint
URL = "https://api.stormgate.untapped.gg/api/v1/leaderboard?match_mode=ranked_1v1"

# defining a params dict for the parameters to be sent to the API
PARAMS = {}

# sending get request and saving the response as response object
r = requests.get(url = URL, params = PARAMS)

# extracting data in json format
data = r.json()

own_rank = []
adv_rank = []
date = []
forbidden = 0

# Extract last 100 games
for player in data:
    time.sleep(3)
    print(f'Working on {player['playerName']}')
    profileId=player['profileId']
    matchMode= 'ranked_1v1'
    season=  'current'
    URL = f'https://api.stormgate.untapped.gg/api/v2/matches/players/{profileId}/recent/{matchMode}?season={season}'
    r = requests.get(url = URL)
    try:
        games = r.json()
    except:
        print(f'Player {player['playerName']} does not allow to use his history')
        continue
    if "detail" in games.keys(): 
        forbidden = forbidden + 1
        continue
    for race in games.keys():
        for game in games[race][:]:
            own_rank.append( game['players'][0]['previous_ranking']['points'] )
            adv_rank.append( game['players'][1]['previous_ranking']['points'] )
            date.append(game['match_start'])


df = pandas.DataFrame({
    'date': date,
    'own_rank': own_rank,
    'adv_rank': adv_rank,
    })

df.to_csv('MMR_data.csv')
df['date'] = [ datetime.datetime.fromtimestamp( f ) for f in df.date]
df['Rank_Difference'] = numpy.abs(df['own_rank'] - df['adv_rank'])

dd = df.set_index('date').sort_index()
dd['Rank_Difference'].plot(marker='o', ylabel='MMR difference', linestyle='', markersize=0.5)
plt.title(f'Sampling: {len(dd)} make from the history of {500-forbidden} players')
plt.save('Rank_Difference.png')
dd['Rank_Difference'].resample('1d').median('date').plot(marker='o', ylabel='Daily median MMR difference', linestyle='-', markersize=1)
plt.save('Rank_Difference_median_per_day.png')
plt.close()