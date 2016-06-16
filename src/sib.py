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

import pygtk
pygtk.require20()
import gtk, gobject
import gtk.glade, gtk.gdk
import os
import pynotify
import commands
import pango

import prefrence
import dbmanager
import dbquery

__DATADIR__ = "/usr/share/sib"
__PIXDIR__ = "/usr/share/pixmaps/sib"

class main:
    version = "0.8"
    tray = None
    clipboardtimer = 1000
    lastclipboard = ""
    lastword = ""
    reverse = False
    shownotify = False
    minimize = 0
    chistory = 0
    word_change = 0
    ## for Speech
    festival = 'echo "%s"|festival --tts'
    espeak = 'espeak "%s"'
          
    def clipboard_text_received(self, clipboard, text, data):
        if not text or text == '' or text[0] == ' ':
            return
        ch = ord(text[0])
        if not( (ch>=97 and ch<=122)or(ch>=65 and ch<=90)):
            return
        
        if self.lastclipboard != text:
            word = text
            word = self.parse(word)
            if self.lastword != word:
                self.shownotify = True
                self.comboentry.insert_text(0, word)
                self.comboentry.set_active(0)
                self.word_change = 0
                self.lastword = word

            self.chistory += 1
            if self.chistory>self.history:
                self.comboentry.remove_text(self.history)
                self.chistory -= 1
            self.lastclipboard = text
        return
    
    def fetch_clipboard_info(self):
        self.clipboard.request_text(self.clipboard_text_received)
        return True
        
    def activate_icon_cb(self, data=None):
        if self.minimize == 1:
            self.window.set_property("skip-taskbar-hint", False)
            self.window.deiconify()
            self.minimize = 0
            return
        
        if self.window.get_property('visible'):
            self.window.hide()
        else:
            self.window.set_property("skip-taskbar-hint", False)
            self.window.present()

    def popup_menu_cb(self, obj, button, time):
        menu = self.pmenu.get_widget("menu1")
        menu.popup(None, None, None, button, time)
    
    def TrayLoad(self):
        self.statusIcon = gtk.StatusIcon()
        self.statusIcon.set_from_file(__PIXDIR__+"/sib-24.png")
        self.statusIcon.set_tooltip("Dictonary Sib")
        self.statusIcon.connect('activate', self.activate_icon_cb)
        self.statusIcon.connect('popup-menu', self.popup_menu_cb)
        self.statusIcon.set_visible(True)

        self.clipboard = gtk.clipboard_get(gtk.gdk.SELECTION_PRIMARY)
        self.clipboard.request_text(self.clipboard_text_received)
        gobject.timeout_add(self.clipboardtimer, self.fetch_clipboard_info)
        
    def about_dialog(self, obj):
        if (self.about is None):
            self.about = gtk.AboutDialog()
            self.about.set_name("Sib is a dictionary")
            #self.about.set_version(self.version)
            self.about.set_authors(["Mola Pahnadayan  <mola.mp@gmail.com>", 
                                    "   Project Manager, Maintainer",
                                    "\nThanks to",
                                    "  Foad Nosrati Habibi  <foad.nh@gmail.com>"
                                    ])
            file = open(__DATADIR__+"/COPYING")
            license = file.read()
            file.close()
            self.about.set_license(license)
            pixmap = gtk.gdk.pixbuf_new_from_file(__PIXDIR__+"/about.png")
            self.about.set_logo(pixmap)
            self.about.set_transient_for(self.window)
            self.about.set_website("http://sib.ospdev.net")
            def response_cb(widget, id):
                return True
            self.about.connect ("response", response_cb)
            result=self.about.run()
            self.about.destroy()
            self.about = None
        
    def __init__(self):
        ghome=os.environ.get('HOME', '')+'/.sib'
        if os.path.exists(ghome)==False:
            os.mkdir(ghome)
        prefrence.option_parse()
        self.speak = self.festival
        self.dbs = dbmanager.lbase()
        self.glade = gtk.glade.XML(__DATADIR__+"/interface.glade","window1")
        self.window = gtk.Window()
        self.window = self.glade.get_widget("window1")
        dict = {"on_window1_delete_event":self.wdelete,
              "on_comboboxentry1_changed":self.change,
              "on_treeview1_cursor_changed":self.cursorchange,
              "on_togglebutton1_toggled":self.reversesearch,
              "on_window1_window_state_event":self.mainchange,
              "on_treeview1_button_press_event":self.popupcopy,
              "on_btn_speech_clicked":self.speechplay,
              }
        self.glade.signal_autoconnect(dict)      
        
        self.comboentry = gtk.ComboBoxEntry()
        self.comboentry = self.glade.get_widget("comboboxentry1")
        self.store = gtk.ListStore(str)
        self.comboentry.set_model(self.store)
        self.comboentry.set_text_column(0)
        self.entry1 = self.comboentry.get_child()
        self.entry1.connect("key_press_event",self.entry_keypress)

        ## Speech button
        self.btn_speech = gtk.Button()
        self.btn_speech = self.glade.get_widget("btn_speech")
                        
        toggle = self.glade.get_widget("togglebutton1")
        image = gtk.Image()
        image.set_from_file(__PIXDIR__+"/reverse.png")
        toggle.set_image(image)
        self.pmenu = gtk.glade.XML(__DATADIR__+"/interface.glade","menu1")
        mdict = {"on_quit1_activate":gtk.main_quit,
               "on_about1_activate":self.about_dialog,
               "on_preferences1_activate":self.loadpref,
               "on_DBmanager_activate":self.loadDBmanager
               }
        self.pmenu.signal_autoconnect(mdict)
        
        self.about = None
        self.DB_con = dbquery.Database(__DATADIR__)
        
        self.window.set_icon_from_file(__PIXDIR__+"/sib.png")
        self.TrayLoad()
        
        self.treestore = gtk.ListStore(str,str)

        self.treeview = self.glade.get_widget("treeview1")
        self.treeview.set_model(self.treestore)
        
        self.cell = gtk.CellRendererText()
        col = gtk.TreeViewColumn("Word",self.cell,text = 0)
        self.treeview.append_column(col)
        self.treeview.set_search_column(0)
        
        self.textv = self.glade.get_widget("textview1")
        self.btn_speech = self.glade.get_widget("btn_speech")
        if os.path.exists("/usr/bin/festival"):
            self.btn_speech.set_sensitive(True)
        self.option_applay()

        self.window.hide()
    
    def change(self, obj):
        if self.searchontype:
            id = self.comboentry.get_active_text()
            self.translate(id)
        self.word_change = 0


    def translate(self, id = None):
        string = None
        conv = 0
        if len(id)>0:
            if self.reverse:
                string = self.query('wname','wmean like "%% %s %%"'%(id))
            else:
                string = self.query('wname','wname like "%s%%"'%(id))
                while string == None and conv != 2:
                    id, conv = self.convert(id, conv)
                    string = self.query('wname','wname like "%s%%"'%(id))                
        self.treestore.clear()
        if string != None:
            for s in string:
                self.treestore.append([s,None])
            count = self.glade.get_widget("statusbar1")
            buff = " Find %d words" % len(string)
            count.push(0,buff)
        else:
            textview = self.glade.get_widget("textview1")
            buf = textview.get_buffer()
            buf.set_text("Word not find")
            textview.set_buffer(buf)
        row = self.treestore.get_iter_first()
        if row!= None:
            path = self.treestore.get_path(row)
            self.treeview.set_cursor(path, None, False)

    def convert(self, word, conv):
        if word[-1:] == 'd' and conv == 0:
            return word[:-1], 1
        elif word[-1:] == 'e' and conv == 1:
            return word[:-1], 2
        elif word[-1:] == 's' and conv == 0:
            return word[:-1], 1
        elif word[-3:] == 'ing' and conv == 0:
            return word[:-3], 2
        elif word[-2:] == 'ly' and conv == 0:
            return word[:-2], 2
        else:
            return word, 2

    def cursorchange(self, obj):
        selection = obj.get_selection()
        (mode,iter) = selection.get_selected()
        word = mode.get(iter,0)[0]
        string = self.query('wmean','wname = "%s"'%(word))
        if len(string)>0:
            text = ""
            for s in string:
                text += unicode(s) + ','
            string = text
        if not(self.window.is_active()) :
            self.notify(word,unicode(string))
        textview = self.glade.get_widget("textview1")
        buf = textview.get_buffer()
        buf.set_text(string)
        textview.set_buffer(buf)
        self.word_change = 1

    def query(self, field, state):
        find = self.DB_con.get_all(field, state)
        if len(find)!= 0 :
            return find
        
        return None
    
    def notify(self, word, msg):
        pynotify.init("Dictonary Sib")
        n = pynotify.Notification(word, msg, __PIXDIR__+"/sib.png")
        n.set_urgency(pynotify.URGENCY_NORMAL )
        n.set_timeout(self.notifytimer) 
        if not n.show():
            print "Can't create notify"
        
    def reversesearch(self, obj):
        self.reverse = obj.get_active()

    def mainchange(self, obj, state):
        event = state.new_window_state
        if event == gtk.gdk.WINDOW_STATE_ICONIFIED:
            self.window.set_property("skip-taskbar-hint", True)
            self.minimize = 1
            
    def wdelete(self, obj, event):
        self.window.hide()
        return True
    
    def parse(self, str):
        string = ""
        for char in str:
            ch = ord(char)
            if ( (ch>=97 and ch<=122)or(ch>=65 and ch<=90)):
                string+=char
            else:
                break
                
        return string

    def copytoclipboard(self, obj):
        selection=self.treeview.get_selection()
        (mode,iter) = selection.get_selected()
        if iter:
            word = mode.get(iter,0)[0]
            self.shownotify = False
            c = gtk.Clipboard()
            c.set_text(''.join(word))
            c.store()
        
    def popupcopy(self, button, event):
        if event.button==3:
            menu = gtk.Menu()
            mcopy = gtk.ImageMenuItem(stock_id=gtk.STOCK_COPY)
            mcopy.connect("activate",self.copytoclipboard)
            mcopy.show()
            menu.insert(mcopy,0)
            menu.popup(None, None, None, event.button, event.time)

    def entry_keypress(self, obj, key):
        if key.keyval==gtk.keysyms.Return:
            word = self.comboentry.get_active_text()
            self.shownotify = False
            self.comboentry.insert_text(0,word)
            self.lastword = word
            self.chistory += 1
            self.word_change = 0
            if self.chistory>self.history:
                self.comboentry.remove_text(self.history)
                self.chistory -= 1
            if not(self.searchontype):
                self.translate(word)

    def loadpref(self, obj, data=None):
        dialog = prefrence.prefrence(__DATADIR__,__PIXDIR__,self.searchontype,
                            self.notifytimer,self.history,self.Dfont,self.Sfont)
        feedback=dialog.dlg.run()
        dialog.dlg.destroy()
        self.option_applay()
    
    def loadDBmanager(self, obj, data=None):
        dialog = dbmanager.DBmanager(__DATADIR__)
            
    def option_applay(self):
        try:
            if str(prefrence.Option['searchontype'])[0] == 'T':
                self.searchontype = True
            else:
                self.searchontype = False
        except:
            self.searchontype = True

        try:
            self.notifytimer =int( prefrence.Option['notifytimer'])
        except:
            self.notifytimer = 5000
        
        try:
            self.history = int(prefrence.Option['history'])
        except:
            self.history = 10
        
        if str(prefrence.Option['Dfont'])[0]=='T':
            self.Dfont = True
        else:
            self.Dfont = False
        
        try:
            self.Sfont = str(prefrence.Option['Sfont'])
        except:
            self.Sfont = ""

        if (self.Dfont==True)and(self.Sfont!=None):
            self.textv.modify_font(pango.FontDescription(self.Sfont))
        else:
            self.textv.modify_font(pango.FontDescription(""))

    
    def speechplay(self,obj,data=None):
        if self.comboentry.get_active_text() == '':
            return
        if self.word_change == 0:
            out_put = commands.getstatusoutput(self.speak %(self.comboentry.get_active_text()))
        else:
            selection = self.treeview.get_selection()
            (mode,iter) = selection.get_selected()
            word = mode.get(iter,0)[0]
            out_put = commands.getstatusoutput(self.speak %(word))
            
        if out_put[1].find("Invalid device") >= 0:
            pynotify.init("Dictonary Sib")
            n = pynotify.Notification("Warnning", "Sound device is used by another program", __PIXDIR__+"/sib.png")
            n.set_urgency(pynotify.URGENCY_CRITICAL)
            n.set_timeout(self.notifytimer) 
            if not n.show():
                print "Can't create notify"
#            self.notify("Error", "Sound device is used by another program")
#            msgWindow=gtk.MessageDialog(None,0,gtk.MESSAGE_WARNING,gtk.BUTTONS_CLOSE,'Error')
#            msgWindow.format_secondary_text('Sound device is used by another program' )
#            response=msgWindow.run()
#            msgWindow.destroy()
        
if __name__ == "__main__":
    main()
    gtk.main()
