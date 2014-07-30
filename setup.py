from setuptools import setup, find_packages

setup(name='SpaceDrive',
      version='1.1',
      description='Panda3D Space Game Engine. Requires sandbox',
      author='croxis',
      author_email='croxis@gmail.com',
      url='http://croxis.net/',
      package_data={
          ''
          'spacedrive': ['Shader/Star/*.glsl',
                         'renderpipeline/Data/Antialiasing/*.png',
                         'renderpipeline/Data/Cubemaps/Default/*.png',
                         'renderpipeline/Data/Cubemaps/DirectionLookup/*.png',
                         'renderpipeline/Data/GUI/*.png',
                         'renderpipeline/Shader/*.fragment',
                         'renderpipeline/Shader/*.vertex',
                         'renderpipeline/Shader/DefaultShadowCaster/*.glsl',
                         'renderpipeline/Shader/Includes/*.include',
                         'renderpipeline/Shader/Occlusion/*.include',
                         'renderpipeline/Shader/SMAA/*.fragment',
                         'renderpipeline/Shader/SMAA/*.vertex',]
      },
      packages=find_packages(),
      include_package_data=True,
)
