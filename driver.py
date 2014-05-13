from string import Template
from xml.etree import ElementTree as etree
import os
import pexpect
try:
   import cPickle as pickle
except:
   import pickle

XMLNS = 'http://www.w3.org/1998/Math/MathML'
XMLNS_qname = '{%s}' % XMLNS
etree.register_namespace('', XMLNS)

bad_elem = Template('''<formula type="display">
  <math xmlns="%s">
    <mtext mathbackground="maroon"
           mathcolor="white">Problem: $error_text (rc = $return_code)</mtext>
  </math>
</formula>''' % XMLNS)

class TralicsDriver(object):
    def __init__(self, tralics_dir):
        binary = os.path.join(tralics_dir, 'bin', 'tralics')
        cfgdir = os.path.join(tralics_dir, 'conf', 'tralics')
        self.newcommands = os.path.join(cfgdir, 'newcommands')
        self.tralics_cmd = '%s -interactivemath -noentnames -confdir %s' % (binary, cfgdir)

        self.pickle_cache = os.path.join(cfgdir, 'cache.pkl')
        if os.path.isfile(self.pickle_cache):
            with open(self.pickle_cache) as f:
                self.cache = pickle.load(f)
        else:
            self.cache = dict()
        self.started = False

    def start(self):
        self.child = pexpect.spawn(self.tralics_cmd)
        self.child.expect('> ')
        self.child.send('\\usepackage{amsmath}\n')
        self.child.expect('> ')
        if os.path.isfile('%s.tex' % self.newcommands):
            self.child.send('\\input{%s}\n' % self.newcommands)
            self.child.expect('> ')
        self.started = True

    def convert(self, mathstring):
        '''Driver entry point'''
        s = self.cache.get(mathstring)
        if not s:
            if not self.started:
                self.start()
            s = self.getmath(mathstring)
        else:
            print 'GOT CACHED'
        return self.clean_formula(s)

    def getmath(self, expr):
        self.child.sendline(expr)
        rc = self.child.expect(['<formula.*formula>', pexpect.EOF, pexpect.TIMEOUT])
        if rc:
            s = bad_elem.substitute({'error_text': expr, 'return_code': rc})
        else:
            text_before = self.child.before.strip()
            result = self.child.after.strip()
            error_found = text_before.find('Error')

            if error_found != -1:
                error_text = text_before[error_found:].replace('\n','')
                s = bad_elem.substitute({'error_text': error_text, 'return_code': '3'})
            else:
                self.cache[expr] = result
                s = result
        return s

    def clean_formula(self, formula_string):
        formula = etree.fromstring(formula_string)
        elem = formula.find('%smath' % XMLNS_qname)
        if formula.attrib.get('type') == 'display':
            elem.attrib['display'] = 'block'
        else:
            elem.attrib['display'] = 'inline'

        if elem.attrib.get('mode'):
            del elem.attrib['mode']

        return elem

    def stop(self):
        if self.started:
            self.child.close()
            with open(self.pickle_cache, 'wb') as f:
                pickle.dump(self.cache, f)

def main():
    test_math = [
    '$x+y=\sqrt{z}$', '$\\mathrm{x} = 1.0$', '$\\mathsf{h}_0 = 0$',
    '$x+y=\sqrt{z}$',
    '\\begin{align*}x &= y\\\\ z &= w\end{align*}',
    '$\\mytest + y$',
    '$\sum_x^y z = 0$'
    ]

    t = TralicsDriver('/usr/local')
    for mathstring in test_math:
        elem = t.convert(mathstring)
        print etree.tostring(elem)
        print
    t.stop()

if __name__ == '__main__':
    main()