import sqlite3
import json
import zlib
import re
from datetime import datetime, timedelta 

#it may be nessecarry to deal with strange time issues, but for my machine and the server it should be fine

try:
    import dateutil.parser as parser
except:
    pass

def parsedate(ds) :
    """Parses an ISO-like date string from the API."""
    try:
        # Use dateutil.parser if available
        pdate = parser.parse(ds)
        return pdate.isoformat()
    except:
        # Fallback if dateutil is not installed/fails
        return ds.split('T')[0] # Fallback to just YYYY-MM-DD

# reading from the index table
conn = sqlite3.connect('file:raw_data.sqlite?mode=ro',uri = True)
cur = conn.cursor()

# writing tto the index table
connIDX = sqlite3.connect('rugby_index.sqlite')
curIDX = connIDX.cursor()

# refreshing the tables when re-runs are neccessary
curIDX.execute('DROP TABLE IF EXISTS Games')
curIDX.execute('''DROP TABLE IF EXISTS Teams''')
curIDX.execute('''DROP TABLE IF EXISTS Leagues''')

curIDX.execute('CREATE TABLE IF NOT EXISTS Leagues(id INTEGER PRIMARY KEY, league_name TEXT UNIQUE, TYPE TEXT,logo_url TEXT)')
curIDX.execute('CREATE TABLE IF NOT EXISTS Teams (id INTEGER PRIMARY KEY, team_name TEXT UNIQUE, national INTEGER, founded INTEGER, logo_url TEXT) ') 
curIDX.execute('''CREATE TABLE IF NOT EXISTS Games (id INTEGER PRIMARY KEY, league_id INTEGER, game_date TEXT, home_team_id INTEGER, away_team_id INTEGER, home_score INTEGER, away_score INTEGER, status TEXT, raw_json BLOB)''')

# dictionaires for the uniqe types of data
teams = dict()
leagues = dict()

def defineTeam(team_data):
    # Inserts or retrieves a team record
    if not team_data or 'id' not in team_data : return None

    team_id = team_data['id']
    team_name = team_data['name'].strip()

    if team_id in teams:
        return teams[team_id]
        
    #insert team here
    curIDX.execute('INSERT OR IGNORE INTO Teams (id, team_name, national, logo_url) VALUES ( ?, ?, ?, ? )', 
                   (team_id, team_name, team_data.get('national', 0), team_data.get('logo')))
    connIDX.commit()

    #get the ID here
    curIDX.execute('SELECT id FROM Teams WHERE id = ? LIMIT 1',(team_id,))
    row = curIDX.fetchone()
    if row is not None:
        teams[team_id] = row[0]
        return row[0]
    return None

def defineLeague(league_data):
    # Inserts or retrieves a league record
    if not league_data or 'id' not in league_data: return None

    league_id = league_data['id']
    league_name = league_data['name'].strip()

    if league_id in leagues:
        return leagues[league_id]
    
    # putting the league in here
    curIDX.execute('INSERT OR IGNORE INTO Leagues (id, league_name,type,logo_url) VALUES (?,?,?,?)', (league_id,league_name,league_data.get('type'),league_data.get('logo')))
    connIDX.commit()

    # FIX: Use curIDX to select the ID from the index database
    curIDX.execute('SELECT id FROM Leagues WHERE id = ? LIMIT 1', (league_id,)) 
    row = curIDX.fetchone()
    if row is not None:
        leagues[league_id] = row[0]
        return row[0]
    return None

# this here takes the raw data here and can make something happen with it
cur.execute('SELECT json_data FROM RawData WHERE endpoint = ?',('leagues',))
for row in cur:
    data = json.loads(row[0])
    if 'response' in data:
        for item in data['response']:
            # FIX: Use item directly (as confirmed in previous steps)
            defineLeague(item) 

# working with the raw games
cur.execute('SELECT json_data FROM RawData WHERE endpoint = ? ',('games',))

count = 0
for row in cur:
    raw_json = row[0]
    data = json.loads(raw_json) # This line should now work correctly, as the cursor is clean.

    if 'response' not in data: continue

    for item in data['response']:

        # making sure this is not an empty response
        if item.get('errors'): continue

        
        game_id = item.get('id')
        game_date = parsedate(item.get('date'))
        
        status = item.get('status', {}).get('long') 

        teams_data = item.get('teams')
        scores = item.get('scores')
        league_id = item.get('league',{}).get('id')

        
        if None in [game_id,league_id,teams_data,scores]: continue
        
        home_team_id = defineTeam(teams_data.get('home'))
        away_team_id = defineTeam(teams_data.get('away'))

        # if score key fails here(like it did beofre we shoudl probably use degfault value of 0)
        home_score = scores.get('home',0)
        away_score = scores.get('away',0)

        # again skip if the id fails to resolve
        if None in [home_team_id, away_team_id]: continue

        
        
        curIDX.execute('''INSERT OR IGNORE INTO Games (id, league_id, game_date, home_team_id, away_team_id, home_score, away_score, status, raw_json)
                    VALUES (?,?,?,?,?,?,?,?,?)''',(game_id,league_id,game_date,home_team_id,away_team_id,home_score,away_score,status, zlib.compress(raw_json.encode())))
        
        # zlib is used here to encode because the data can get quite big and its so the data deosnt get to big

        count+=1
        if count%50 == 0: connIDX.commit()
        if count% 250 == 0: print(f"Processed {count} games.")
        # this will only get the first 250 records and then the next to show that it is getting the data properly

connIDX.commit()
print(f"Modeling complete. Total games indexed: {count}. Data stored in the file")

cur.close()
conn.close()
curIDX.close()
connIDX.close()