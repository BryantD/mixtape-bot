Bot script to generate five song mix tapes based on the Billboard Top 100 for a 
given year. By default, it draws on the 1980s. 

Currently sending output to  [https://botsin.space/@scratchytdk](https://botsin.space/@scratchytdk) and [https://twitter.com/30minutemix](https://twitter.com/30minutemix). 

To do:
* Lots of code cleanup

Stuff I used:
* The profile image on the bot's Mastodon accounts is by Andrey Korzun [CC BY-SA 4.0] (https://creativecommons.org/licenses/by-sa/4.0), from [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Compact_Cassette_-_TDK_SA_60.JPG)
* The profile images on the bot's Twitter account are licensed as [CC0 1.0 Public Domain](https://creativecommons.org/publicdomain/zero/1.0/) and are from:
	* [https://www.publicdomainpictures.net/en/view-image.php?image=189929&picture=sixteen-audio-cassettes](https://www.publicdomainpictures.net/en/view-image.php?image=189929&picture=sixteen-audio-cassettes)
	* [https://www.maxpixel.net/Cassette-Band-Magnetband-Analog-Tape-Sound-Music-2979721](https://www.maxpixel.net/Cassette-Band-Magnetband-Analog-Tape-Sound-Music-2979721)
* The data set is [Billboard Hot 100 1958-2017](https://data.world/kcmillersean/billboard-hot-100-1958-2017), from Sean Miller
* [Tweepy](http://www.tweepy.org), which is nice and simple
* [Mastodon.py](http://mastodonpy.readthedocs.io/en/latest/), which is also pretty simple
* Code and inspiration for handling the Spotify API from [https://github.com/mileshenrichs/spotify-playlist-generator](https://github.com/mileshenrichs/spotify-playlist-generator)