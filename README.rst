Linkcheckerjs is the best tool ever to check your websites. It parses the pages using phantomjs in order to detect all the errors even if they come from css or javascript. Linkcheckerjs is free under MIT License.


Installation
============


Requirements
------------

* python >= 2.6

* node & npm: please refer to `node doc <https://nodejs.org/en/download/>`_


Installation via Pip
--------------------

::

    pip install linkcheckerjs


Installation from source
------------------------

::

    cd where_i_want_to_clone_linkcheckerjs

    git clone https://github.com/LeResKP/linkcheckerjs.git

    cd linkcheckerjs

    python setup.py install


Basic usage
===========


To check recursively an URL like 'https://www.python.org' just type the following command in your terminal::

    linkcheckerjs https://www.python.org


.. note::

    The external links (not on the same domain) will not be checked strongly. It's only check the page itself, nor the resources nor the links.



Advanced usage
==============


We will not see the powerful of creating a json and displaying the output separately here since it's in development.
But for now it's just useful when you lost the output of linkcheckerjs command.


You can create a json output when running linkcheckerjs::

    linkcheckerjs https://www.python.org -o /tmp/linkcheckerjs-output.json


To read the generated json, type in your terminal::

    linkreaderjs https://www.python.org -o /tmp/linkcheckerjs-output.json


Build Status
------------

.. |master| image:: https://secure.travis-ci.org/LeResKP/linkcheckerjs.png?branch=master
   :alt: Build Status - master branch
   :target: https://travis-ci.org/#!/LeResKP/linkcheckerjs

.. |develop| image:: https://secure.travis-ci.org/LeResKP/linkcheckerjs.png?branch=develop
   :alt: Build Status - develop branch
   :target: https://travis-ci.org/#!/LeResKP/linkcheckerjs

+----------+-----------+
| Branch   | Status    |
+==========+===========+
| master   | |master|  |
+----------+-----------+
| develop  | |develop| |
+----------+-----------+
