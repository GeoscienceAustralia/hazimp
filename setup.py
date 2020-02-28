import setuptools
setuptools.setup(name='hazimp',
                 packages=setuptools.find_packages(),
                 entry_points = dict(console_scripts=['hazimp=hazimp.main:cli']))
