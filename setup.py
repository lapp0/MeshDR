from setuptools import setup


setup(
    name='meshdr',
    description='',
    author='Andrew Lapp',
    author_email='andrew@robochef.rew.la',
    url='',
    packages=[
        'meshdr'
    ],
    entry_points={
        'console_scripts': [
            'meshdr=meshdr.meshdr:main'
        ]
    }
)
