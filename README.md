tralics_driver
==============

Driver for Tralics: Convert LaTeX math snippets to MathML elements

*Note*: Tralics is a LaTeX to XML Translator from http://www-sop.inria.fr/marelle/tralics/
This is only a driver.

Requirements
-------------

  * Python 2.6 or greater
  * Pexpect package
  * Tralics installation
  
What does it do?
----------------

The problem this project attempts to solve is when you have a bunch of LaTeX math 
snippets (inline or block math) and you want to convert them to MathML. It all started 
because I want to create ``epub`` documents from LaTeX source that can be read in an e-reader.
That means I need my math to be in MathML.

For example, once this project is running, you'll be able to write code like this::

    math_elements = list()
    
    driver = TralicsDriver()
    for s in latex_strings:
        formula = driver.getmath(s)
        math_elements.append(clean_formula(formula))
    driver.stop()
    
    do_something(math_elements)
    
Assumptions
------------

  * You have installed Tralics
  * If you have custom ``newcommand``s defined, you put them in a file ``newcommands.tex`` and place that file in the Tralics ``conf`` directory.
  * You want to cache your string conversions and you're willing to pickle them on disk (you could use a database, but you'll need to make the modifications for that yourself). I use MongoDB for my own project but I didn't want to add that dependency to this project. File caching works fine.

In my own version of this project, I walk through a tree of HTML files that were generated from LaTeX source; the math in that LaTeX source was rendered to PNG images and the ``alt`` text on each image contains the LaTeX source corresponding to the image. 

I gather all the math snippets embedded in the HTML ``alt`` text and pass them through the ``TralicsDriver`` in order to replace the image with a MathML element.

So I start with HTML that has images and LaTeX snippets for alt text; I end up with HTML + MathML. The reason for all this work is to produce ``epub`` documents that contain MathML. 

Although browsers support MathJax rendering (http://mathjax.org) of LaTeX inside HTML, apparently e-readers do not.
From what I have heard, MathJax works inside many ereaders when the math is in MathML.



        
