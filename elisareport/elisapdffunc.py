from reportlab.platypus import *
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm, inch
from reportlab.lib.styles import getSampleStyleSheet, TA_CENTER

normal = getSampleStyleSheet()["Normal"]
normal.fontSize += 2
centered = getSampleStyleSheet()["Normal"]
centered.fontSize += 2
centered.alignment = TA_CENTER

#from jkominek/chematox/general.py
#puts the address block and the header on to a page
def header(title):
    chematoxheader = ["ChemaTox Laboratory, Inc.",
                      "PO Box 20590, Boulder, CO 80308",
                      "303-440-4500"]

    page = map(lambda l: Paragraph(l, centered), chematoxheader)

    page.append(Spacer(0, 72*.25))
    page.append(Paragraph("<font size='+3'>"+title+"</font>", centered))

    page.append(Spacer(0, 72*.25))

    return page

#from jkominek/chematox/general.py
#bolds text for a row
def bolder(x):
    if len(x):
        return Paragraph("<b>%s</b>" % (x,), centered)
    else:
        return x

#from jkominek/chematox/general.py
#sets up canvas which has infromation on the bottom
def generateNumberedCanvasClass(initials, gentime, run):
    class NumberedCanvas(canvas.Canvas):
        def __init__(self, *args, **kwargs):
            canvas.Canvas.__init__(self, *args, **kwargs)
            self._saved_page_states = []

        def showPage(self):
            self._saved_page_states.append(dict(self.__dict__))
            self._startPage()

        def save(self):
            """add page info to each page (page x of y)"""
            num_pages = len(self._saved_page_states)
            for state in self._saved_page_states:
                self.__dict__.update(state)
                self.draw_page_number(num_pages)
                canvas.Canvas.showPage(self)
            canvas.Canvas.save(self)

        def draw_page_number(self, page_count):
            self.setFont("Times-Roman", 11)
            self.drawString(1*inch, 1*inch,
                            "Testing analyst initials: %s (Run: %s)" % (initials, str(run)))
            self.drawCentredString(5.25*inch, 1*inch,
                                    "Report Generated: "+gentime)
            self.drawRightString(7.5*inch, 1*inch,
                                 "Page %d of %d" % \
                                     (self._pageNumber, page_count))
    return NumberedCanvas
