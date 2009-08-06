
from distutils.core import setup

setup(
    name = 'django-gsb',
    version = '0.1',
    description = "Django interface to Google Safe Browsing API",
    long_description = """Django interface to Google Safe Browsing API.
See the project page for more information:
  http://code.google.com/p/django-gsb/""",
    author = 'Ivan Fedorov',
    author_email = 'oxyum@oxyum.ru',
    url = 'http://code.google.com/p/django-gsb/',
    license = 'MIT License',
    platforms = ['any'],
    packages = ['gsb'],
    classifiers = ['Development Status :: 4 - Beta',
                   'Environment :: Web Environment',
                   'Framework :: Django',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: MIT License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Utilities'],
)
