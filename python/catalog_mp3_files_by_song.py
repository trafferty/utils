
import glob
import os
from mutagen.easyid3 import EasyID3

root_dir = '/Volumes/SANDISK_32'
root_dir = '/Volumes/homes/trafferty/rip'

glob_spec = "%s/**/*.mp3" % (root_dir)
#glob_spec = "%s/*.mp3" % (root_dir)
mp3_file_paths = sorted(glob.glob(glob_spec))

print(" ******** Searching %d MP3 files: " % (len(mp3_file_paths)))

MP3_song_dict = {}
for mp3_file_path in mp3_file_paths:
    try:
        tags = EasyID3(mp3_file_path)
    except Exception as e:
        print(">> Exception while reading MP3 file: %s" % (mp3_file_path))

    try:
        artist_lst = tags['artist']
    except Exception as e:
        print(">> Error reading artist tag from MP3 file: %s" % (mp3_file_path))

    try:
        title_lst = tags['title']
    except Exception as e:
        print(">> Error reading title tag from MP3 file: %s" % (mp3_file_path))

    song = f"{artist_lst[0]} : {title_lst[0]}"

    MP3_song_dict[song] = MP3_song_dict.get(song, 0) + 1

print("\nSearch complete. Found %d unique songs" % (len(MP3_song_dict)))

song_freq = {}

for song, cnt in sorted(MP3_song_dict.items(), key=lambda kv: kv[1]):
    song_freq[cnt] = song_freq.get(cnt, 0) + 1
    print("%70s: %d" % (song, cnt))

print("--------------------------------------------------------------")
for freq, cnt in sorted(song_freq.items()):
    print("songs played %02d time(s): %d" % (freq, cnt))
