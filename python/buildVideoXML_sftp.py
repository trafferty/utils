#!/Library/Frameworks/Python.framework/Versions/Current/bin/python
import os
from os.path import join, getsize, split
from random import randint
import pysftp   #conda install pysftp
import argparse
from getpass import getpass

def addEntry (XMLFile, finfo, dirs, NASPath):
    #finfo[1].replace(' ', '_')
    finfo[1] = finfo[1].replace('.', '_', finfo.count('.')-1)
    title = finfo[1].split('.')[0]
    
    root = ''
    genre = 'Tom and Frederika'
    pathlist = finfo[0].split('/')
    for pathchunk in pathlist:
        for dirname in dirs:
            if pathchunk == dirname:
                genre = dirname
            
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
        imageFile = 'images/FAM%d.jpg' % randint(1,278)
        
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

if __name__ == '__main__':
    NAS_pw = getpass("Enter NAS pw: ")
    NAS_hostname='192.168.129.142'
    NAS_user='traff_ss'
    NAS_root='media/videos'

    videoXMLFileName = 'videos.xml'
    NASRoot = "Y:\\media\\videos\\"

    allfiles = []
    allDirs = []

    print('Reading in files from NAS at path: ' + NAS_root)
    def store_files_name(fname):
        #print(fname)
        root, name = os.path.split(fname)
        if (name.find('mp4') > -1 or name.find('MP4') > -1) and name.find('._') == -1:
            allfiles.append([root, name, len(allfiles)])
        if (name.find('mkv') > -1 or name.find('MKV') > -1) and name.find('._') == -1:
            allfiles.append([root, name, len(allfiles)])
        if (name.find('avi') > -1 or name.find('AVI') > -1) and name.find('._') == -1:
            allfiles.append([root, name, len(allfiles)])

    def store_dir_name(dir_name):
        allDirs.append(os.path.split(dir_name)[-1])

    def store_other_file_type(other_file):
        pass

    with pysftp.Connection(NAS_hostname, username=NAS_user, password=NAS_pw) as sftp:
        sftp.walktree(NAS_root, store_files_name, store_dir_name, store_other_file_type)
        sftp.close()

    # print(allfiles[10:30])
    # print(allDirs)

    videoXMLFile = open(videoXMLFileName, 'w')
    videoXMLFile.write("<xml>\n")
    videoXMLFile.write("<viddb>\n")
    videoXMLFile.write("<movies>" + str(len(allfiles)) +"</movies>\n\n")

    print('...read in ' + str(len(allfiles) + 1) + ' files')
    print('Building XML media file at ' + videoXMLFileName)

    for finfo in allfiles:
        pathlist = finfo[0].split('/')
        NASPath = NASRoot
        for pathchunk in pathlist[-1:]:
            NASPath = NASPath + pathchunk + "\\"
        NASPath = NASPath + finfo[1]
        #print NASPath + " - " + finfo[0] + "/" + finfo[1]
        addEntry (videoXMLFile, finfo, allDirs, NASPath)

    videoXMLFile.write("</viddb>\n")
    videoXMLFile.write("</xml>\n")  
    videoXMLFile.close()

    print('Built XML media file for ' + str(len(allfiles) + 1) + ' movies')
    print('Now copying to NAS at: ', NAS_root)

    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None  

    with pysftp.Connection(NAS_hostname, username=NAS_user, password=NAS_pw, cnopts=cnopts) as sftp:
        sftp.put(videoXMLFileName,f"{NAS_root}/{videoXMLFileName}")  
        sftp.close()