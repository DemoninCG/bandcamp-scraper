import requests
from bs4 import BeautifulSoup
import os
import re
import json
import sys

def download_all_albums(artist_url):
    response = requests.get(artist_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all album elements
    albums = soup.find_all('li', class_='music-grid-item')
    #print(albums)

    for album in albums:
        album_url = album.find('a', href=True)['href']
        print(album_url)
        #album_title = album.find('p', class_='title').text.split('\n')[1].strip()
        album_title = album_url[7:]
        print(f"Processing album: {album_title}")
        download_bandcamp_tracks(artist_url + album_url, album_title)

    # Additional albums beyond the first 16 are in the "data-client-items" ol
    # Equivalent to a [data-client-items] CSS selector
    script_tag = soup.find("ol", {"data-client-items": True})
    if script_tag:
        # Get the data-client-items attribute
        data_tralbum = script_tag["data-client-items"]
        # Parse the JSON data
        albums2 = json.loads(data_tralbum)

        for album in albums2:
            #album_url = album.find('a', href=True)['href']
            album_url = album['page_url']
            print(album_url)
            #album_title = album.find('p', class_='title').text.split('\n')[1].strip()
            album_title = album_url[7:]
            print(f"Processing album: {album_title}")
            download_bandcamp_tracks(artist_url + album_url, album_title)

def download_bandcamp_tracks(url, album_title):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all track elements
    tracks = soup.find_all('tr', class_='track_row_view')

    for track in tracks:
        # Extract track title and URL
        title_element = track.find('span', class_='track-title')
        if title_element:
            title = title_element.text.strip()
            track_url = artist_url + track.find('a', href=True)['href']
            print(f"URL: {track_url}")

            print(f"Processing: {title}")

            download_bandcamp_track(track_url, album_title)
        else:
            print("Could not find title for a track, skipping...")

    print(f"All available tracks for '{album_title}' downloaded successfully!")

def download_bandcamp_track(url, album_title):
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Failed to access the page. Status code: {response.status_code}")
        return

    tralbum_data_match = re.search(r'data-tralbum="([^"]*)"', response.text)
    if not tralbum_data_match:
        print("Failed to find track data on the page.")
        return

    tralbum_data = json.loads(tralbum_data_match.group(1).replace("&quot;", '"'))

    track_info = tralbum_data['trackinfo'][0]
    track_title = track_info['title']
    track_url = track_info['file']['mp3-128']

    if not track_url:
        print("No downloadable track found.")
        return

    # Create album folder if it doesn't exist
    album_folder = os.path.join('albums', album_title)
    if not os.path.exists(album_folder):
        os.makedirs(album_folder)

    print(f"Downloading: {track_title}")
    track_response = requests.get(track_url)

    if track_response.status_code != 200:
        print(f"Failed to download the track. Status code: {track_response.status_code}")
        return

    filename = f"{track_title}.mp3"
    filename = "".join(c for c in filename if c.isalnum() or c in (' ', '.', '-', '_')).rstrip()
    filepath = os.path.join(album_folder, filename)

    with open(filepath, 'wb') as f:
        f.write(track_response.content)

    print(f"Downloaded: {filepath}")

# Usage
#artist_url = "https://genomrecords.bandcamp.com"
artist_url = sys.argv[1]
download_all_albums(artist_url)