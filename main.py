"""






-------------------------------------------------------------------------------
--
--   WARNING
--
--   This file exists for testing purposes only!
--   It is not supposed to be run by the user. Please have a look at the samples
--   provided at Samples/.
--
--
-------------------------------------------------------------------------------





"""


from __future__ import print_function

import sys
import getpass



from direct.showbase.ShowBase import ShowBase
from panda3d.core import Vec3

from __init__ import *
from Code.Util.MovementController import MovementController


# This check is required, because many people downloading the pipeline think this
# is the mainfile, while its only my main testing file. So this check here
# is to avoid confusion.
if len(sys.argv) != 2 or sys.argv[1] != "dev":
    if getpass.getuser() != "tspringe":
        print("This file is not meant to be run by the user!")
        print("Please have a look at the samples located at Samples/")
        sys.exit(0)


class MainApp(ShowBase):

    """ Main Testing Showbase """

    def __init__(self):

        self.render_pipeline = RenderPipeline(self)
        self.render_pipeline.set_default_loading_screen()

        # Set the base path and mount the directories
        self.render_pipeline.get_mount_manager().set_write_path("Temp")
        self.render_pipeline.get_mount_manager().disable_cleanup()
        self.render_pipeline.get_mount_manager().mount()

        # Load the default prc file and settings
        self.render_pipeline.load_settings("Config/pipeline.yaml")

        # Create the pipeline
        self.render_pipeline.create()

        profile = self.render_pipeline.load_ies_profile("Data/IESProfiles/Defined.ies")

        plane = self.loader.loadModel("Data/BuiltinModels/Plane/Plane.bam")
        plane.set_scale(2.0)
        plane.reparent_to(render)

        # Load some models, most of them are not included in the repository
        model = self.loader.loadModel("Models/MaterialTester.ignore/Scene.bam")
        # model = loader.loadModel("Models/HDRTest/Scene.bam")
        # model = loader.loadModel("Models/SimpleShapes/Sphere.bam")
        # model = loader.loadModel("Models/SimpleShapes/Wall.bam")
        # model = loader.loadModel("Models/Test.ignore/Statue.bam")
        # model = loader.loadModel("Models/Test.ignore/Car0.bam")
        # model = loader.loadModel("Models/DemoTerrain/Scene.bam")
        # model = loader.loadModel("Models/Sponza.ignore/Scene.bam")
        # model = loader.loadModel("box")
        model.flatten_strong()

        if False:
            render.set_shader_input("roughness", 1.0)
            render.set_shader_input("metallic", 0.0)
            render.set_shader_input("specular", 0.05)

            for roughness in range(11):
                for metallic in range(2):
                    placeholder = render.attach_new_node("placeholder")
                    placeholder.set_pos((roughness-5) * 2.3, (metallic) * 5.3, 0)
                    placeholder.set_shader_input("roughness", roughness / 10.0)
                    placeholder.set_shader_input("metallic", metallic / 1.0)
                    model.instance_to(placeholder)
        else:
            model.reparent_to(render)

        self.render_pipeline.create_default_skybox()

        # Add some random lights
        sqr = 0
        for x in range(sqr):
            for y in range(sqr):
                light = PointLight()
                pos_x, pos_y = (x-sqr//2) * 6.0, (y-sqr//2) * 4.0
                # pos_x, pos_y = 0, 0
                light.set_pos(Vec3(pos_x, pos_y, 3.0))
                # light.set_color(Vec3(random(), random(), random())* 1.0)
                light.set_color(Vec3(3, 3, 3))
                light.set_radius(5)
                light.set_ies_profile(profile)
                self.render_pipeline.add_light(light)

        if False:
            test_light = SpotLight()
            test_light.set_pos(0, 9, 15)
            test_light.set_radius(30)
            test_light.set_color(Vec3(1.0, 1.0, 1.0) * 4.0)
            test_light.look_at(0, 0, 0)
            test_light.set_fov(90)
            test_light.set_ies_profile(0)
            self.render_pipeline.add_light(test_light)

        # Init movement controller
        self.controller = MovementController(self)
        self.controller.set_initial_position(Vec3(10), Vec3(0))
        # self.controller.set_initial_position(Vec3(0, 0, 100), Vec3(0))
        self.controller.setup()

MainApp().run()
