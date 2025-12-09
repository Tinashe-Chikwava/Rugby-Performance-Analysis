import sqlite3
import zlib
import sys
# basic imports for this file, what this does is going to hold the raw data to look at

def topTeamsByWins(cur,teams,howmany):
    #gets the top teams by wins across all leagues (finished)
    print('='*50)
    print(f'Top {howmany} Teams by Wins (Finished Games)')
    print('='*50)

    
    cur.execute('''SELECT home_team_id, away_team_id, home_score, away_score FROM Games WHERE status = 'Finished' ''')

    team_wins = {}

    for row in cur:
        
        home_id, away_id, home_score, away_score = row

        #sanity check that the scores are going to be integers
        if isinstance(home_score, int) and isinstance(away_score, int):
            if home_score > away_score:
                team_wins[home_id] = team_wins.get(home_id, 0) + 1
            elif away_score > home_score:
                team_wins[away_id] = team_wins.get(away_id, 0) + 1 
                
    x = sorted(team_wins,key = team_wins.get, reverse = True)
    for team_id in x[:howmany]:
        # checking if the team id does indeed exist
        if team_id is None: continue
        print(teams.get(team_id, f"Team ID {team_id}"), team_wins[team_id])
        if team_wins[team_id] < 1 : break
    print('\n')

def leaguesByGameCount(cur, leagues, howmany):
    #gets the top leagues and which ones play the most games
    print('='*50)
    print(f'Top {howmany} Leagues by Game Count')
    print('='*50)

    
    cur.execute('SELECT league_id, COUNT(id) FROM Games GROUP BY league_id ORDER BY COUNT(id) DESC LIMIT ?',(howmany,))
    for league_id, count in cur:
        print(leagues.get(league_id, f"League ID {league_id}"), count)
        if count < 1 : break
    print('\n') 

def topTeamsByTries(cur,teams,howmany):
    #this gets the top teams by how many tries they scored each

    print('='*50)
    print(f'Top {howmany} Teams by Total Tries Scored')
    print('='*50)

    cur.execute('SELECT home_team_id, away_team_id, home_score, away_score FROM Games')

    team_tries = {}

    for row in cur:
        home_id, away_id, home_score, away_score = row

     #sanity check once agin that the numbers are indeed integers
        if isinstance(home_score, int):
            team_tries[home_id] = team_tries.get(home_id, 0) + home_score
        
        if isinstance(away_score, int):
            team_tries[away_id] = team_tries.get(away_id, 0) + away_score 

    x = sorted(team_tries, key = team_tries.get, reverse = True)   
    for team_id in x[:howmany]:
        if team_id is None: continue 
        print(teams.get(team_id, f"Team ID {team_id}"), team_tries[team_id])
        if team_tries[team_id] < 1: break
    print('\n')

def topLargestScoreDifferenceGames(cur,teams,leagues,howmany):
    #gets the games with the largest margins

    print('='*50)
    print(f'Top {howmany} Games with the largest score margins')
    print('='*50)

    
    cur.execute('''SELECT league_id, home_team_id, away_team_id, home_score, away_score
                FROM Games WHERE status = 'Finished'
                AND home_score IS NOT NULL
                AND away_score IS NOT NULL
                ORDER BY ABS(home_score-away_score) DESC LIMIT ?''',
                (howmany,))
    
    for league_id, home_id,away_id, home_score, away_score in cur:
        difference = abs(home_score-away_score)
       
        league_name = leagues.get(league_id, f"League ID {league_id}") 
        home_name = teams.get(home_id, f"Team ID {home_id}")
        away_name = teams.get(away_id, f"Team ID {away_id}")

        print(f"[{league_name}] {home_name} {home_score} - {away_score} {away_name} (Difference: {difference})")
    
    print('\n')

if __name__ == '__main__':
    try:
        
        howmany = int(input("How many to dump: "))
    except ValueError:
        print("The input was invalid, try again with a proper number")
        sys.exit(1)

    conn = sqlite3.connect('rugby_index.sqlite')
    cur = conn.cursor()

    cur.execute('SELECT id, team_name FROM Teams')
   
    teams = {row[0]: row[1] for row in cur} 

    cur.execute('SELECT id, league_name FROM Leagues')
   
    leagues = {row[0]: row[1] for row in cur}

    topTeamsByWins(cur,teams,howmany)
    leaguesByGameCount(cur, leagues, howmany) 
    topTeamsByTries(cur,teams,howmany)
    topLargestScoreDifferenceGames(cur,teams,leagues,howmany) 

    cur.close()
    conn.close()