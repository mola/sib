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

import pygtk
pygtk.require20()
import gtk, gobject
import gtk.glade
import os
import bgl2sdb
from pysqlite2 import dbapi2 as sqlite
import pynotify

__DATADIR__ = "/usr/share/sib"
__PIXDIR__ = "/usr/share/pixmaps/sib"

class lbase:
    def __init__(self):
        self.home = os.environ.get('HOME', '')+"/.sib/"
        self.list_db = None
        
    def list_of_db(self):
        DBdir = os.listdir(__DATADIR__)
        DBlist = [__DATADIR__+"/"+x for x in DBdir
                      if x.endswith('.sdb')
                      ]
        DBdir = os.listdir(self.home)
        DBuser = [self.home+x for x in DBdir
                      if x.endswith('.sdb')
                      ]
        DBlist += DBuser
        self.list_db=DBlist

    def write_to_file(self, dict):
        cpath = "custom_database"
        output = file(self.home+cpath, "w")
        for i in dict:
            output.write(i+":"+str(dict[i][0])+":"+dict[i][1]+'\n')
        output.close()
        return True
    
    def read_from_file(self):
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

class DBmanager:
    con = None
    cur = None
    num = 0
    tbs = None
    col_1 = 4
    def_database = "generic"
    custom_database={"generic":[1, ""]}
    
    def __init__(self,Ddir):
        self.ldb = lbase()
        self.glade=gtk.glade.XML(__DATADIR__+"/interface.glade","Dbmanager")
        self.window=gtk.Window()
        self.window=self.glade.get_widget("Dbmanager")
        self.status=self.glade.get_widget("statusbar2")
        self.toolbutton_apply = self.glade.get_widget("toolbutton8")
        self.toolbutton_cancel = self.glade.get_widget("toolbutton9")
        dict={"on_Dbmanager_destroy":self.wdestroy,
              "on_treeview2_cursor_changed":self.changeDB,
              "on_treeview3_cursor_changed":self.changeCursor,
              "on_toolbutton3_clicked":self.import_bgl,
              "on_toolbutton1_clicked":self.add_database,
              "on_toolbutton5_clicked":self.db_add_word,
              "on_toolbutton6_clicked":self.db_delete_word,
              "on_toolbutton7_clicked":self.db_edit_word,
              "on_toolbutton10_clicked":self.db_show_word, 
              "on_toolbutton11_clicked":self.set_as_defualt
              }

        self.treestore = gtk.ListStore(str,str,gobject.TYPE_BOOLEAN,str,str)

        self.treeview=self.glade.get_widget("treeview2")
        self.treeview.set_model(self.treestore)

        self.celli = gtk.CellRendererPixbuf()
        col = gtk.TreeViewColumn("D",self.celli)
        #self.celli.connect('button_press_event', self.col_image_cb,self.treestore)
        col.set_attributes( self.celli,stock_id=1)
        self.treeview.append_column(col)

        self.cellt = gtk.CellRendererToggle()
        self.cellt.set_property('activatable', True)
        self.cellt.connect( 'toggled', self.col1_toggled_cb,self.treestore )
        col = gtk.TreeViewColumn("Q",self.cellt)
        col.add_attribute( self.cellt, "active", 2)
        self.treeview.append_column(col)


        self.cell1 = gtk.CellRendererText()
        self.cell1.set_property( 'editable', True )
        self.cell1.connect( 'edited', self.col1_edited, self.treestore)
        col2 = gtk.TreeViewColumn("Database",self.cell1,text=3)
        self.treeview.append_column(col2)
        self.treeview.set_search_column(1)

        self.treestore.clear()

        self.treestore3 = gtk.ListStore(str)

        self.treeview3=self.glade.get_widget("treeview3")
        self.treeview3.set_model(self.treestore3)
        self.cell2 = gtk.CellRendererText()
        col3 = gtk.TreeViewColumn("Word",self.cell2,text=0)
        self.treeview3.append_column(col3)
        self.treeview3.set_search_column(0)

        self.custom_database=self.ldb.read_from_file()
        self.treestore3.clear()
        self.ldb.list_of_db()
        Default = None
        if self.ldb.list_db != None:
            for s in self.ldb.list_db:
                fi = os.path.basename(s).split(".")[0]
                if fi.find("Untitle")>=0:
                    self.num+=1
                
                if  self.custom_database.has_key(fi):
                    if self.custom_database.get(fi)[0]==1:
                        Default = gtk.STOCK_APPLY
                self.treestore.append([None,Default,self.custom_database.has_key(fi),fi,s])
                Default = None
        self.glade.signal_autoconnect(dict)
        self.window.show_all()
    
    def col1_edited( self, cell, path, new_text, model ):
        """
        Called when a text cell is edited.  It puts the new text
        in the model so that it is displayed properly.
        """
        home = os.environ.get('HOME', '')+"/.sib/"
        new = home+new_text+'.sdb'

        st = os.stat(model[path][self.col_1])
        mode = st[stat.ST_MODE]

        if mode & stat.S_IWRITE:  # same as stat.S_IWUSR
            if new_text!=model[path][self.col_1-1]:
                os.rename(model[path][self.col_1], new)

        model[path][self.col_1-1] = new_text
        model[path][self.col_1] = new

        return
            
    def col_image_cb(self,tree):
        print tree
        
    def set_as_defualt(self, obj):
        print "Set to default"
        
    def col1_toggled_cb( self, cell, path, model ):
        """
        Sets the toggled state on the toggle button to true or false.
        """
        model[path][2] = not model[path][2]
        if model[path][2]== True:
            self.custom_database[model[path][3]]=[1, model[path][self.col_1]]
        else:
            self.custom_database.__delitem__(model[path][3])
        print self.custom_database
        self.ldb.write_to_file(self.custom_database)
        return

    def add_database(self,obj):
        """ 
            Add database 
        """
        home = os.environ.get('HOME', '')+"/.sib"
        
        path = (home+"/Untitle%s.sdb"%(str(self.num)))
        self.con = sqlite.connect(path)
        self.cur = self.con.cursor()
        self.cur.execute("CREATE TABLE word (s_id INTEGER PRIMARY KEY,wname VARCHAR(75),wmean VARCHAR(400))")
        self.con.commit()        
        self.treestore.append([0,None,False,"Untitle%s"%(str(self.num)),path])
        self.num+=1
        self.con.close()
        
    def changeDB(self,obj,data=None):
        selection=obj.get_selection()
        (model,iter)=selection.get_selected()
        DB = model.get(iter,0)[0]
        path = model.get(iter,self.col_1)[0]
        self.status.push(0,path)

        self.clear()
        self.treestore3.clear()
        
        if os.access(path, os.R_OK):   # same as stat.S_IRUSR
            self.glade.get_widget("image2").set_from_stock(gtk.STOCK_YES,gtk.ICON_SIZE_BUTTON)
            self.glade.get_widget("toolbutton10").set_sensitive(True)
        else:
            self.glade.get_widget("toolbutton10").set_sensitive(False)
            self.status.push(0,"Not have permission")
            self.default_form()
            return

        if os.access(path, os.W_OK):  # same as stat.S_IWUSR
            for i in ['5','6','7']:
                self.glade.get_widget("toolbutton%s" %(i)).set_sensitive(True)
            self.glade.get_widget("image3").set_from_stock(gtk.STOCK_YES,gtk.ICON_SIZE_BUTTON)
        else:
            for i in ['5','6','7']:
                self.glade.get_widget("toolbutton%s" %(i)).set_sensitive(False)
            self.glade.get_widget("image3").set_from_stock(gtk.STOCK_NO,gtk.ICON_SIZE_BUTTON)
            
