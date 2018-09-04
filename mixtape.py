#!/usr/bin/env python3

# Copyright 2018 Bryant Durrell
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
# 
# 1. Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
# 
# 2. Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
# 
# 3. Neither the name of the copyright holder nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
# IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
# TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
# PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
# TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import argparse
import sqlite3
import requests
import random
import base64
import urllib
import json
import tweepy
from mastodon import Mastodon
from credentials import *

def getSpotifyToken(clientID, clientSecret, refreshToken):
	clientInfo = '{}:{}'.format(clientID, clientSecret)
	clientEncode = base64.b64encode(clientInfo.encode())
	reqHeader = {'Authorization': 'Basic {}'.format(clientEncode.decode())}
	reqBody = {'grant_type': 'refresh_token', 'refresh_token': refreshToken}
	r = requests.post('https://accounts.spotify.com/api/token', headers=reqHeader, data=reqBody)
	
	return r.json()['access_token']
	
def findSpotifySong(name, artist, spotifyToken):
	reqHeader = {'Authorization': 'Bearer {}'.format(spotifyToken)}
	reqArgs = {
		'q': 'track:"{}" artist:"{}"'.format(name, artist),
		'type': 'track',
		'market': 'us',
		'limit': '1'
	}
	r = requests.get('https://api.spotify.com/v1/search', params=reqArgs, headers=reqHeader)
	
	if r.status_code == 200:
		res = r.json()
		if len(res['tracks']['items']) > 0:
			return res['tracks']['items'][0]['uri']
		else:
			if artist.find(' With ') != -1:
				artist = artist.split(' With ')[0]
				songUri = findSpotifySong(name, artist, spotifyToken)
			elif artist.find(' Featuring ') != -1:
				artist = artist.split(' Featuring ')[0]
				songUri = findSpotifySong(name, artist, spotifyToken)
			else:
				return False
			
			return songUri
			
	else:
		return False
	
def getPlaylists(spotifyToken):
	reqHeader = {'Authorization': 'Bearer {}'.format(spotifyToken)}
	
def makePlaylist(spotifyToken, userID, name, songs):
	reqHeader = {'Authorization': 'Bearer {}'.format(spotifyToken)}
	reqBody = {'name': name}
	rCreate = requests.post('https://api.spotify.com/v1/users/{}/playlists'.format(userID), data=json.dumps(reqBody), headers=reqHeader)
	
	if rCreate.status_code == 200 or rCreate.status_code == 201:
		res = rCreate.json()
		
		reqArgs = {'uris': ','.join(songs)}
		rAdd = requests.post(
			'https://api.spotify.com/v1/users/{}/playlists/{}/tracks'.format(
				userID, res['id']
			), 
			headers=reqHeader, 
			params=reqArgs
		)
	
		if rAdd.status_code == 201:
			return res['external_urls']['spotify']

	return 0
	
def formatSong(song):
	return '"{}", {}'.format(song[2].replace('"', '\''), song[3])
 
def pickPosition(used, range):
	position = -1
	while (position == -1):
		position = random.randint(0, range-1)
		if (position in used):
			position = -1
	return position

def pickWeek(cursor, startYear, endYear):
	year = random.randint(startYear, endYear)
	week = random.randint(1, 52)

	weekID = cursor.execute('SELECT weekID FROM weeks WHERE week=? AND year=?', (week, year))

	return cursor.fetchone()[0]

def getSongList(cursor, mixWeek):
	songs = cursor.execute('SELECT week, weekPosition, song, performer FROM billboard WHERE week=? ORDER BY weekPosition', (mixWeek,))

	return cursor.fetchall()

def pickSongs(songList):
	mixtape = [random.randint(0, 4)]
	mixtape.append(pickPosition(mixtape, 10))
	mixtape.append(pickPosition(mixtape, 40))
	mixtape.append(pickPosition(mixtape, 40))
	mixtape.append(pickPosition(mixtape, 100))
	
	random.shuffle(mixtape)
	
	return mixtape
	
def makeText(emotion, mixWeek, mixtapeSongs, songList):
	output = 'It\'s {}/{}/{} and I {} you, so I made you a mixtape.\n'.format(mixWeek[5:7].lstrip('0'), mixWeek[8:10].lstrip('0'), mixWeek[0:4], emotion)

	for i in mixtapeSongs:
		output += '\n{}'.format(formatSong(songList[i]))
	
	return output

def pickEmotion():
	emotion = random.randint(1, 100)
	if (emotion <= 40):
		return "like"
	elif (emotion <= 65):
		return "miss"
	elif (emotion <= 90):
		return "love"
	elif (emotion <= 95):
		return "need"
	elif (emotion <= 99):
		return "want"
	else:
		return "hate"

def generate():
	parser = argparse.ArgumentParser(description='Mix tape tweetbot')
	parser.add_argument('--maxlen', default=255, type=int, help='Max tweet length')
	parser.add_argument('--db', required=True, help='Database location')
	parser.add_argument('--start', default=1980, type=int, help='Start year')
	parser.add_argument('--end', default=1989, type=int, help='End year')
	parser.add_argument('--print', help='Print mixtape', action='store_true')
	parser.add_argument('--tweet', help='Tweet mixtape', action='store_true')
	parser.add_argument('--toot', help='Toot mixtape', action='store_true')
	parser.add_argument('--spotify', help='Create a Spotify playlist', action='store_true')
	args = parser.parse_args()

	# Twitter URLs are 23 characters & we burn 2 characters on newlines
	# For reference, Mastodon URLs are the same (but are not shortened)	
	if args.spotify:
		args.maxlen -= 25

	conn = sqlite3.connect(args.db)
	c = conn.cursor()
	
	mixWeek = pickWeek(c, args.start, args.end)
	songList = getSongList(c, mixWeek)

	emotion = pickEmotion()

	text = None
	while (text is None or len(text) > args.maxlen):
		mixtapeSongs = pickSongs(songList)
		text = makeText(emotion, mixWeek, mixtapeSongs, songList)

	if args.spotify:
		spotifyToken = getSpotifyToken(spotify_client_id, spotify_client_secret, spotify_refresh_token)

		gotSongs = True
		songIDs = []
		for song in mixtapeSongs:
			spotID = findSpotifySong(songList[song][2], songList[song][3], spotifyToken)
			if spotID == False:
				gotSongs = False
			else:
				songIDs.append(findSpotifySong(songList[song][2], songList[song][3], spotifyToken))

		if gotSongs:
			playlistName = '{}/{}/{}'.format(mixWeek[5:7].lstrip('0'), mixWeek[8:10].lstrip('0'), mixWeek[0:4])
			spotifyURL = makePlaylist(spotifyToken, spotify_user_id, playlistName, songIDs)
		
		if not spotifyURL == 0:
			text += '\n\n{}'.format(spotifyURL)

	if args.print:
		print(text)
	if args.toot:
		mastodon = Mastodon(
			access_token=mastodon_access_token,
			api_base_url = 'https://botsin.space')
		mastodon.toot(text)
	if args.tweet:
		auth = tweepy.OAuthHandler(twitter_consumer_key, twitter_consumer_secret)
		auth.set_access_token(twitter_access_token, twitter_access_token_secret)
		api = tweepy.API(auth)
		api.update_status(text)
		
	conn.close()

if __name__ == '__main__':
	generate()

