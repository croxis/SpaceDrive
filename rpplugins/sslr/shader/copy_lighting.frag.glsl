/**
 *
 * RenderPipeline
 *
 * Copyright (c) 2014-2016 tobspr <tobias.springer1@gmail.com>
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 *
 */

#version 430

#define USE_MAIN_SCENE_DATA
#define USE_GBUFFER_EXTENSIONS
#pragma include "render_pipeline_base.inc.glsl"
#pragma include "includes/color_spaces.inc.glsl"
#pragma include "includes/gbuffer.inc.glsl"
#pragma include "includes/transforms.inc.glsl"

uniform sampler2D CombinedVelocity;
uniform writeonly image2D RESTRICT DestTex;
uniform sampler2D Previous_PostAmbientScene;
uniform sampler2D Previous_SceneDepth;

// Copies the previous scene color to the first sslr mipmap.
// Also outputs the current frame intersection depth

void main() {
  vec2 texcoord = get_texcoord();
  vec2 velocity = texture(CombinedVelocity, texcoord).xy;
  vec2 last_coord = texcoord + velocity;

  // Out of screen, can early out
  if (out_of_screen(last_coord)) {
    imageStore(DestTex, ivec2(gl_FragCoord.xy), vec4(0));
    return;
  }

  float fade = 1.0;

  // Check if reprojected position matches
  float curr_depth = get_depth_at(texcoord);

  // Fade out skybox
  if (get_linear_z_from_z(curr_depth) > 3000.0) {
    fade = 0.0;
  }

  float last_depth = textureLod(Previous_SceneDepth, texcoord, 0).x;
  vec3 curr_pos = calculate_surface_pos(curr_depth, texcoord);

  // XXX: inverse is totally slow! Instead pass it as a main scene data
  vec3 last_pos = calculate_surface_pos(last_depth, last_coord, inverse(MainSceneData.last_view_proj_mat_no_jitter));

  if (distance(curr_pos, last_pos) > 1.0) {
    // XXX
  //   fade = 0.0;
  }

  last_coord = truncate_coordinate(last_coord);
  vec3 intersected_color = texture(Previous_PostAmbientScene, last_coord).xyz;
  imageStore(DestTex, ivec2(gl_FragCoord.xy), vec4(intersected_color, 1) * fade);
}
