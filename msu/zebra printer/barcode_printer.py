import win32print

def zebraprintbc(pname, label):
    ll = len(label)/2
    los = 200 - (12*ll)
    bos = 200 - (7*(ll+3))                                                                                                                                                                                                                                                                                                                                                                                               - (5*ll)
    text = '^XA^FO%s,20^BY1,2^B3N,N,60,N,N^FD%s^FS^FO%s,85^ADN,18,10^FD%s^FS^XZ' % (str(bos), label, str(los), label)
    data = (text).encode()

    printer = win32print.OpenPrinter(pname)

    win32print.StartDocPrinter(printer,1,("simple label",None,'RAW'))
    win32print.StartPagePrinter(printer)
    win32print.WritePrinter(printer,data)
    win32print.EndPagePrinter(printer)
    win32print.EndDocPrinter(printer)
    win32print.ClosePrinter(printer)

def zebraprint(pname, label):
    labelparts = label.split(';')
    if len(labelparts) > 2:
        print('No can do boss')
    elif len(labelparts) == 2:
        text = '^XA^FO80,25^A0N,42,28^FD%s^FS^FO80,65^A0N,42,28^FD%s^FS^XZ' % (labelparts[0],labelparts[1])
    else:
        text = '^XA^FO80,40^A0N,42,28^FD%s^FS^XZ' % (labelparts[0])
    data = (text).encode()

    printer = win32print.OpenPrinter(pname)

    win32print.StartDocPrinter(printer,1,("simple label",None,'RAW'))
    win32print.StartPagePrinter(printer)
    win32print.WritePrinter(printer,data)
    win32print.EndPagePrinter(printer)
    win32print.EndDocPrinter(printer)
    win32print.ClosePrinter(printer)
