SUBDIRS = src
PYFILES = $(wildcard *.py)
PKGNAME = sib
VERSION = 0.1
PYTHON = python
SRCDIR = src
MISCDIR=misc
PIXDIR = pixmaps

subdirs:
	for d in $(SUBDIRS); do make -C $$d; [ $$? = 0 ] || exit 1 ; done

clean:
	for d in $(SUBDIRS); do make -C $$d clean ; done

install:
	mkdir -p $(DESTDIR)/usr/share/sib
	mkdir -p $(DESTDIR)/usr/share/pixmaps/sib
	mkdir -p $(DESTDIR)/usr/share/applications
	mkdir -p $(DESTDIR)/usr/share/gnome/autostart
	mkdir -p $(DESTDIR)/usr/bin
	install -m644 COPYING $(DESTDIR)/usr/share/sib/.
	install -m644 $(PIXDIR)/*.png $(DESTDIR)/usr/share/pixmaps/sib/.
	install -m755 $(MISCDIR)/sib $(DESTDIR)/usr/bin/.
	chmod +x $(DESTDIR)/usr/bin/sib
	install -m644 $(MISCDIR)/sib.desktop $(DESTDIR)/usr/share/applications/.
	install -m644 $(MISCDIR)/sib-applet.desktop $(DESTDIR)/usr/share/gnome/autostart
	for d in $(SUBDIRS); do make DESTDIR=$(DESTDIR) -C $$d install; [ $$? = 0 ] || exit 1; done
