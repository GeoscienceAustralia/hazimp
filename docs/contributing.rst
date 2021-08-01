.. _contributing: 

=================
Contributing code
=================

The preferred way to contribute to HazImp is to fork the 
`main repository <http://github.com/GeoscienceAustralia/hazimp>`_ on GitHub:

1. Fork the `project repository <http://github.com/GeoscienceAustralia/hazimp>`_:
   click on the 'Fork' button near the top of the page. This creates
   a copy of the code under your account on the GitHub server.

2. Clone this copy to your local disk (using ssh commands)::

          $ git clone git@github.com:YourLogin/hazimp.git
          $ cd hazimp

3. Create a branch to hold your changes::

          $ git checkout -b my-feature

   and start making changes. Never work in the ``master`` branch!

4. Work on this copy on your computer using Git to do the version
   control. When you're done editing, do::

          $ git add modified_files
          $ git commit

   to record your changes in Git, then push them to GitHub with::

          $ git push -u origin my-feature

Finally, go to the web page of the your fork of the hazimp repo,
and click 'Pull request' to send your changes to the maintainers for
review. This will send an email to the committers. **Pull requests should
only be made against the 'develop' branch of the repository.** Pull requests
against the 'master' branch will be refused and requested to resubmit against
the 'develop' branch.

A demonstration of the git workflow used for HazImp can be seen at
https://leanpub.com/git-flow/read.  

(If any of the above seems like magic to you, then look up the 
`Git documentation <http://git-scm.com/documentation>`_ on the web.)

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

-  Include clear provenance statements in any new functionality that generates
   output, using the `'prov' library <https://prov.readthedocs.io/>`_.

You can also check for common programming errors with the following
tools:

-  Code with good unittest coverage, check with::

          $ pip install nose coverage
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
from the list of `Issues <https://github.com/GeoscienceAustralia/hazimp/issues>`_
in the issue tracker. Resolving these issues allow you to start
contributing to the project without much prior knowledge. Your
assistance in this area will be greatly appreciated by the more
experienced developers as it helps free up their time to concentrate on
other issues.

Documentation
-------------

We use sphinx-doc_ for creating documentation for HazImp. reStructuredText
files are stored in the `docs` folder, while function docstrings are embedded in
the code base.

Running Sphinx
~~~~~~~~~~~~~~

If using a conda_ environment to run HazImp, users may need to set the
`SPHINXBUILD` environment variable to point to the correct `sphinx-build.exe`
executable. 

To build the HTML pages on your local computer, use the `make html` command.

On Windows::

    set SPHINXBUILD=%CONDAPATH%\envs\hazimp\Scripts\sphinx-build.exe
    make html

On bash::

    export SPHINXBUILD=$CONDAPATH/envs/hazimp/scripts/sphinx-build
    make html

Check the output for any error messages, then open the created docs in
`_build/html/index.html`. 

See the sphinx-doc_ pages for more details on using Sphinx Python Documentation
Generator.


.. _conda: https://conda.io/en/latest/index.html
.. _sphinx-doc: https://www.sphinx-doc.org/en/master/