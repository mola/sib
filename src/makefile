PKGDIR = /usr/share/sib

all: 
	@../tools/py-compile *.py 

clean:
	rm -fv *.pyc *.pyo *~ *.bak *.gladep *.o *.so

install:
	mkdir -p $(DESTDIR)/usr/share/sib
	install -m755 *.pyc $(DESTDIR)/$(PKGDIR)/.
	install -m755 *.py $(DESTDIR)/$(PKGDIR)/.
	install -m644 interface.glade $(DESTDIR)/$(PKGDIR)/.
	install -m644 generic.sdb $(DESTDIR)/$(PKGDIR)/.
