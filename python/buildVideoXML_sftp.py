#!/Library/Frameworks/Python.framework/Versions/Current/bin/python
import os
from os.path import join, getsize, split
from random import randint
import pysftp   #conda install pysftp
import argparse
from getpass import getpass

def getVideoList(hostname, user, pw, path):
    def store_files_name(fname):
        #print(fname)
        root, name = os.path.split(fname)
        if (name.find('mp4') > -1 or name.find('MP4') > -1) and name.find('._') == -1:
            allFiles.append([root, name, len(allFiles)])
        if (name.find('mkv') > -1 or name.find('MKV') > -1) and name.find('._') == -1:
            allFiles.append([root, name, len(allFiles)])
        if (name.find('avi') > -1 or name.find('AVI') > -1) and name.find('._') == -1:
            allFiles.append([root, name, len(allFiles)])
    def store_dir_name(dir_name):
        allDirs.append(os.path.split(dir_name)[-1])
    def do_nothing(_str):
        pass

    print('Reading in files from NAS at path: ' + path)
    allFiles = []
    allDirs = []
    with pysftp.Connection(hostname, username=user, password=pw) as sftp:
        sftp.walktree(path, store_files_name, store_dir_name, do_nothing)
        sftp.close()

    return allFiles, allDirs

def getJPGList(hostname, user, pw, path):
    def store_files_name(fname):
        #print(fname)
        root, name = os.path.split(fname)
        if (name.find('jpg') > -1 or name.find('JPG') > -1) and name.find('FAM') > -1:
            allJPGs.append([root, name, len(allJPGs)])
    def do_nothing(_str):
        pass

    allJPGs = []
    with pysftp.Connection(hostname, username=user, password=pw) as sftp:
        sftp.walktree(path, store_files_name, do_nothing, do_nothing)

    return allJPGs

def addEntry (XMLFile, finfo, dirs, NASPath, jpg_cnt):
    finfo[1] = finfo[1].replace('.', '_', finfo.count('.')-1)
    title = finfo[1].split('.')[0]
    
    root = ''
    genre = 'Tom and Frederika'
    pathlist = finfo[0].split('/')
    for pathchunk in pathlist:
        for dirname in dirs:
            if pathchunk == dirname:
                genre = dirname
            
    imageFile = 'images/FAM%d.jpg' % randint(1,jpg_cnt)
        
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
    NAS_video_path='media/videos'
    NAS_jpg_path = path='media/videos/images'

    videoXMLFileName = 'videos.xml'
    NASRoot = "Y:\\media\\videos\\"

    allFiles, allDirs = getVideoList(NAS_hostname,NAS_user,NAS_pw,NAS_video_path)
    # print(allfiles[10:30])
    # print(allDirs)

    allJPGs = getJPGList(NAS_hostname,NAS_user,NAS_pw,NAS_jpg_path)
    jpg_cnt = len(allJPGs)

    videoXMLFile = open(videoXMLFileName, 'w')
    videoXMLFile.write("<xml>\n")
    videoXMLFile.write("<viddb>\n")
    videoXMLFile.write("<movies>" + str(len(allFiles)) +"</movies>\n\n")

    print('...read in ' + str(len(allFiles) + 1) + ' files')
    print('Building XML media file at ' + videoXMLFileName)

    for finfo in allFiles:
        pathlist = finfo[0].split('/')
        NASPath = NASRoot
        for pathchunk in pathlist[-1:]:
            NASPath = NASPath + pathchunk + "\\"
        NASPath = NASPath + finfo[1]
        #print NASPath + " - " + finfo[0] + "/" + finfo[1]
        addEntry (videoXMLFile, finfo, allDirs, NASPath, jpg_cnt)

    videoXMLFile.write("</viddb>\n")
    videoXMLFile.write("</xml>\n")  
    videoXMLFile.close()

    print('Built XML media file for ' + str(len(allFiles) + 1) + ' movies')
    print('Now copying to NAS at: ', NAS_video_path)

    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None  

    with pysftp.Connection(NAS_hostname, username=NAS_user, password=NAS_pw, cnopts=cnopts) as sftp:
        sftp.put(videoXMLFileName,f"{NAS_video_path}/{videoXMLFileName}")  
        sftp.close()