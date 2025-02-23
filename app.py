from flask import Flask, render_template, redirect, request, jsonify
from datetime import datetime
import requests
from datetime import datetime
from dotenv import load_dotenv
from pymongo import MongoClient
from flask_cors import CORS  # Add this import


app = Flask(__name__) 
CORS(app) # to run on postman
CLIENT_ID = "15e2ce55d5e94dbb8bd11133b6b997c6"
CLIENT_SECRET = "7465ffc4c2e443648164b43b2bcada8d"

client = MongoClient("mongodb://localhost:27017")
db = client["time-capsule"]

# just using the spotify api
def get_spotify_token():
    url = "https://accounts.spotify.com/api/token"
    data = {"grant_type": "client_credentials"}
    auth = (CLIENT_ID, CLIENT_SECRET)
    response = requests.post(url, data=data, auth=auth)
    return response.json().get("access_token")
ACCESS_TOKEN = get_spotify_token()

@app.route("/")
def home():
    return render_template('index.html')

# spotify search stuff lols 
@app.route('/search', methods=["GET"]) 
def search_songs():  
    query = request.args.get("q")  
    if not query:  
        return jsonify({"Search something up!"}), 400 
    
    url = f"https://api.spotify.com/v1/search?q={query}&type=track&limit=5"   
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}   
    response = requests.get(url, headers=headers)   
    if response.status_code != 200:  
        return jsonify({"There was an error :( Try again!"}), response.status_code  
    songs = response.json()["tracks"]["items"]  
    results = [  
        {
            "song_name": song["name"],
            "artist": song["artists"][0]["name"],
            "album_art": song["album"]["images"][0]["url"],
            "spotify_url": song["external_urls"]["spotify"]
        }
        for song in songs
    ]
    
    return jsonify(results)

# create capsules method NEED TO FIX !!!! 
@app.route('/create_capsule', methods = ["POST"]) 
def create_capsule(): 
    data = request.json
    print("fu")
    if not data: # minor check rn delete later 
        return jsonify("No data received!")
    required_fields = ["capsule_title", "unlock_date"]
    if not all(field in data for field in required_fields): 
        return jsonify({"Missing required fields!"}), 400
    capsules_set = db["capsules"] # name of collection of capsules
    capsules_set.insert_one(data) # simply interesting data into set
    return jsonify({"Capsule created!"})


if __name__ == "__main__": 
    app.run(debug=True) 
