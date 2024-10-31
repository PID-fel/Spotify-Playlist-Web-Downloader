from spotipy import *
from constants import *
import urllib.request
import spotipy
import requests
import json
import re
import subprocess
import os

def create_valid_filename(string):
    if string is None:
        string = "none"
    # Replace non-ASCII characters with underscores
    string = re.sub(r'[^\x00-\x7F]', '_', string)
    # Replace other invalid characters with underscores
    filename = re.sub(r'[^\w\s-]', '_', string)
    # Remove leading and trailing spaces
    filename = filename.strip()
    # Replace spaces with underscores
    filename = filename.replace(' ', '_')
    # Truncate to maximum length
    filename = filename[:255]
    # Return the valid filename
    return filename

scope = 'playlist-read-private'

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID,
                                               client_secret=CLIENT_SECRET,
                                               redirect_uri=AUTH_URL,
                                               scope=scope))


playlists = sp.current_user_playlists()


playlistInfo = []
playlistTracks = None

index = 0
for playlist in playlists['items']:
    tracks = []

    playlistTracks = sp.playlist_tracks(playlist['id'])
    for track in playlistTracks['items']:
        tracks.insert(len(tracks), [create_valid_filename(track['track']['name']), create_valid_filename(track['track']['artists'][0]['name']), track['track']['id']])

    playlistInfo.insert( index, [playlist['id'], create_valid_filename(playlist['name']), create_valid_filename(playlist['description']), playlist['images'][0]['url'], tracks ])

    index =+ 1


out_file = open("Playlist_JSON_Dump.json", "w")  
    
json.dump(playlistTracks, out_file, indent = 6)  
    
out_file.close()  

folders = next(os.walk('.'))[1]

if not os.path.exists("playlists"):
    os.makedirs("playlists")

for playlist in playlistInfo:

    folderNames = next(os.walk('./playlists'))[1]

    playlistFolderExists = False

    for folderName in folderNames:
        if folderName.split("-")[-1] == playlist[0]:
            playlistFolderExists = True
        
    if not (playlistFolderExists):
        os.makedirs('./playlists/' + playlist[1] + "-" + playlist[2] + "-" + playlist[0])

    undownloadedSongs = []

    for track in playlist[-1]:

        filePath = './playlists/' + playlist[1] + "-" + playlist[2] + "-" + playlist[0]
        
        fileNames = os.listdir(filePath)

        fileExists = False
        searchTerm = track[0] + "_" +  track[1] + "_full_song"

        for fileName in fileNames:
            if (fileName.split("-")[-1].split(".")[0] == track[-1]):
                fileExists = True


        if not fileExists:
            undownloadedSongs.append(searchTerm)

            fileNameWouldToSave = filePath + '/' + track[0] + "-" +  track[1] + "-" +  track[2] + ".mp3"
            
            try:
                searchTerm = track[0] + "_" +  track[1] + "_full_song"

                html = urllib.request.urlopen("https://www.youtube.com/results?search_query=" + searchTerm)
                video_id = None

                video_id = (re.findall(r"watch\?v=(\S{11})", html.read().decode()))[0]
            except:
                try:
                    searchTerm = track[0] + "_" +  track[1] 

                    html = urllib.request.urlopen("https://www.youtube.com/results?search_query=" + searchTerm)
                    video_id = None
                    video_id = (re.findall(r"watch\?v=(\S{11})", html.read().decode()))[0]
                except:
                    print("no available audio for: " + searchTerm)
                
            if video_id != None:
                videoLink = "https://www.youtube.com/watch?v=" + video_id
                output_path =  fileNameWouldToSave
                subprocess.run(["yt-dlp", "-f", "bestaudio", "--extract-audio", "--audio-format", "mp3", "-o", output_path, videoLink], stderr=subprocess.DEVNULL)
                print(searchTerm + " succesfully downloaded")

    for c in undownloadedSongs:
        print(c + " " + playlist[1])

    thumbNailExists = False
    for fileName in fileNames:
        if (fileName == "_thumbnail"):
            thumbNailExists = True

    if not thumbNailExists:
        
        img_data = requests.get(playlist[3]).content
        with open('./playlists/' + playlist[1] + "-" + playlist[2] + "-" + playlist[0] + '/_thumbnail.jpg', 'wb') as handler:
            handler.write(img_data)