
import glob
import os
from mutagen.easyid3 import EasyID3

root_dir = '/Volumes/SANDISK_32'
artist_to_remove_lst = ['Bob Dylan']

glob_spec = "%s/**/*.mp3" % (root_dir)
#glob_spec = "%s/*.mp3" % (root_dir)
mp3_file_paths = sorted(glob.glob(glob_spec))

print(" ******** Searching %d MP3 files for the following artistS to remove: " % (len(mp3_file_paths)))
print(artist_to_remove_lst)

MP3s_to_remove_list = []
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
        for artist_to_remove in artist_to_remove_lst:
            if artist.lower() == artist_to_remove.lower():
                print('***** Found song to remove:', mp3_file_path)
                MP3s_to_remove_list.append(mp3_file_path)

print("Search complete. Found %d songs to remove" % (len(MP3s_to_remove_list)))
print(MP3s_to_remove_list)

for MP3_to_remove in MP3s_to_remove_list:
    print("Removing:", MP3_to_remove)
    os.remove(MP3_to_remove)