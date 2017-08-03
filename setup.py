import pip.download
from pip.req import parse_requirements
from setuptools import setup, find_packages


def get_requirements():
    requirements = parse_requirements(
        'requirements.txt',
        session=pip.download.PipSession()
    )
    return [str(r.req) for r in list(requirements)]


setup(
    name='avs_client',
    version='0.2.0',
    url='https://github.com/richtier/alexa-voice-service-client',
    license='MIT',
    author='Richard Tier',
    description='Python Client for Alexa Voice Service (AVS)',
    packages=find_packages(),
    long_description=open('README.md').read(),
    include_package_data=True,
    install_requires=get_requirements(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
