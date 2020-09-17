Patricia Cornwell

    Flesh and Blood
    Flesh and Blood: A Scarpetta Novel (Scarpetta Novels Book 22)
    The Scarpetta Factor

David Baldacci

    Bullseye: Willl Robie / Camel Club Short Story
    The Camel Club
    The Christmas train
    The collectors
    Deliver Us From Evil
    Divine justice
    The Escape
    The Finisher
    First Family
    Hour Game
    Last Man Standing
    Saving Faith
    Simple Genius
    The Simple Truth
    Total Control
    True Blue
    The whole truth
    The winner
    Wish You Well




author_list =['cornwell', 'baldacci', 'patterson', 'grisham', 'koontz',
               'child', 'pierce', 'woods', 'wolfe', 'stelljes', 'connelly' ]
               
[x[0] for x in os.walk(dirs[0])]
b = os.path.getsize("/path/isa_005.mp3")

import os
import glob

author_list =['patricia cornwell', 'david baldacci', 'james patterson', 'john grisham', 'dean koontz',
               'lee child', 'blake pierce', 'stuart woods', 'leslie wolfe', 'roger stelljes',    
               'michael connelly','cornwell, patricia', 'baldacci, david', 'patterson, james', 
               'grisham, john', 'koontz, dean', 'child, lee', 'pierce, blake', 'woods, stuart', 
               'wolfe, leslie', 'stelljes, roger', 'connelly, michael' ]

glob_spec = '/home/frederika/Calibre Library/*/'
dirs = glob.glob(glob_spec)

found = {}
for dir in dirs:
   for root, drs, files in os.walk(dir):
      for name in files:
         if name.lower().find('.mobi') > -1 or name.lower().find('.epub') > -1:
            author = dir.lower().split('/')[-2]
            if author in author_list:
               if author not in found.keys():
                  found[author] = []
               found[author].append(name)
               print("book found in %s by %s: %s" % (dir, author, name))


for key in found.keys():
   print(" --- %s %s:" % (key.split(' ')[0].capitalize(), key.split(' ')[1].capitalize() ))
   for book in found[key]:
      print("  %s" % book)