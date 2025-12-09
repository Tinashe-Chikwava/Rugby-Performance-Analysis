import sqlite3
import json
from collections import defaultdict #this file is goign to provide a good level of analysis that will be good to see
import math

file = 'Consistency.json'

def getTeamNames(cur):
    #gets all of the team names
    cur.execute('SELECT id, team_name FROM Teams')
    return {row[0]: row[1] for row in cur}

def calculateConsistency():
    # here this calculates average tries and the standard deviation of those tries

    conn = sqlite3.connect('rugby_index.sqlite')
    cur = conn.cursor()

    team_names = getTeamNames(cur)
    team_scores = defaultdict(list)

    # getting all of the scores here for each team
    cur.execute('''SELECT home_team_id, away_team_id, home_score, away_score
                FROM Games WHERE status = 'Finished' ''')
    
    for home_id, away_id, home_score, away_score in cur:
        try:
            home_score = int(home_score)
            away_score = int(away_score)
        except (ValueError, TypeError):
            continue # goes through the invalid games to not kill the process

        team_scores[home_id].append(home_score)
        team_scores[away_id].append(away_score)

    cur.close()
    conn.close()

    data = []
    # here we do the calculations

    for team_id, scores in team_scores.items():
        if len(scores) < 3: # makes sure they have to play at the very least three games in the seaon
            continue

        team_name = team_names.get(team_id, f"Unknown Team ID {team_id}")

        # average
        avg = sum(scores) / len(scores)

        # standard deviation 
        # Calculates the variance
        variance = sum((x - avg) ** 2 for x in scores) / len(scores)

        standardDeviation = math.sqrt(variance)

        data.append({
            "team_name": team_name,
            "games_played": len(scores),
            "avg_tries": round(avg, 2), # ultimately becomes the x axis (performance wise)
            "standard_deviation": round(standardDeviation, 2) # ultimately becomes the y xis (consistency)
        })
    
    return data 

def saveData(data):
    #writes this data onto a json file
    try:
        with open(file,'w') as f:
            json.dump(data,f,indent = 4)
        print(f"Datat writing success {len(data)} team records to {file}")
    except Exception as e:
        print(f"There was some major error writing to the file: {e}")

if __name__ == '__main__':
    print("Starting the visualization")

    consistency_data = calculateConsistency()

    if consistency_data:
        saveData(consistency_data)
    else:
        print("No consistenty data is generated her , check the main file for errors")
