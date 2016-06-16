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
import gtk
import gtk.glade
import os

Optionfile="/sib.conf"
Option = {'notifytimer':5000,
          'searchontype':True,
          'history':10,
          'Dfont':False,
          'Sfont':None}

def get_home():
    home = os.environ.get('HOME', '')
    return home+"/.sib"
    
def option_parse():
    home = get_home()
    if os.path.isfile(home+Optionfile):
        sibconf = open(home+Optionfile, 'r')
        for element in sibconf:
            sin,sout = element.split(' = ')
            Option[sin] = sout[:-1]
        sibconf.close()
                
class prefrence:
    def __init__(self,datadir,pixdir,dsearch,dtime,dhist,Dfont,Sfont):
        self.glade=gtk.glade.XML(datadir+"/interface.glade","Preference")
        self.dlg=self.glade.get_widget("Preference")
        dict = {"on_preference_close":self.cancel,
              "on_cancelbutton1_clicked":self.cancel,
              "on_okbutton1_clicked":self.close,
              "on_radiobutton_changed":self.groupchange,
              "on_fontselection1_set_focus_child":self.fontselection, 
              }
        self.glade.signal_autoconnect(dict)      
        
        self.spin1 = self.glade.get_widget("spinbutton1")
        self.spin2 = self.glade.get_widget("spinbutton2")
        self.checkbutton = self.glade.get_widget("checkbutton1")
        self.font_sel = self.glade.get_widget("fontselection1")
        self.checkbutton.set_active(dsearch)
        self.spin1.set_value(dtime/1000)
        self.spin2.set_value(dhist)
        
        self.Dfont=Dfont
        self.Sfont=Sfont
        if Dfont:
            self.glade.get_widget("radiobutton2").set_active(True)
            self.font_sel.set_sensitive(True)
            self.font_sel.set_font_name(Sfont)
            
        
        self.image= gtk.Image()
        self.image.set_from_file(pixdir+"/sib.png")
        
        if os.path.exists(get_home())==False:
            os.mkdir(get_home())
        

    def close(self, obj, data=None):
        global Option
        home = get_home()
        timer = self.spin1.get_value_as_int()*1000
        history = self.spin2.get_value_as_int()
        search = self.checkbutton.get_active()
        
        Option['searchontype']=search
        Option['notifytimer']=timer
        Option['history']=history
        Option['Dfont']=self.Dfont
        Option['Sfont']=self.Sfont

        sibconf=open(home+Optionfile,'w')
        sibconf.write('notifytimer = '+str(timer)+'\n')
        sibconf.write('history = '+str(history)+'\n')
        sibconf.write('searchontype = '+str(search)+'\n')
        sibconf.write('Dfont = '+str(self.Dfont)+'\n')
        sibconf.write('Sfont = '+str(self.Sfont)+'\n')
        sibconf.close()
        
        return 1
    
    def cancel(self, obj, data=None):
        self.dlg.destroy()
    
    def groupchange(self, obj, data=None):
        if obj.get_name()=="radiobutton2":
            self.font_sel.set_sensitive(True)
            self.Dfont =True
            self.Sfont = self.font_sel.get_font_name()
            return
        elif obj.get_name()=="radiobutton1":
            self.font_sel.set_sensitive(False)
            self.Dfont=False
    
    def fontselection(self, obj, data=None):
        self.Sfont = obj.get_font_name()
