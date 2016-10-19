from setuptools import setup

setup(name='upnp_discovery',
      version='0.1',
      description='Simple UPnP discovery library',
      url='http://somelibrary.com',
      author='Derek Barnhart',
      author_email='Derek.Barnhart@neustar.biz',
      license='MIT',
      packages=['discovery'],
      install_requires=[
          'twisted',
      ],
      zip_safe=False,
      )
