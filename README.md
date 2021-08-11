HazImp
======

A natural hazard impact assessment tool.

For the latest documentation, installation guide and user guide, see https://hazimp.readthedocs.io
[![Documentation Status](https://readthedocs.org/projects/hazimp/badge/?version=latest)](https://hazimp.readthedocs.io/en/latest/?badge=latest)

This branch enables users to develop new functions for HazImp.

Status
------------

[![Unit tests for HazImp (master branch)](https://github.com/GeoscienceAustralia/hazimp/actions/workflows/hazimp-tests.yml/badge.svg?branch=master)](https://github.com/GeoscienceAustralia/hazimp/actions/workflows/hazimp-tests.yml)
[![Unit tests for HazImp (develop branch)](https://github.com/GeoscienceAustralia/hazimp/actions/workflows/hazimp-tests.yml/badge.svg?branch=develop)](https://github.com/GeoscienceAustralia/hazimp/actions/workflows/hazimp-tests.yml)
[![Documentation Status](https://readthedocs.org/projects/hazimp/badge/?version=latest)](https://hazimp.readthedocs.io/en/latest/?badge=latest)
[![codecov](https://codecov.io/gh/GeoscienceAustralia/hazimp/branch/master/graph/badge.svg?token=YPcgBIMxts)](https://codecov.io/gh/GeoscienceAustralia/hazimp)

Data
==== 

All exposure and hazard data under version control is for
testing purposes only and should not be considered as realistic.  The
provenance for this data is unknown.

Contributing code
=================

Generally, development of new functionality and bug fixes happens in
the `develop` branch in HazImp.  The `master` branch is only for
significant releases, and maintenance. Even then, any bug-fixes should
follow the procedure outlined below to contribute fixes - that is,
create a new (temporary) branch, make the fix, then submit teh fix as
a pull request. Once the pull request has been approved and merged,
the temporary branch can be deleted.

The preferred way to contribute to HazImp is to fork the 
[main repository](http://github.com/GeoscienceAustralia/hazimp) on GitHub:

1. Fork the [project repository](http://github.com/GeoscienceAustralia/hazimp):
   click on the 'Fork' button near the top of the page. This creates
   a copy of the code under your account on the GitHub server.

2. Clone this copy to your local disk::
          $ git clone git@github.com:YourLogin/hazimp.git
          $ cd hazimp

3. Create a branch to hold your changes::

          $ git checkout -b my-feature

   and start making changes. Never work in the ``master`` branch! We recommend
   starting from the ``develop`` branch, where we do our development work. 

4. Check the code using the unit test suite. This will also run a quick check of
   the code syntax using ``pycodestyle``::

         $ nosetests -v --exe

   If this passes with no errors, then you can commit the changes.

5. Work on this copy on your computer using Git to do the version
   control. When you're done editing, do::

          $ git add modified_files
          $ git commit

   to record your changes in Git, then push them to GitHub with::

          $ git push -u origin my-feature

Finally, go to the web page of your fork of the hazimp repo,
and click 'Pull request' to send your changes to the maintainers for
review. request. This will send an email to the committers.

(If any of the above seems like magic to you, then look up the 
[Git documentation](http://git-scm.com/documentation) on the web.)

It is recommended to check that your contribution complies with the
following rules before submitting a pull request:

-  All public methods should have informative docstrings with sample
   usage presented as doctests when appropriate.

-  When adding additional functionality, provide at least one
   example script in the ``examples/`` folder. Have a look at other
   examples for reference. Examples should demonstrate why the new
   functionality is useful in practice.

-  At least one paragraph of narrative documentation with links to
   references in the literature (with PDF links when possible) and
   an example.

You can also check for common programming errors with the following
tools:

-  Code with good unittest coverage, check with::

          $ pip install nose coverage --user
          $ nosetests --with-coverage path/to/tests_for_package

-  No pyflakes warnings, check with::

           $ pip install pyflakes
           $ pyflakes path/to/module.py

-  No PEP8 warnings, check with::

           $ pip install pep8
           $ pep8 path/to/module.py

-  AutoPEP8 can help you fix some of the easy redundant errors::

           $ pip install autopep8
           $ autopep8 path/to/pep8.py

Issues
------

A great way to start contributing to HazImp is to pick an item
from the list of [Issues](https://github.com/GeoscienceAustralia/hazimp/issues)
in the issue tracker. (Well there are none there yet, but we will be 
putting some up soon!) Resolving these issues allow you to start
contributing to the project without much prior knowledge. Your
assistance in this area will be greatly appreciated by the more
experienced developers as it helps free up their time to concentrate on
other issues.

Documentation
-------------

We are in the process of creating sphinx based documentation for HazImp. 
Any help in setting this up will be gratefully accepted!

At present you will find the user_manual in the docs folder. 

We are glad to accept any sort of documentation: function docstrings,
reStructuredText documents (like this one), tutorials, etc.
reStructuredText documents (will) live in the source code repository under the
docs/ directory.

When you are writing documentation, it is important to keep a good
compromise between mathematical and algorithmic details, and give
intuition to the reader on what the algorithm does. It is best to always
start with a small paragraph with a hand-waving explanation of what the
method does to the data and a figure (coming from an example)
illustrating it.
