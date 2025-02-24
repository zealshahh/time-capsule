from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
import requests 
from bson import ObjectId # store ids as object ID

app = Flask(__name__)
CLIENT_ID = "15e2ce55d5e94dbb8bd11133b6b997c6"
CLIENT_SECRET = "7465ffc4c2e443648164b43b2bcada8d"


client = MongoClient("mongodb://localhost:27017/")
db = client["capsules_collection"]
capsule_collection = db["capsules"]  # collection to store capsules


# just using the spotify api
def get_spotify_token():
    url = "https://accounts.spotify.com/api/token"
    data = {"grant_type": "client_credentials"}
    auth = (CLIENT_ID, CLIENT_SECRET)
    response = requests.post(url, data=data, auth=auth)
    return response.json().get("access_token")
ACCESS_TOKEN = get_spotify_token()

#home page 
@app.route("/")
def home():
    return render_template('index.html')

# spotify search page and method 
@app.route('/search_song', methods=["GET"]) # to run it http://127.0.0.1:5000/search_song?q=No_one_noticed
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

@app.route("/create_capsule", methods=["POST"])
def create_capsule():
    data = request.get_json()  # retrieves json data
    if not data: 
        return jsonify({"error: Create a capsule!"}), 400 
    required_fields = ["title", "unlock_date"] 
    if not all(field in data for field in required_fields): 
        return jsonify("Error: Missing required fields!") # fix this syntax later 
    inserted_id = capsule_collection.insert_one(data).inserted_id    
    return jsonify({"message": "Your capsule was saved!"}), 201  

# show all capsules  
@app.route('/my_capsules', methods = ["GET"])  
def user_capsules(): 
    user_id = request.args.get("user_id")
    if not user_id: # if user dne 
        return jsonify({"error": "Missing user ID!"}), 400 # just add a little 400 for error stuff
    
    capsule_collection = db["capsules"]
    user_capsules = list(capsule_collection.find({"user_id": user_id}, {"_id": 0}))  # return capsules and get rid of usual mongodb id  
    if not user_capsules:  # if user has no capsules yet 
        return jsonify({"message": "You have no capsules yet!"})
    return jsonify(user_capsules) # to run http://127.0.0.1:5000/my_capsules?user_id=xxx

@app.route('/delete_capsule/<capsule_id>', methods=["DELETE"])
def delete_capsule(capsule_id): 
    pass 

if __name__ == "__main__":
    app.run(debug=True)
