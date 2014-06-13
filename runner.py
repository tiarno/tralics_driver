from tralics_driver import driver
import tralics_driver
from lxml import etree
import os

'''
This is an example as how you might use the tralics driver.

It retrieves all the images with class="math" in a tree of HTML files and
passes the alt text(presumed to be LaTeX math strings) to the driver.

It creates a new HTML file in the current directory that contains a table
showing the LaTeX math snippet and the resulting MathML in each HTML source
file encountered.

Things to override:
ROOT: path to parent of html directories

functions:
    main
        change the method of locating the source HTML files  to suit your own situation.
        (I have the configuration set and record errors in a MongoDB database).
        Invoke the driver with your own options.

    get_documents
        return a list of directories containing HTML files for processing

    forget_errors
        erase errors encounter in previous run

    record_errors
        record errors encountered in this run
'''

ROOT = '/path/to/html/parent'
MATHJAX = "http://cdn.mathjax.org/mathjax/latest/MathJax.js?config=MML_HTMLorMML"

def get_documents():
    pass

def forget_errors(name):
    pass

def record_errors(error_list):
    pass

def get_mathstring(path):
    files = sorted([x for x in os.listdir(path) if x.endswith('.htm')])
    parser = etree.HTMLParser()
    for fname in files:
        tree = etree.parse(os.path.join(path, fname), parser=parser)
        for image in tree.xpath('//img[@class="math"]'):
            mtext = image.get('alt')
            yield (fname, mtext)

def write_html(title, math):
    page = etree.Element('html')
    doc = etree.ElementTree(page)
    head = etree.SubElement(page, 'head')
    mcss = etree.SubElement(head, 'script', type='text/x-mathjax-config')
    mcss.text = 'MathJax.Hub.Config({displayAlign: "left", displayIndent: "2em"});'
    etree.SubElement(head, 'script', src=MATHJAX, type='text/javascript')
    css = etree.SubElement(head, 'style', type='text/css')
    css.text = '''
        table {width:100%; border: 1px solid navy;font-family: sans-serif;}
        .filename {background-color: #d5e4bc; font-family: sans-serif;}
        .latex {background-color: #c1dcb7; font-family: serif;}
        .mathml {background-color: #bad6c8;}
      '''
    body = etree.SubElement(page, 'body')
    table = etree.SubElement(body, 'table')
    fcol = etree.SubElement(table, 'colgroup', attrib={'class':'filename'})
    etree.SubElement(fcol, 'col')
    lcol = etree.SubElement(table, 'colgroup', attrib={'class':'latex'})
    etree.SubElement(lcol, 'col')
    mcol = etree.SubElement(table, 'colgroup', attrib={'class':'mathml'})
    etree.SubElement(mcol, 'col')

    thead = etree.SubElement(table, 'thead')
    thead_row = etree.SubElement(thead, 'tr')
    for heading in ['Filename', 'LaTeX', 'MathML']:
        h = etree.SubElement(thead_row, 'th')
        h.text = heading
    tbody = etree.SubElement(table, 'tbody')
    lastname = ''
    for fname, mathstring, elemstring in math:
        try:
            elem = etree.fromstring(elemstring)
        except (etree.XMLSyntaxError, ValueError) as e:
            elem = etree.fromstring(tralics_driver.bad_elem.substitute(
                                    {'error_text': str(e),
                                     'expr': tralics_driver.escape(mathstring),
                                     'return_code': 6}))

        tr = etree.SubElement(tbody, 'tr')
        td1 = etree.SubElement(tr, 'td')
        td2 = etree.SubElement(tr, 'td')
        td3 = etree.SubElement(tr, 'td')
        if fname != lastname:
            td1.text = fname

        td2.text = mathstring
        if elem is not None:
            td3.append(elem)

        lastname = fname

    with open('%s_mathml.html' % title, 'wb') as f:
        doc.write(f, pretty_print=True, method='html')


def main():
    doc_dirs = get_documents()
    for doc_dir in doc_dirs:
        forget_errors(doc_dir)
        t = driver.TralicsDriver('/path/to/tralics')
        math = list()

        path = os.path.join(ROOT, doc_dir)
        for fname, mathstring in get_mathstring(path):
            elemstring = t.convert(fname, mathstring)
            math.append((fname, mathstring, elemstring))
        record_errors(t.errors)
        t.stop()
        write_html(doc_dir, math)


if __name__ == '__main__':
    main()
    print

'''
To replace the image elements with the mathml element:
try:
    math_elem = etree.fromstring(elemstring)
except etree.XMLSyntaxError as e:
    print e
else:
    image.getparent().replace(image, math_elem)
'''