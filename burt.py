import sys
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pickle
from threading import Thread

# Variable definitions ------------------------------------------------------ #

# Verify input
if len(sys.argv) == 1:
    print("Error! No playlist link provided.")
    quit()

elif len(sys.argv) > 2:
    print("Error! Too many options given.")
    quit()

# Configure spotify client
cfg = open('client.cfg','rb')
client_credentials = SpotifyClientCredentials(**pickle.load(cfg))
cfg.close()
spotify = spotipy.Spotify(client_credentials_manager=client_credentials)

# Parse user input and get initial playlist tracks
user_id, _, playlist_id = sys.argv[1].split('/')[4:7]
playlist = spotify.user_playlist(user_id, playlist_id)

# --------------------------------------------------------------------------- #


# Function definitions ------------------------------------------------------ #

def var(feature0, feature1):
    return abs(feature0 - feature1)/(feature0+0.00001)*100 < 10

def recommended_tracks(related_artist, base_track):
    """Scan all artist tracks and return those with similar features to the
       base_track. artist_uri is the artist's spotify URI, and base_track is
       the dictionary of features returned by the audio_features request"""

    # Get all albums
    albums = [album['uri'] for album in
              spotify.artist_albums(related_artist)['items']]


    recommended_tracks = []
    for album in albums:

        # Get the audio features for all tracks on album
        tracks = [t['uri'] for t in spotify.album_tracks(album)['items']][:20]
        album_tracks_features = spotify.audio_features(tracks)

        # For each track, examine audio features. If all are within 10% range
        # of the base_track, recommend that song (add to list of URLs)
        for track in album_tracks_features:

            if track is None:
                continue
            if (
               var(track['danceability'], base_track['danceability']) and
               var(track['energy'],       base_track['energy']      ) and
               var(track['speechiness'],  base_track['speechiness'] ) and
               var(track['liveness'],     base_track['liveness']    ) and
               var(track['valence'],      base_track['valence']     )
               ):
                recommended_tracks += ['https://open.spotify.com/track/' + track['id']]

    return recommended_tracks

# ---------------------------------------------------------------------------- #

# Main script ---------------------------------------------------------------- #

# Get all tracks in user playlist
for track in playlist['tracks']['items']:

    track = track['track']

    # Get spotify artist URI and audio features for that track
    artist_uri = track['artists'][0]['uri']
    track_audio_features = spotify.audio_features(track['uri'])[0]

    # Look at all related artists' discography
    # Recommend songs with similar characteristics
    scanning = '%s: %s...' % (track['artists'][0]['name'], track['name'])
    related_artists = spotify.artist_related_artists(artist_uri)['artists']
    recommended = []
    for i, related_artist in enumerate(related_artists):

        # Recommend songs, Show status
        print(f'{scanning} {100*i/len(related_artists)}%',  end='\r')
        recommended += recommended_tracks(related_artist['uri'], 
                                          track_audio_features)

    print(f'{scanning} 100.0%')
    print(recommended)
    print()
