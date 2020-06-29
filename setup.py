import setuptools
setuptools.setup(name='hazimp',
                 version='0.3'
                 packages=setuptools.find_packages(),
                 entry_points = dict(console_scripts=['hazimp=hazimp.main:cli']),
                 
                 # metadata:
                 author = "Craig Arthur",
                 author_email = "craig.arthur@ga.gov.au",
                 description = "HazImp - Hazard-Impact assessment tool",
                 url = "https://hazimp.readthedocs.io/")
