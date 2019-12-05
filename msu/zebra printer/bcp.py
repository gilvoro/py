import win32print

def zebraprint(pname, label):
    ll = len(label)/2
    los = 200 - (10*ll)
    bos = 200 - (10*(ll+2))                                                                                                                                                                                                                                                                                                                                                                                               - (5*ll)
    text = '^XA^FO%s,20^BY1,3^B3N,N,60,N,N^FD%s^FS^FO%s,85^ADN36,20^FD%s^FS^XZ' % (str(bos), label, str(los), label)
    data = (text).encode()
    print(data)

    printer = win32print.OpenPrinter(pname)

    win32print.StartDocPrinter(printer,1,("simple label",None,'RAW'))
    win32print.StartPagePrinter(printer)
    win32print.WritePrinter(printer,data)
    win32print.EndPagePrinter(printer)
    win32print.EndDocPrinter(printer)
    win32print.ClosePrinter(printer)
