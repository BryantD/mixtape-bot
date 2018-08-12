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
import random
import tweepy
from mastodon import Mastodon
from credentials import *

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

def makeText(emotion, week, songList):
	output = 'It\'s {}/{}/{} and I {} you, so I made you a mixtape.\n'.format(week[5:7].lstrip('0'), week[8:10].lstrip('0'), week[0:4], emotion)

	mixtape = [random.randint(0, 4)]
	mixtape.append(pickPosition(mixtape, 10))
	mixtape.append(pickPosition(mixtape, 40))
	mixtape.append(pickPosition(mixtape, 40))
	mixtape.append(pickPosition(mixtape, 100))
	
	random.shuffle(mixtape)

	for i in mixtape:
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
	parser.add_argument('--maxlen', default=280, type=int, help='Max tweet length')
	parser.add_argument('--db', required=True, help='Database location')
	parser.add_argument('--start', default=1980, type=int, help='Start year')
	parser.add_argument('--end', default=1989, type=int, help='End year')
	parser.add_argument('--print', help='Print mixtape', action='store_true')
	parser.add_argument('--tweet', help='Tweet mixtape', action='store_true')
	parser.add_argument('--toot', help='Toot mixtape', action='store_true')
	args = parser.parse_args()

	conn = sqlite3.connect(args.db)
	c = conn.cursor()

	mixWeek = pickWeek(c, args.start, args.end)
	songList = getSongList(c, mixWeek)

	emotion = pickEmotion()

	text = None
	while (text is None or len(text) > args.maxlen):
		text = makeText(emotion, mixWeek, songList)

	if args.print:
		print(text)
	if args.toot:
		mastodon = Mastodon(
			access_token=mastodon_access_token,
			api_base_url = 'https://botsin.space')
		mastodon.toot(text)
	if args.tweet:
		api.update_status(text)
		
	conn.close()

if __name__ == '__main__':
    generate()

