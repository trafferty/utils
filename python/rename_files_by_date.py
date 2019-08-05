
import glob
import os

root_dir = '/Volumes/homes/trafferty/rip/RP0_no_indexes'

#glob_spec = "%s/**/*.mp3" % (root_dir)
glob_spec = "%s/*.mp3" % (root_dir)
mp3_file_paths = glob.glob(glob_spec)

print(" ******** Searching %d MP3 files: " % (len(mp3_file_paths)))

MP3_song_dict = {}
for mp3_file_path in mp3_file_paths:
    MP3_song_dict[os.path.getmtime(mp3_file_path)] = mp3_file_path

print("\nSearch complete. Found %d unique songs" % (len(MP3_song_dict)))


print("--------------------------------------------------------------")
prev_timestamp = None
cnt = 0
for timestamp, song in sorted(MP3_song_dict.items()):
    if prev_timestamp is not None:
        delta = timestamp - prev_timestamp

        if delta < 0:
            print("!!!!!!!!!!!!!!!!! Delta is negative! %d: %s" % (delta, os.path.basename(song)))
            print("  timestamp     : %f" % (timestamp))
            print("  Prev timestamp: %f" % (prev_timestamp))
        else:
            path, fname = os.path.split(song)
            new_path = "%s/%04d_%s" % (path, cnt, fname)
            cnt += 1
            print("%4d: %s" % (delta, new_path))
            os.rename(song, new_path)
    prev_timestamp = timestamp
