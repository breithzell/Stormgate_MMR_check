# importing the requests library
import requests
import pandas
import time
import matplotlib.pyplot as plt
import datetime
import numpy
import scipy.stats as stats

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
plt.title(f'Sampling: {len(dd)} make from the history of XX players')
plt.savefig('Rank_Difference.png')
dd['Rank_Difference'].resample('1d').median('date').plot(marker='o', ylabel='Daily median MMR difference', linestyle='-', markersize=1)
plt.savefig('Rank_Difference_median_per_day.png')
plt.close()

# Normal distribution
df_mean = numpy.mean(df['Rank_Difference'])
df_std = numpy.std(df['Rank_Difference'])
pdf = stats.norm.pdf(df["Rank_Difference"].sort_values(), df_mean, df_std)
plt.plot(df["Rank_Difference"].sort_values(), pdf*100)

periods = [['2024-08-01', '2024-09-30'], ['2024-10-01', '2024-11-13'], ['2024-11-14', '2024-11-30']]
period_txt = ['All', '2024-08-01 > 2024-09-30', '2024-10-01 > 2024-11-13', '2024-11-14 > 2024-11-30']
for period in periods:
    df_mean = numpy.mean(df['Rank_Difference'].where((df['date'] >= period[0]) & (df['date'] < period[1])) )
    df_std = numpy.std(df['Rank_Difference'].where((df['date'] >= period[0]) & (df['date'] < period[1])) )
    pdf = stats.norm.pdf(df["Rank_Difference"].where((df['date'] >= period[0]) & (df['date'] < period[1])).sort_values(), df_mean, df_std)
    plt.plot(df["Rank_Difference"].where((df['date'] >= period[0]) & (df['date'] < period[1])).sort_values(), pdf*100)

plt.xlabel("Rank difference (MMR)")
plt.ylabel("Frequency (%)")
plt.legend(period_txt[:])
plt.grid(True, alpha=0.3, linestyle="--")
plt.savefig('Probability_density_function.png')
plt.close()

# Binned histogram
periods = [['2024-08-01', '2024-09-30'], ['2024-10-01', '2024-11-13'], ['2024-11-14', '2024-11-30']]
period_txt = ['All', '2024-08-01 > 2024-09-30', '2024-10-01 > 2024-11-13', '2024-11-14 > 2024-11-30']
for bin_size,bin_mmr in zip([25, 10, 5], [100, 250, 500]):
    g, ax = plt.subplots()
    for period in periods:
        df.where((df['date'] >= period[0]) & (df['date'] < period[1])).hist('own_rank', bins=bin_size, ax=ax)
    plt.xlabel("Count (in games)")
    plt.ylabel("Own MMR range")
    plt.legend(period_txt[:])
    plt.grid(True, alpha=0.3, linestyle="--")
    plt.savefig(f'Available_players_by_{bin_mmr}.png')
    plt.close()

periods = [['2024-08-01', '2024-09-30'], ['2024-10-01', '2024-11-13'], ['2024-11-14', '2024-11-30']]
period_txt = ['All', '2024-08-01 > 2024-09-30', '2024-10-01 > 2024-11-13', '2024-11-14 > 2024-11-30']
for bin_size,bin_mmr in zip([25, 10, 5], [100, 250, 500]):
    g, ax = plt.subplots()
    for period in periods:
        df.where((df['date'] >= period[0]) & (df['date'] < period[1])).hist('adv_rank', bins=bin_size, ax=ax)
    plt.xlabel("Count (in games)")
    plt.ylabel("Opponent MMR range")
    plt.legend(period_txt[:])
    plt.grid(True, alpha=0.3, linestyle="--")
    plt.savefig(f'Available_players_by_opponent_{bin_mmr}.png')
    plt.close()