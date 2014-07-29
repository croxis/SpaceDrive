from setuptools import setup, find_packages

setup(name='SpaceDrive',
      version='1.1',
      description='Panda3D Space Game Engine. Requires sandbox',
      author='croxis',
      author_email='croxis@gmail.com',
      url='http://www.python.org/sigs/distutils-sig/',
      package_data={
          'spacedrive': ['renderpipeline/Data/Antialiasing/*.png',
                         'renderpipeline/Data/Cubemaps/Default/*.png',
                         'renderpipeline/Data/Cubemaps/DirectionLookup/*.png',
                         'renderpipeline/Data/GUI/*.png',]
      },
      packages=find_packages(),
      include_package_data=True,
)
