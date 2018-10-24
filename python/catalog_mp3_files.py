
import glob
import os
from mutagen.easyid3 import EasyID3

root_dir = '/Volumes/SANDISK_32'

glob_spec = "%s/**/*.mp3" % (root_dir)
#glob_spec = "%s/*.mp3" % (root_dir)
mp3_file_paths = sorted(glob.glob(glob_spec))

print(" ******** Searching %d MP3 files: " % (len(mp3_file_paths)))

MP3_artist_dict = {}
for mp3_file_path in mp3_file_paths:
    try:
        tags = EasyID3(mp3_file_path)
    except Exception as e:
        print(">> Exception while reading MP3 file: %s" % (mp3_file_path))

    try:
        artist_lst = tags['artist']
    except Exception as e:
        print(">> Error reading artist tag from MP3 file: %s" % (mp3_file_path))

    for artist in artist_lst:
        MP3_artist_dict[artist] = MP3_artist_dict.get(artist, 0) + 1

print("\nSearch complete. Found %d unique artists" % (len(MP3_artist_dict)))

for artist, cnt in sorted(MP3_artist_dict.items()):
    print("%30s: %d" % (artist, cnt))
