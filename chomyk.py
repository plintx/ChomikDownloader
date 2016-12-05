#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import getopt
import logging
import hashlib
import requests
import os
from sys import stdout
from time import time, strftime
from xml.etree import ElementTree as et
from collections import OrderedDict

class Item:

    def __init__(self):
        self.id = 0
        self.AgreementInfo = 'own'
        self.realId = 0
        self.name = ''
        self.url = ''
        self.num = 1

    def dl(self):
        r = requests.get(self.url, stream=True)
        path = os.getcwd()+'/'+self.name
        with open(path, 'wb') as fd:
            total_length = int(r.headers.get('content-length'))
            dl_size = 0
            for chunk in r.iter_content(chunk_size=128):
                dl_size = dl_size+128
                progress = dl_size * 100. / total_length
                status = "\r%.2s. %.20s %10d MB  [%3d%%] [%-25s]" % (self.num, self.name, dl_size/(1024**2), progress, "#"*int(progress/4))
                stdout.write(status)
                stdout.flush()
                fd.write(chunk)
        print ("\r")

class Chomyk:

    def __init__(self, username, password):
        self.logger = logging.getLogger(__name__)
        self.isLogged = True
        self.lastLoginTime = 0
        self.hamsterId = 0
        self.token = ''
        self.items = 0

        self.username = username
        self.password = hashlib.md5(password.encode("utf-8")).hexdigest()

        self.logger.info("Obiekt zainicjowany")
        self.login()

    def postData(self, postVars):
        url = "http://box.chomikuj.pl/services/ChomikBoxService.svc"
        body = postVars.get("body")
        headers = {
            "SOAPAction": postVars.get("SOAPAction"),
            "Content-Encoding": "identity",
            "Content-Type": "text/xml;charset=utf-8",
            "Content-Length": str(len(body)),
            "Connection": "Keep-Alive",
            "Accept-Encoding": "identity",
            "Accept-Language": "pl-PL,en,*",
            "User-Agent": "Mozilla/5.0",
            "Host": "box.chomikuj.pl",
            }

        self.logger.info("Post data url:" + url)
        self.logger.info("Post data body:" + body)

        response = requests.post(url, data=body, headers=headers)

        self.logger.info("Response:" + str(response.content))
        self.parseResponse(response.content)

    def dl(self, url):
        shortUrl = url[18:]
        rootParams = {
            "xmlns:s": "http://schemas.xmlsoap.org/soap/envelope/",
            "s:encodingStyle": "http://schemas.xmlsoap.org/soap/encoding/"
            }
        root = et.Element('s:Envelope', rootParams)

        body = et.SubElement(root, "s:Body")
        downloadParams = {
            "xmlns": "http://chomikuj.pl/"
            }
        download = et.SubElement(body, "Download", downloadParams)
        downloadSubtree = OrderedDict([
            ("token", self.token,),
            ("sequence", [
                ("stamp", "123456789"),
                ("part", "0"),
                ("count", "1")
                ]),
            ("disposition", "download"),
            ("list",  [
                    ("DownloadReqEntry", [
                        ("id", shortUrl),
                    ])
                ])
            ])

        self.add_items(download, downloadSubtree)

        xmlDoc = """<?xml version="1.0" encoding="UTF-8"?>"""
        xmlDoc += et.tostring(root, encoding='unicode', method='xml')
        self.logger.info("Post: "+ xmlDoc)

        dts = {
            "body": xmlDoc,
            "SOAPAction": "http://chomikuj.pl/IChomikBoxService/Download"
        }
        self.postData(dts)

    def dl_step_2(self, idx, agreementInfo,cost = 0):
        rootParams = {
            "xmlns:s": "http://schemas.xmlsoap.org/soap/envelope/",
            "s:encodingStyle": "http://schemas.xmlsoap.org/soap/encoding/"
            }
        root = et.Element('s:Envelope', rootParams)

        body = et.SubElement(root, "s:Body")
        downloadParams = {
            "xmlns": "http://chomikuj.pl/"
            }
        download = et.SubElement(body, "Download", downloadParams)
        downloadSubtree = OrderedDict([
            ("token", self.token,),
            ("sequence", [
                ("stamp", "123456789"),
                ("part", "0"),
                ("count", "1")
                ]),
            ("disposition", "download"),
            ("list",  [
                    ("DownloadReqEntry", [
                        ("id", idx),
                        ("agreementInfo", [
                            ("AgreementInfo", [
                                ("name", agreementInfo),
                                ("cost", cost),
                            ])
                        ])
                    ])
            ])
            ])

        self.add_items(download, downloadSubtree)

        xmlDoc = """<?xml version="1.0" encoding="UTF-8"?>"""
        xmlDoc += et.tostring(root, encoding='unicode', method='xml')

        dts = {
            "body": xmlDoc,
            "SOAPAction": "http://chomikuj.pl/IChomikBoxService/Download"
        }
        self.postData(dts)

    def login(self):

        rootParams = {
            "xmlns:s": "http://schemas.xmlsoap.org/soap/envelope/",
            "s:encodingStyle": "http://schemas.xmlsoap.org/soap/encoding/"
            }
        root = et.Element('s:Envelope', rootParams)

        body = et.SubElement(root, "s:Body")
        authParams = {
            "xmlns": "http://chomikuj.pl/"
            }
        auth = et.SubElement(body, "Auth", authParams)

        authSubtree = OrderedDict([
            ("name", self.username,),
            ("passHash", self.password,),
            ("ver", "4"),
            ("client", OrderedDict([
                    ("name", "chomikbox"),
                    ("version", "2.0.5"),
                ]))
            ])

        self.add_items(auth, authSubtree)

        xmlDoc = """<?xml version="1.0" encoding="UTF-8"?>"""
        xmlDoc += et.tostring(root, encoding='unicode', method='xml')

        dts = {
            "body": xmlDoc,
            "SOAPAction": "http://chomikuj.pl/IChomikBoxService/Auth"
        }
        self.postData(dts)

    def add_items(self, root, items):
        if type(items) is OrderedDict:
            for name, text in items.items():
                if type(text) is str:
                    elem = et.SubElement(root, name)
                    elem.text = text
                if type(text) is list:
                    subroot = et.SubElement(root, name)
                    self.add_items(subroot, text)
        elif type(items) is list:
            for name, text in items:
                if type(text) is str:
                    elem = et.SubElement(root, name)
                    elem.text = text
                if type(text) is list:
                    subroot = et.SubElement(root, name)
                    self.add_items(subroot, text)

    def parseResponse(self, resp):
        self.logger.info("Response: " + str(resp))
        respTree = et.fromstring(resp)

        #Autoryzacja
        for dts in respTree.findall(".//{http://chomikuj.pl/}AuthResult/{http://chomikuj.pl}status"):
            status = dts.text
            if status.upper() == "OK":
                self.isLogged = True
                self.lastLoginTime = time()
                self.token = respTree.findall(".//{http://chomikuj.pl/}AuthResult/{http://chomikuj.pl}token")[0].text
                self.hamsterId = respTree.findall(".//{http://chomikuj.pl/}AuthResult/{http://chomikuj.pl}hamsterId")[0].text
                print ("Login: OK")

            else:
                 self.isLogged = False
                 print ("Login: " + status)

        #Pobieranie urli plikow
        for dts in respTree.findall(".//{http://chomikuj.pl/}DownloadResult/{http://chomikuj.pl}status"):
            status = dts.text
            if status.upper() == "OK":
                for dlfile in respTree.findall(".//{http://chomikuj.pl/}files/{http://chomikuj.pl/}FileEntry"):
                    url = dlfile.find('{http://chomikuj.pl/}url')
                    idx = dlfile.find('{http://chomikuj.pl/}id').text
                    cost = dlfile.find('{http://chomikuj.pl/}cost')
                    if url.text == None:
                        agreementInfo = dlfile.find("{http://chomikuj.pl/}agreementInfo/{http://chomikuj.pl/}AgreementInfo/{http://chomikuj.pl/}name").text
                        costInfo = dlfile.find("{http://chomikuj.pl/}agreementInfo/{http://chomikuj.pl/}AgreementInfo/{http://chomikuj.pl/}cost")
                        if costInfo.text == None:
                            cost = 0
                        else:
                            cost = costInfo.text
                        self.dl_step_2(idx, agreementInfo,cost)
                    else:
                        self.items = self.items +1
                        it = Item()
                        it.id = idx
                        it.num = self.items
                        it.url = url.text
                        it.name = dlfile.find('{http://chomikuj.pl/}name').text
                        it.dl()


def main(argv):
    url = ''
    output = ''
    username = ''
    password = ''
    try:
        opts, args = getopt.getopt(argv,"hupi:o",["username=","password=","ifile=","ofile="])
    except getopt.GetoptError:
        printUsage()
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print("Help:")
            printUsage()
            sys.exit()
        elif opt in ("--i", "--ifile"):
            url = arg
        elif opt in ("--o", "--ofile"):
            output = arg
        elif opt in ("--u", "--username"):
            username = arg
        elif opt in ("--p", "--password"):
            password = arg

    if len(password) > 0 and len(username) >0 and len(url)>0:
        ch = Chomyk(username,password)
        ch.dl(str(url))
    else:
        printUsage()

def printUsage():
    print ('chomyk.py --u username --p password --i <url>')
    sys.exit(2)

if __name__ == "__main__":
   main(sys.argv[1:])