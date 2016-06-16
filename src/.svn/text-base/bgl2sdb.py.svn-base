#!/usr/bin/env python
# -*- coding: utf-8 -*-
##
#    
#    Copyright (C) 2007  Mola Pahnadayan
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
##

import gtk
import gzip                      # Read and write gzipped files.
import os                        # Miscellaneous OS interfaces.
import re                        # Regular Expression
from pysqlite2 import dbapi2 as sqlite



class BGL:
    '.Bgl (Babylon Glossary) Reader Class'
    def __init__(self, bglFileName):
        self.bglFileName = bglFileName
        # File formats to romove from DataBase
        self.TrimFileExts = ['.bmp', '.html','.gif','.jpg'] 
        
    def open(self):
        print '\n+ Opening "%s"'.ljust(40)%self.bglFileName,
        try:
            bglFile = file(self.bglFileName, 'rb')
        except:
            print '\nIOError !\nNo such file or directory: %s\n'%self.bglFileName
            return False

        if not bglFile:
            return False
        # Reading and testing first 4 byte.
        # BGL file signature must be : 0x12340001 or 0x12340002
        sign = bglFile.read(6)
        if len(sign)<6 or sign[:3]!='\x12\x34\x00' or sign[3]=='\x00' or sign[3]>'\x02':
            print '\n%s is not a .BGL(Babylon Glossary) file !\n'%self.bglFileName
            return False
        # Calculating gz header and bypass it
        gz = ord(sign[4]) << 8 | ord(sign[5])
        bglFile.seek(gz)
        file('temp.tmp','wb').write(bglFile.read())
        del bglFile
        self.bglFile = gzip.open('temp.tmp','rb')
        print '\t\t[Ok]'.ljust(40)
        return True
    
    def close(self):
        'Close Bgl file & Remove temp file'
        print '+ Closing "%s"'.ljust(40)%self.bglFileName,
        self.bglFile.close()
        os.remove('temp.tmp')
        print '\t\t[Ok]'.ljust(40)
        
    def BglBlockReader(self):
        block = {'data': None}
        block['length'] = self.BglRawReader(1)
        block['type'] = block['length'] & 0xf
        block['length'] >>= 4
        if block['length'] < 4 :
            block['length'] = self.BglRawReader(block['length'] + 1)
        else:
            block['length'] -= 4
        if block['length'] :
            block['data'] = self.bglFile.read(block['length'])
        return block
        
    def BglRawReader(self, bytes):
        val = 0
        if bytes<1 or bytes>4:
            return 0
        buf = self.bglFile.read(bytes)
        if not buf:
            raise IOError, 'EOF !'
        for i in buf:
            val = val << 8 | ord(i)
        return val
    
    def readWord(self):
        try:
            block = self.BglBlockReader()
        except :
            return False
        if not block :
            return False
        try:
            lenHW = ord(block['data'][0]) + 1
            word = block['data'][1:lenHW].split('$')[0]
            lenDF = (ord(block['data'][lenHW + 1])) + 1
            definition = block['data'][lenHW+2:lenDF+lenHW+1]

            return self.TrimBlock(word, definition)
        except:
            return None
        
    def TrimBlock(self, word, definition):
        "Remove unwanted data from word and it's definition"
        # It is link ! not data !!
        if word.count('@'):
            return None
        # return None if it is a file 
        for ext in self.TrimFileExts:
            if word.count(ext):
                return None
        
        word = word.strip()
        word = unicode(word, 'utf8')

        # spilting fragmented data
        try:
            definition += ' ' +  definition.split('\x18')[1]
        except:
            pass
        
        # we only need first piece of data 
        definition = definition.split('\x14')[0]
        
        # Converting to Persian(Arabic) 
        # TODO: support other charsets
        definition = unicode(definition,'cp1256').encode('utf8')

        # Remove Tags
        definition = definition.replace('<BR>','\n')
        if definition.count('<'):
            definition = re.sub('<.{1,4}>','', definition)
        if definition.count('href'):
            definition = re.sub('<.*href.*>','', definition)
        
        definition = definition.replace('<','(')
        definition = definition.replace('>',')')        
        definition = unicode(definition, 'utf8')
        
        return word, definition
    
    def ReadBglHeader(self):
        if not self.bglFile:
            return False
        self._numEntries = 0
        while True:
            block = self.BglBlockReader()
            if not block or not block['length']:
                break
        return True
    
        
class SDB:
    def __init__(self,sqlFilename):
        self.sqlFile = sqlFilename
        self.con = sqlite.connect(self.sqlFile)
        self.cur = self.con.cursor()
        ### Create database
        try :
            self.cur.execute("CREATE TABLE word (s_id INTEGER PRIMARY KEY,wname VARCHAR(75),wmean VARCHAR(400))")
            self.con.commit()
        except:
            print " Faild "
    
    def insert(self,name,data):
        if name.find('"')!=-1:
            name=self.findquata(name)
        if data.find('"')!=-1:
            data=self.findquata(data)
        todo = 'INSERT INTO word (s_id,wname,wmean) VALUES (NULL,"%s","%s")' % (name,data)
        self.cur.execute(todo)
        self.con.commit()
        return True
    
    def findquata(self,name):
        result = ""
        for s in name:
            result += s
            if s =='"':
                result+='"'
        return result
        
    

class Bgl2Sdb():
    def __init__(self, Bgl,Sdb,bar,progress):
        self.counter = 0 # Word counter
        self.bglFileName = Bgl
        self.bar = bar
        self.progress = progress
        self.SDB = SDB(Sdb)
        self.BGL = BGL(self.bglFileName)
    
    def convert(self):
        if not self.BGL.open():
            print 'Error in Reading bgl file !\n'
            return False
        self.BGL.ReadBglHeader()
        dbname = os.path.splitext(self.bglFileName)[0]
        dbname = os.path.split(dbname)[1]
        ### Converting
        while True:
            data = self.BGL.readWord()
            # Error or EOF
            if data == False :
                break
            
            elif data == None or data[0] == '' or data[1] == '': 
                continue
            else:
                if self.SDB.insert(data[0],data[1]) == True:
                    self.progress.pulse()
                    self.counter+=1
                    print self.counter
                    buff = " %d Words added." % (self.counter)
                    self.bar.push(0,buff)
                    while gtk.events_pending():
                        gtk.main_iteration_do(False)


        self.BGL.close()
        print '\nOk! %d word converted from %s to %s !\n'%(self.counter, self.bglFileName, self.SDB.sqlFile)
