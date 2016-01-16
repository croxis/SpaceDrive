
from .. import *

from panda3d.core import Camera, OrthographicLens, NodePath, CullFaceAttrib
from panda3d.core import DepthTestAttrib, Vec4, PTALVecBase3, Vec3, Texture

class VoxelizationStage(RenderStage):

    """ This stage voxelizes the whole scene """

    required_inputs = []
    required_pipes = []

    def __init__(self, pipeline):
        RenderStage.__init__(self, "VoxelizationStage", pipeline)
        self._voxel_res = 256
        self._voxel_ws = 50.0
        self._pta_grid_pos = PTALVecBase3.empty_array(1)

    def get_produced_inputs(self):
        return {"VoxelGridPosition": self._pta_grid_pos}

    def get_produced_pipes(self):
        return {"SceneVoxels": self._voxel_grid}
 
    def get_produced_defines(self):
        return {
            "VOXEL_GRID_RES": self._voxel_res,
            "VOXEL_GRID_WS_SIZE": self._voxel_ws,
        }

    def create(self):
        # Create the voxel grid used to store the voxels
        self._voxel_grid = Image.create_3d(
            "Voxels", self._voxel_res, self._voxel_res, self._voxel_res,
            Texture.T_float, Texture.F_r11_g11_b10)
        self._voxel_grid.set_clear_color(Vec4(0))


        # Create the camera for voxelization
        self._voxel_cam = Camera("VoxelizeCam")
        self._voxel_cam.set_camera_mask(self._pipeline.tag_mgr.get_voxelize_mask())
        self._voxel_cam_lens = OrthographicLens()
        self._voxel_cam_lens.set_film_size(-self._voxel_ws, self._voxel_ws)
        self._voxel_cam_lens.set_near_far(0.0, 2.0 * self._voxel_ws)
        self._voxel_cam.set_lens(self._voxel_cam_lens)
        self._voxel_cam_np = Globals.base.render.attach_new_node(self._voxel_cam)
        self._pipeline.tag_mgr.register_voxelize_camera(self._voxel_cam)

        # Create the voxelization target
        self._voxel_target = self._create_target("VoxelizeScene")
        self._voxel_target.set_source(source_cam=self._voxel_cam_np, source_win=Globals.base.win)
        self._voxel_target.set_size(self._voxel_res, self._voxel_res)
        self._voxel_target.set_create_overlay_quad(False)
        self._voxel_target.add_color_texture()
        self._voxel_target.prepare_scene_render()

        # Create the initial state used for rendering voxels
        initial_state = NodePath("VXInitialState")
        initial_state.set_attrib(CullFaceAttrib.make(CullFaceAttrib.M_cull_none), 100000)
        initial_state.set_attrib(DepthTestAttrib.make(DepthTestAttrib.M_none), 100000)
        # initial_state.set_attrib(ColorWriteAttrib.make(ColorWriteAttrib.C_off, 100000))
        self._voxel_cam.set_initial_state(initial_state.get_state())

        Globals.base.render.set_shader_input("voxelGridPosition", self._pta_grid_pos)
        Globals.base.render.set_shader_input("VoxelGridDest", self._voxel_grid.texture)


    def update(self):
        # Position voxelization camera
        grid_position = Vec3(0, 40, 0)
        self._voxel_cam_np.set_pos(grid_position)
        self._voxel_cam_np.look_at(0, 0, 0)
        self._pta_grid_pos[0] = grid_position

      

    def set_shaders(self):
        pass
