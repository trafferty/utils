#!/Library/Frameworks/Python.framework/Versions/Current/bin/python
import os
from os.path import join, getsize

def addEntry (XMLFile, videosDir, finfo, dirs, NASPath):
    #finfo[1].replace(' ', '_')
    finfo[1] = finfo[1].replace('.', '_', finfo.count('.')-1)
    title = finfo[1].split('.')[0]
    
    root = ''
    genre = 'Tom and Frederika'
    pathlist = finfo[0].split('/')
    
    if 0:
        for pathchunk in pathlist:
            for dirname in dirs:
                if pathchunk == dirname:
                    genre = dirname
    else:
        locs = finfo[0][len(videosDir)+1:]
        if len(locs) > 0:
            if locs.find('/') >= 0:
                genre = "[%s]" % (locs)
            else:
                genre = "%s" % (locs)
        print("finfo: %s, locs: %s, genre: %s" % (finfo[0], locs, genre))        
            
    imageRoot = ''
    for pathchunk in pathlist:
        if pathchunk.find('videos') == -1:
            imageRoot = imageRoot + pathchunk + '/'
        else:
            imageRoot = imageRoot + 'videos/images/'
            break
    
    imageFile = imageRoot + title + '.jpg'
    if os.path.exists(imageFile):
        imageFile = 'images/' +  title + '.jpg'
    else:
        imageFile = 'images/na.jpg'
        
    XMLFile.write("<movie>\n")
    XMLFile.write("<num>" + str(finfo[2]) + "</num>\n")
    XMLFile.write("<origtitle>" + title + "</origtitle>\n")
    XMLFile.write("<year>2009</year>\n")
    XMLFile.write("<genre>" + genre + "</genre>\n")
    XMLFile.write("<mpaa>Rated G</mpaa>\n")
    XMLFile.write("<director></director>\n")
    XMLFile.write("<actors></actors>\n")
    XMLFile.write("<description></description>\n")
    XMLFile.write("<path>" + NASPath + "</path>\n")
    XMLFile.write("<length>110</length>\n")
    XMLFile.write("<videocodec>MP4</videocodec>\n")
    XMLFile.write("<poster>" + imageFile + "</poster>\n")
    XMLFile.write("</movie>\n\n")
#------ End of addEntry

videosDir        = '/Volumes/Volume_1-1/media/videos'
#videosDir        = './videos'
videoXMLFileName = videosDir + '/videos.xml'
NASRoot = "Y:\\media\\videos\\"

allfiles = []
allDirs = []

print 'Reading in files from ' + videosDir;
for root, dirs, files in os.walk(videosDir):
    for dirname in dirs:
        allDirs.append(dirname)
    for idx, file_name in enumerate(files):
        if (file_name.find('mp4') > -1 or file_name.find('MP4') > -1) and file_name.find('._') == -1:
            allfiles.append([root, file_name, idx])

videoXMLFile = open(videoXMLFileName, 'w')
videoXMLFile.write("<xml>\n")
videoXMLFile.write("<viddb>\n")
videoXMLFile.write("<movies>" + str(len(allfiles)) +"</movies>\n\n")

print '...read in ' + str(len(allfiles) + 1) + ' files'
print 'Building XML media file at ' + videoXMLFileName

for finfo in allfiles:
    pathlist = finfo[0].split('/')
    NASPath = NASRoot
    for pathchunk in pathlist[5:]:
        NASPath = NASPath + pathchunk + "\\"
    NASPath = NASPath + finfo[1]
    #print NASPath + " - " + finfo[0] + "/" + finfo[1]
    addEntry (videoXMLFile, videosDir, finfo, allDirs, NASPath)

videoXMLFile.write("</viddb>\n")
videoXMLFile.write("</xml>\n")  
videoXMLFile.close()

print 'Built XML media file for ' + str(len(allfiles) + 1) + ' movies'
