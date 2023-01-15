from html.parser import HTMLParser
from datetime import date
import time

class MyHTMLParser(HTMLParser):
    allhtml = ""
    baseurl = "http://site.ru"
    todate = date.fromtimestamp(time.time())

    def handle_starttag(self, tag, attrs):
        for attr in attrs:
            if (tag == "a" and attr[0] == "href"):
                self.allhtml +="<url><loc>" + self.baseurl + attr[1] + "</loc><lastmod>" + self.todate.isoformat() + "</lastmod></url>\r\n"

parser = MyHTMLParser()
parser.feed('<div>put html with links here <a href="/boo.html">link</a>,<a href="/foo.html">link 2</a>,</div>')
print(parser.allhtml)
