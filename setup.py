from setuptools import setup, find_packages

import os
import subprocess
import sys
print("PBR pipeline will now be setup for your system.")
print("If you would like to compile the C++ addon please follow these instructions before continuing:")
print("https://github.com/tobspr/RenderPipeline/wiki/Building-the-CPP-Modules")
input("Press enter to continue")
os.chdir('spacedrive/renderpipeline')
subprocess.call([sys.executable, "setup.py"])
os.chdir('../..')

setup(name='SpaceDrive',
      version='2.0',
      description='Panda3D Space Game Engine. Requires sandbox',
      author='croxis',
      author_email='croxis@gmail.com',
      url='http://croxis.net/',
      install_requires=[
            'pyyaml'
      ],
      package_data={
          ''
          'spacedrive': ['Shader/Planet/*.glsl',
                         'Shader/Scattering/*.include',
                         'Shader/Star/*.glsl',
                         'Skybox/*.egg',
                         'renderpipeline/config/*.yaml',
                         'renderpipeline/config/*.prc',
                         'renderpipeline/data/install.flag',
                         'renderpipeline/data/*/*.png',
                         'renderpipeline/data/builtin_models/skybox/*.*',
                         'renderpipeline/data/default_cubemap/*.*',
                         'renderpipeline/data/default_cubemap/*/*.png',
                         'renderpipeline/data/environment_brdf/*.*',
                         'renderpipeline/data/environment_brdf/*/*.*',
                         'renderpipeline/data/film_grain/*.*',
                         'renderpipeline/data/font/*.*',
                         'renderpipeline/data/gui/*.*',
                         'renderpipeline/data/ies_profiles/*.ies',
                         'renderpipeline/data/ies_profiles/*.IES',
                         'renderpipeline/data/InternalModels/*.bam',
                         'renderpipeline/data/*/*.jpg',
                         'renderpipeline/effects/*.yaml',
                         'renderpipeline/rpcore/native/*.flag',
                         'renderpipeline/rpcore/native/*.so',
                         'renderpipeline/rpcore/shader/*.*',
                         'renderpipeline/rpcore/shader/*/*.*',
                         'renderpipeline/rpplugins/*/*.*',
                         'renderpipeline/rpplugins/*/*/*.*',
                         'renderpipeline/rpplugins/*/*/*/*.*',]
      },
      packages=find_packages(),
      include_package_data=True,
)