##        if mode & stat.S_IEXEC:   # same as stat.S_IXUSR
##            print "executable"
        if self.con!=None :
            self.con.close()
        self.con = sqlite.connect(path)
        self.cur = self.con.cursor()
        self.glade.get_widget("label4").set_text(model.get(iter,self.col_1-1)[0])
        self.glade.get_widget("label6").set_text(str(self.rowcount()))

    def rowcount(self):
        todo='select count(word.wname) from word'
        self.cur.execute(todo)
        find=self.cur.fetchall()
        if len(find)!= 0 :
            return find[0][0]
        
        return None
    
    def default_form(self):
        self.glade.get_widget("label4").set_text("-")
        self.glade.get_widget("label6").set_text("0")
        self.glade.get_widget("image2").set_from_stock(gtk.STOCK_NO,gtk.ICON_SIZE_BUTTON)
        self.glade.get_widget("image3").set_from_stock(gtk.STOCK_NO,gtk.ICON_SIZE_BUTTON)

    def db_add_word(self,obj):
        textbox=gtk.TextView()
        entry = self.glade.get_widget("entry1")
        textbox = self.glade.get_widget("textview2")
        
        self.clear()
        
        self.toolbutton_apply.connect("clicked",self.add_word,entry,textbox)
        self.toolbutton_cancel.connect("clicked",self.cancel_word,entry,textbox)
        self.toolbutton_apply.set_sensitive(True)
        self.toolbutton_cancel.set_sensitive(True)
        entry.set_property('editable', True)
        textbox.set_property('editable', True)
        

    def add_word(self,obj,entry,textbox):
        buf = textbox.get_buffer()
        text= buf.get_text(buf.get_start_iter(),buf.get_end_iter(),True)
        self.cur.execute('INSERT INTO word (s_id,wname,wmean) VALUES (NULL,"%s","%s")'%(entry.get_text(),text))
        self.con.commit()        

        entry.set_property('editable', False)
        textbox.set_property('editable', False)
        self.toolbutton_apply.set_sensitive(False)
        self.toolbutton_cancel.set_sensitive(False)
        
    def cancel_word(self,obj,entry,textbox):
        self.clear()
        entry.set_property('editable', False)
        textbox.set_property('editable', False)
        
    def db_delete_word(self,obj):
        selection=self.treeview3.get_selection()
        (model,iter)=selection.get_selected()
        word = model[iter][0]
        if iter==None:
            self.messageon("Can't Delete","First select the word",pynotify.URGENCY_CRITICAL)
            return
        
        msgWindow=gtk.MessageDialog(None,0,gtk.MESSAGE_QUESTION,gtk.BUTTONS_OK_CANCEL,"Do you want to delete word?")
        response=msgWindow.run()
        msgWindow.destroy()
        if response == -5:
            self.cur.execute('DELETE FROM word WHERE wname="%s"'%(word))
            self.con.commit()
            self.clear()
        
    def db_edit_word(self,obj):
        selection=self.treeview3.get_selection()
        (model,iter)=selection.get_selected()
        entry = model[iter][0]
        textbox = self.glade.get_widget("textview2")

        self.toolbutton_apply.connect("clicked",self.edit_word,entry,textbox)
        self.toolbutton_cancel.connect("clicked",self.cancel_word,entry,textbox)
        self.toolbutton_apply.set_sensitive(True)
        self.toolbutton_cancel.set_sensitive(True)
        textbox.set_property('editable', True)

    def edit_word(self, obj, entry, textbox):
        buf = textbox.get_buffer()
        text= buf.get_text(buf.get_start_iter(),buf.get_end_iter(),True)
        self.cur.execute('Update word SET wmean = "%s" WHERE wname="%s"'%(text,entry))
        self.con.commit()        

        textbox.set_property('editable', False)
        self.toolbutton_apply.set_sensitive(False)
        self.toolbutton_cancel.set_sensitive(False)

    def db_show_word(self,obj):
        if self.con==None :
            return
        todo='SELECT * FROM word'
        self.cur.execute(todo)
        find=self.cur.fetchall()
        self.treestore3.clear()
        if find != None:
            for s in find:
                self.treestore3.append([s[1]])

    def changeCursor(self,obj):
        selection=obj.get_selection()
        (mode,iter)=selection.get_selected()
        word=mode.get(iter,0)[0]
        string=self.query('wmean','wname = "%s"'%(word))
        textview=self.glade.get_widget("textview2")
        buf=textview.get_buffer()
        buf.set_text(string[0][0])
        textview.set_buffer(buf)

    def query(self,field,state):
        todo='SELECT %s FROM word WHERE %s' % (field,state)
        self.cur.execute(todo)
        find=self.cur.fetchall()
        
        if len(find)!= 0 :
            return find
        
        return None

    def clear(self):
        entry = self.glade.get_widget("entry1")
        textbox = self.glade.get_widget("textview2")
        
        entry.set_text("")
        buf = textbox.get_buffer()
        buf.set_text("")
        textbox.set_buffer(buf)
                
    def messageon(self, titr, text, model):
        pynotify.init("Dictonary Sib")
        n = pynotify.Notification(titr, text, __PIXDIR__+"/sib.png")
        n.set_urgency(model)
        n.set_timeout(4000) 
        if not n.show():
            print "Can't create notify"
    
    def import_bgl(self, obj):
        Dialog = gtk.FileChooserDialog(title=None,action=gtk.FILE_CHOOSER_ACTION_OPEN,
                                       buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,
                                                gtk.STOCK_OPEN,gtk.RESPONSE_OK))

        filter = gtk.FileFilter()
        filter.set_name("All files")
        filter.add_pattern("*")
        filter = gtk.FileFilter()
        filter.set_name("BGL file")
        filter.add_pattern("*.bgl")
        filter.add_pattern("*.BGL")
        Dialog.add_filter(filter)
        
        result = Dialog.run()
        bglfile = Dialog.get_filename()
        Dialog.destroy()
        if result == gtk.RESPONSE_CANCEL:
            return
        
        if result == gtk.RESPONSE_OK:
            progress = self.glade.get_widget("progressbar1")
            bar = self.glade.get_widget("statusbar2")
            progress.pulse()
            #self.window.set_sensitive(False)
            self.glade.get_widget("hpaned2").set_sensitive(False)
            self.glade.get_widget("toolbar1").set_sensitive(False)
            
            bname = os.path.basename(bglfile)
            
            home = os.environ.get('HOME', '')+"/.sib"
            p = home+"/"+bname[0:-4]+".sdb"
            path = (p)
            self.tbs = bgl2sdb.Bgl2Sdb(bglfile,path,bar,progress)
            self.tbs.convert()
            self.glade.get_widget("hpaned2").set_sensitive(True)
            self.glade.get_widget("toolbar1").set_sensitive(True)
        
        progress.set_fraction(0.0)
        self.treestore.clear()
        find = self.ldb.list_of_db()
        if find != None:
            for s in find:
                fi = os.path.basename(s).split(".")[0]
                if fi == "Untitle":
                    self.num+=1
                self.treestore.append([0,False,fi,s])
            
    def wdestroy(self, obj):
        if self.con!=None:
            self.con.close()
        self.window.destroy()
