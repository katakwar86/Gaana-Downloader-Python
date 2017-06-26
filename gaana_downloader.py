# Gaana Downloader to download songs from gaana.com website
# Coded by Arun Kumar Shreevastava
# 26 June 2017

from Crypto.Cipher import AES
import requests
import re
import sys
import os
from json import JSONDecoder

import m3u8

unpad = lambda s : s[0:-ord(s[-1])]
REGEX = re.compile('> ({[^<]*}) <')
JSONDEC = JSONDecoder()


def decryptLink(message):
    KEY = 'g@1n!(f1#r.0$)&%'
    IV = 'asd!@#!@#@!12312'
    aes = AES.new(KEY, AES.MODE_CBC, IV)
    return unpad(aes.decrypt(message.decode('base64')))


def downloadAndParsePage(link):
    response = requests.get(link).text
    raw_songs = list(set(REGEX.findall(response)))
    songs = []
    for raw_song in raw_songs:
        json_song = JSONDEC.decode(raw_song)
        enc_message = None
        if 'high' in json_song['path']:
            enc_message = json_song['path']['high'][0]
        elif 'medium' in json_song['path']:
            enc_message = json_song['path']['medium'][0]
        elif 'normal' in json_song['path']:
            enc_message = json_song['path']['normal'][0]
        else:
            enc_message = json_song['path']['auto'][0]

        song = {'title' : json_song['title'].decode('utf-8'),
                'album' : json_song['albumtitle'].decode('utf-8'),
                'bitrate' : enc_message['bitRate'],
                'link' : decryptLink(enc_message['message'])
        }
        songs.append(song)
    return songs


def downloadSong(song):
    filename = '%s-%s.m4a' % (song['album'], song['title'])
    if os.path.isfile(filename):
        print 'Skipping %s file already exists!',filename
        return
    with requests.Session() as s:
        r = s.get(song['link'])
        m = m3u8.loads(r.text)
        if m.is_variant:
            playlist = m.playlists[0]
            print 'Bandwidth: %d Codecs: %s' % (playlist.stream_info.bandwidth, playlist.stream_info.codecs)
            r = s.get(playlist.uri)

            m3u8_obj = m3u8.loads(r.text)

            with open(filename, 'wb') as f:
                for segment in m3u8_obj.segments:
                    req = s.get(segment.uri, stream=True)
                    for chunk in req.iter_content(chunk_size=1024): 
                        if chunk:
                            f.write(chunk)
            print 'Downloaded ',filename
        else:
            print 'Share the link with dev to look into the error'


def main():
    print '''
    \033[31m
   _____                           _____                      _                 _           
  / ____|                         |  __ \                    | |               | |          
 | |  __  __ _  __ _ _ __   __ _  | |  | | _____      ___ __ | | ___   __ _  __| | ___ _ __ 
 | | |_ |/ _` |/ _` | '_ \ / _` | | |  | |/ _ \ \ /\ / / '_ \| |/ _ \ / _` |/ _` |/ _ \ '__|
 | |__| | (_| | (_| | | | | (_| | | |__| | (_) \ V  V /| | | | | (_) | (_| | (_| |  __/ |   
  \_____|\__,_|\__,_|_| |_|\__,_| |_____/ \___/ \_/\_/ |_| |_|_|\___/ \__,_|\__,_|\___|_|   
                                                                                            
                                                            \033[0m\033[92mBy Arun Kumar Shreevastava\033[0m

'''
    input_url = raw_input('Enter the song/album url:').strip()
    try:
        songs = downloadAndParsePage(input_url)
    except:
        print 'Error', sys.exc_info()[0]
        return
    for i in range(len(songs)):
        print i, '%s-%s' % (songs[i]['album'], songs[i]['title'])
    song_nos = map(int, raw_input('Enter song numbers separated by space, -1 to download all songs:').split())
    if -1 in song_nos:
        for song in songs:
            downloadSong(song)
    else:
        for i in set(song_nos):
            if i < len(songs):
                downloadSong(songs[i])


if __name__ == '__main__':
    main()