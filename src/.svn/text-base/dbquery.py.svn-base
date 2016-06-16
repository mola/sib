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

import os
from pysqlite2 import dbapi2 as sqlite

class db_con:
    name = "connection"
    address = ""
    con = None
    cur = None
    enable = False
    def __init__(self, name, add ,ena):
        self.name = name
        self.address = add
        self.con = sqlite.connect(add)
        self.cur = self.con.cursor()
        self.enable = ena

    def query(self,field,state):
        todo='SELECT %s FROM word WHERE %s' % (field,state)
        self.cur.execute(todo)
        find=self.cur.fetchall()
        if len(find)!= 0 :
            return find
        return None

class Database:
    db_con = []
    db_list = None
    
    def __init__(self,datadir):
        
        if os.path.exists(os.environ.get('HOME', '')+"/.sib/"):
            self.home = os.environ.get('HOME', '')+"/.sib/"
        else:
            self.home = None
        self.datadir=datadir
        self.list_of_db()
        self.ena_db = self.read_from_file()
        self.load()
        
    def list_of_db(self):
        
        DBdir = os.listdir(self.datadir)
        DBlist = [self.datadir+"/"+x for x in DBdir
                      if x.endswith('.sdb')
                      ]
        if (self.home==None):
            self.db_list = DBlist
            return
            
        DBdir = os.listdir(self.home)
        DBuser = [self.home+x for x in DBdir
                      if x.endswith('.sdb')
                      ]
        DBlist += DBuser
        self.db_list = DBlist
    
    def read_from_file(self):
        if self.home==None:
            return {"generic":[1, ""]}
        cpath = "custom_database"
        if os.path.exists(self.home+cpath):
            get_database={}
            input = file(self.home+cpath, "r")
            for i in input.readlines():
                split = i.split(":")
                if len(split)==3:
                    get_database[split[0]]=[int(split[1]), split[2]]
            input.close()
            if len(get_database)>0:
                return get_database
        return {"generic":[1, ""]}

    def load(self):
        if self.db_list==None:
            return
        ena = False
        for s in self.db_list:
            fi = os.path.basename(s).split(".")[0]
            if  self.ena_db.has_key(fi):
                if self.ena_db.get(fi)[0]==1:
                    ena = True
            else:
                ena = False
            
            con = db_con(os.path.basename(s),s,ena)
            self.db_con.append(con)
            
    def reload(self):
        for db in self.db_con:
            db.con.close()
            self.db_con.remove(db)
        
        self.db_con=[]
        self.load()
                    
    def add(self,name,add):
        fi = name.split(".")[0]
        if self.ena_db.get(fi)[0]==1:
            ena = True
        else:
            ena = False
        con = db_con(name,add,ena)
        self.db_con.append(con)
        
    def get_all(self,field,state):
        q = []
        for db in self.db_con:
            if db.enable == 0:
                continue
            r = db.query(field,state)
            if type(r) ==type([]):
                for s in r:
                    q.append(s[0])
        return q