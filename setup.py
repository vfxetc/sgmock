from setuptools import setup, find_packages

setup(
    name='sgmock',
    version='0.1-dev',
    description='Mock Shotgun server for unit testing.',
    url='http://github.com/westernx/sgmock',

    packages=find_packages(exclude=['build*', 'tests*']),

    author='Mike Boers',
    author_email='sgmock@mikeboers.com',
    license='BSD-3',

    entry_points={'console_scripts': '''
        sgmock-server = sgmock.server:main
    '''},
    
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],

)
