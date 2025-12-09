# Rugby-Performance-Analysis
RUGBY DATA PROCESSING PROJECT

This project is designed to retrieve, process, and visualize rugby statistics using the api-sports.io API. It follows a multi-stage data pipeline, similar to the email data project.

### Data Source
The primary data source is the Rugby API v1 (v1.rugby.api-sports.io). An API key is required and must be placed in the `api_key` variable in `rugby_spider.py`.

### Data Flow

1.  **spider.py**: Connects to the API, retrieves raw JSON data (starting with Leagues and then Games/Teams), and stores this raw data into the `raw_rugby_data.sqlite` database.
2.  **model.py**: Reads the raw data, cleans it, extracts key entities (Teams, Leagues, Games), and stores the normalized data into the `rugby_index.sqlite` database. It also handles data normalization, like consolidating team names and parsing dates.
3.  **dump.py**: A utility for querying the normalized `rugby_index.sqlite` database, allowing for quick inspection and debugging of the processed data (e.g., top teams by wins, games per league).
4.  **visualization.py**: (Placeholder for visualization scripts) Will generate data structures for D3.js to create web visualizations (line graphs, etc.).

### Data Structure (api-sports.io Entities)
The following entities are retrieved and modeled:
-   **Leagues**: Basic league information.
-   **Teams**: Team details.
-   **Games**: Match information, including scores and status.
-   **Standings**: League table information.


I was using the wromg key structure which lead to quite a lot of errors on the code
this was fixed with geminis help on the notifciation of using the wronmg key structure manually

this project heavily is inspired and borrws from Python For Everybody by Charles Severance in which I completed the code and was able to make this project


again the limitation of not using the last function for the free plan which made me alter the code again so that the table could be populated properly

code fucntions now propely and was able to get the raw data for the games properly

the data collected all of the fucntions from the data properly raw, it made many many api requests howver, it is advised to use a delay, i will have to do research on this part and see

the model had many issues with keys once again that were sorted out eventually

the dump has quite a few fucntions actually many that could be quite useful
had syntax functions for a while that were crashing so i ended up fixing and cleaning those up
the dump file is now working

we now moved onto the visualization file which i have chosen to just show the teams by tries scored per country
this is the most fun part and where I took the most help from online 
ist going to show Team performance and consistency
x-axis average tries scored per game
y-axis is the standard deviation of tries scored per game (indicating consistecy)

the json for the visualization file was caluclated successfully, need to do the html and d3 file so that it can show nicely

the visalization.py was written and cuntions as expected
the html and d3.json files were created with the help of artificial intelligence that was able to help me make the graph look nice