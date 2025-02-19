import requests
import sqlite3
import datetime
from flask import Flask, render_template
from bs4 import BeautifulSoup

app = Flask(__name__)

DB_FILE = "trump_mentions.db"

# Function to scrape SMH and count "Trump" mentions
def count_trump_mentions():
    url = "https://www.smh.com.au"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return 0  # Return 0 mentions if website is unreachable
    
    soup = BeautifulSoup(response.text, "html.parser")
    text = soup.get_text().lower()
    
    return text.count("trump")

# Function to store highest mention counts in the last 24 hours
def update_mention_history(mention_count):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Create table if it doesn’t exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mentions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            count INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Insert new count
    cursor.execute("INSERT INTO mentions (count) VALUES (?)", (mention_count,))
    
    # Delete records older than 24 hours
    cursor.execute("DELETE FROM mentions WHERE timestamp <= datetime('now', '-1 day')")
    
    conn.commit()
    conn.close()

# Function to get the highest mentions in the last 24 hours
def get_top_mentions():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute("SELECT count, timestamp FROM mentions ORDER BY count DESC LIMIT 10")
    top_mentions = cursor.fetchall()
    
    conn.close()
    return top_mentions

@app.route("/")
def index():
    mention_count = count_trump_mentions()
    update_mention_history(mention_count)
    top_mentions = get_top_mentions()
    
    return render_template("index.html", mention_count=mention_count, top_mentions=top_mentions)

if __name__ == "__main__":
    app.run(debug=True)
