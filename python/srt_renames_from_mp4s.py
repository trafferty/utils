import os
import glob

seasons = [2, 3, 4, 5, 6, 7, 8]
for season in seasons:
    #p = '/home/trafferty/tmp_noback/syn_homes/militho/bt/archive/House_MD_mp4/Season%d/' % (season)
    p = '/run/user/1000/gvfs/smb-share:server=dns-323,share=volume_1-1/media/videos/tv/House_MD/House S%d'  % (season)
    print("For %s..." % (p))

    glob_mp4 = "%s/*.mp4" % (p)
    glob_srt = "%s/*.srt" % (p)
    mp4_files = sorted(glob.glob(glob_mp4))
    srt_files = sorted(glob.glob(glob_srt))
    print("  MP4 file count: %d" % (len(mp4_files)))
    print("  SRT file count: %d" % (len(mp4_files)))

    rename_list = []
    for mp4_file in mp4_files:
        srts_to_rename = []
        for srt_file in srt_files:
            if '%sx%s' % (season, os.path.basename(mp4_file)[0:2]) in srt_file:
                srts_to_rename.append(srt_file)
                #print(" > %s" % srt_file)

        rename_list.append([os.path.basename(mp4_file), srts_to_rename])

    for rename in rename_list:
        print("\n[Season %d] For: '%s'" % (season, rename[0]))
        for idx, srt_to_rename in enumerate(rename[1]):
            post = '' if idx == 0 else '_%d' % idx
            src =  os.path.basename(srt_to_rename)
            dst = '%s%s.srt' % (os.path.basename(rename[0][0:-4]), post)
            print("  '%s' -> '%s'" % (src, dst) )
            #print("  %s/%s > %s/%s" %  (p, src, p, dst) )
            os.rename("%s/%s" % (p, src), "%s/%s" % (p, dst) )



