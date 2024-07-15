from setuptools import setup, find_packages
setup(name='hazimp',
      version='1.3',
      packages=find_packages(),
      entry_points=dict(console_scripts=['hazimp=hazimp.main:cli']),
      author="Geoscience Australia",
      author_email="hazards@ga.gov.au",
      description="HazImp - Hazard-Impact assessment tool",
      url="https://hazimp.readthedocs.io/")
