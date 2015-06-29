from setuptools import setup, find_packages

setup(name='SpaceDrive',
      version='1.2',
      description='Panda3D Space Game Engine. Requires sandbox',
      author='croxis',
      author_email='croxis@gmail.com',
      url='http://croxis.net/',
      package_data={
          ''
          'spacedrive': ['Shader/Planet/*.glsl',
                         'Shader/Scattering/*.include',
                         'Shader/Star/*.glsl',
                         'renderpipeline/Config/*.ini',
                         'renderpipeline/Config/*.prc',
                         'renderpipeline/Data/*/*.png',
                         'renderpipeline/Data/Cubemaps/*/*.png',
                         'renderpipeline/Data/Font/*.otf',
                         'renderpipeline/Data/GUI/Visualization/*.png',
                         'renderpipeline/Data/IESProfiles/*.ies',
                         'renderpipeline/Data/IESProfiles/*.IES',
                         'renderpipeline/Models/*/*.bam',
                         'renderpipeline/Models/Plane/textures/*.png',
                         'renderpipeline/Shader/*.compute',
                         'renderpipeline/Shader/*.fragment',
                         'renderpipeline/Shader/*.vertex',
                         'renderpipeline/Shader/Antialiasing/*/*.fragment',
                         'renderpipeline/Shader/Antialiasing/*/*.vertex',
                         'renderpipeline/Shader/DefaultShaders/*/*.glsl',
                         'renderpipeline/Shader/DefaultShadowCaster/*.glsl',
                         'renderpipeline/Shader/GI/*.fragment',
                         'renderpipeline/Shader/GI/*.include',
                         'renderpipeline/Shader/GI/*.vertex',
                         'renderpipeline/Shader/Includes/*.include',
                         'renderpipeline/Shader/Includes/Structures/*.struct',
                         'renderpipeline/Shader/Occlusion/*.include',
                         'renderpipeline/Shader/Scattering/*.fragment',
                         'renderpipeline/Shader/Scattering/*.geometry',
                         'renderpipeline/Shader/Scattering/*.vertex',
                         'renderpipeline/Shader/Skybox/*.glsl',]
      },
      packages=find_packages(),
      include_package_data=True,
)
