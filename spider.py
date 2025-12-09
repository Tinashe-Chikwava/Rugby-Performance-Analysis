import sqlite3
import time
import ssl
import json
import urllib.parse
import requests 

# basic setting up here
key = 'xxxxxxxxxxxxxxxxxxxx' 
baseurl = "https://v1.rugby.api-sports.io"

# taking care of ssl errors (only necessary if using urllib, but harmless here)
ctx = ssl.create_default_context()
ctx.check_hostname = False 
ctx.verify_mode = ssl.CERT_NONE

# connections here 
conn = sqlite3.connect('raw_data.sqlite')
cur = conn.cursor()

# tables for storing data here
cur.execute('''CREATE TABLE IF NOT EXISTS RawData (endpoint TEXT, parameters TEXT, json_data TEXT)''')
cur.execute('''CREATE TABLE IF NOT EXISTS Leagues (id INTEGER UNIQUE, name TEXT)''')
cur.execute('''CREATE TABLE IF NOT EXISTS Games (id INTEGER UNIQUE, league_id INTEGER, game_date TEXT)''')

# fucntions here

def gettingData(endpoint, params=None):
    # FIX 1: Correct URL construction using f-string
    url = f"{baseurl}/{endpoint}" 
    headers = {'x-apisports-key': key}

    # parameters inside a JSON string so that the database key can access
    parameters = json.dumps(params if params else {}, sort_keys=True)

    # this here checks if the data is already present
    cur.execute('''SELECT json_data FROM RawData WHERE endpoint = ? AND parameters = ?''', (endpoint, parameters))
    try:
        row = cur.fetchone()
        if row is not None:
            print(f"** Cached: {endpoint} with {parameters}")
            return row[0]
    except Exception as e:
        # A specific error is better than a bare 'except'
        print(f"Database read error: {e}")
        pass

    # if it wasn't already present, collect the data
    try:
        print(f"Retrieving: {endpoint} with {parameters}")
        
        # FIX 2: Correct typo 'timout' -> 'timeout' and 'resposne' -> 'response'
        response = requests.get(url, headers=headers, params=params, timeout=30)
         
        # this ensures that we get a good response from the server
        if response.status_code != 200:
            print(f"Error code= {response.status_code}, URL = {url}")
            return None
        
        raw_data = response.text

        # FIX 4: Pass parameters as a single tuple
        cur.execute('''INSERT INTO RawData (endpoint,parameters,json_data) VALUES (?,?,?)''', (endpoint, parameters, raw_data))
        conn.commit()
        return raw_data
    
    # FIX 3: Correct typo 'execptions' -> 'exceptions'
    except requests.exceptions.RequestException as e:
        print(f"Unable to retrieve or parse the page {url}")
        print("Error: ", e)
        return None
    
def proccessLeague():
    # 1. Request the working 2022 season (and use lowercase endpoint)
    # The cache shows 2024 failed, but 2022 succeeded.
    leagues_data = gettingData("leagues", {"season": 2022})

    if leagues_data is None:
        print("The leagues data returned as none")
        return []
    
    data = json.loads(leagues_data)
    league_ids = []

    if data and 'response' in data:
        for item in data['response']:
            # 2. FIX: Access id and name directly from 'item'
            league_id = item.get('id')
            league_name = item.get('name')

            # Ensure we have the necessary data before inserting
            if league_id is not None and league_name is not None:
                cur.execute(''' INSERT OR IGNORE INTO Leagues (id,name) VALUES (?,?)''', (league_id, league_name))
                league_ids.append(league_id)
            else:
                print(f"Skipping malformed league item: {item}")


        conn.commit()
        print(f"Successfully inserted {len(league_ids)} leagues for 2022.")
        return league_ids
    return []

def processGame(league_ids):
    count = 0
    for league_id in league_ids:
        # Note: assuming the function gettingData is correctly used
        games_data = gettingData("games", {"league": league_id, "season": 2022})

        if games_data is None: continue

        data = json.loads(games_data)
        if data and 'response' in data:
            for item in data['response']:
                # FIX: Access id and date directly from 'item'
                game_id = item.get('id')
                game_date = item.get('date')

                if game_id is not None and game_date is not None:
                    # Note: We must insert the league_id from the loop variable
                    cur.execute('''INSERT OR IGNORE INTO Games (id,league_id,game_date) VALUES (?,?,?)''', 
                                (game_id, league_id, game_date))
                    count+=1

                    # commit for every 10 cycles
                    if count % 10 == 0: conn.commit()
            conn.commit()
            
    print(f"Inserted {count} total new games.")

# running the code here

print("Starting Spider...")
league_ids = proccessLeague()
print(f"Found {len(league_ids)} leagues.")
processGame(league_ids)
print("Spider crawl complete. Data stored")

cur.close()
conn.close()