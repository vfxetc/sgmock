from distutils.core import setup

setup(
    name='sgmock',
    version='0.1-dev',
    description='Mock Shotgun server for unit testing.',
    url='http://github.com/westernx/sgmock',
    
    packages=['sgmock'],
    
    author='Mike Boers',
    author_email='sgmock@mikeboers.com',
    license='BSD-3',
    
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    
)