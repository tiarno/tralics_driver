# coding=utf-8
from string import Template
import re

XMLNS = 'http://www.w3.org/1998/Math/MathML'
XMLNS_qname = '{%s}' % XMLNS

bad_elem = Template('''<formula type="display">
  <math xmlns="%s">
    <mtext mathbackground="maroon"
           mathcolor="white">Problem: $error_text (rc = $return_code)</mtext>
    <mtext>$expr</mtext>
  </math>
</formula>''' % XMLNS)

def unescape(s):
    s = s.strip()
    s = s.replace('&lt;', '<',)
    s = s.replace('&gt;', '>',)
    s = s.replace('&amp;', '&',)
    s = s.replace(u'’', u'\'')
    s = s.replace(u'‘', u'\'')
    s = s.replace('\r', '')
    s = s.replace('\n', ' ')
    s = s.replace('\\cr', '\\\\')
    s = re.sub(r'\\\\\s+\\]', '\\]', s)
    if s.startswith(u'\\[') or s.startswith(u'\\begin'):
        s = s + u'\n'
    return s

def escape(s):
    s = s.replace('&', '&amp;')
    s = s.replace('<', '&lt;')
    s = s.replace('>', '&gt;')
    return s
