/**
 * 
 * RenderPipeline
 * 
 * Copyright (c) 2014-2015 tobspr <tobias.springer1@gmail.com>
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
#define USE_TIME_OF_DAY
#pragma include "Includes/Configuration.inc.glsl"
#pragma include "Includes/Noise.inc.glsl"

uniform writeonly image3D RESTRICT CloudVoxels;
uniform sampler2D NoiseTex;
uniform sampler2D CloudNoiseTex;

float cloud_weight(float height) {
    // Clouds get less at higher distances. Also decrease them at the bottom
    const int border_pow = 1 * 2 + 1;
    const float decay = GET_SETTING(Clouds, cloud_decay) * 3.0; 
    // Analytical formula, see wolframalpha: "-(2^15) * abs(x-0.5)^15 + 1 - 0.8*(x^2) from 0 to 1"
    return max(0, -pow(2, border_pow) * pow(abs(height - 0.5), border_pow) + 1.0 - decay * pow(height, 4.0));
}

void main() {
    ivec2 coord = ivec2(gl_FragCoord.xy);
    vec2 flt_coord = vec2(coord) / CLOUD_RES_XY; 

    float time_offs = MainSceneData.frame_time * 0.01;
    vec3 wind_dir = vec3(0.8, 0.6, 0.01);
    vec3 wind_offset = time_offs * wind_dir * 1.0;

    for (int z = 0; z < CLOUD_RES_Z; ++z) {
        vec3 cloud_coord = vec3(flt_coord, float(z) / CLOUD_RES_Z);
        float cloud_factor = 0.0;

        // Stratus
        float stratus = fbm(cloud_coord + 0.7 + wind_offset * 0.7, 3.0) - 0.5;
        stratus = max(0, stratus);
        stratus *= worley_noise(flt_coord + wind_offset.xy * 1.0, 32, 0.0);
        stratus *= 1 - min(1.0, 3.5 * cloud_coord.z);
        stratus *= 6.0;
        cloud_factor += max(0, stratus) * TimeOfDay.Clouds.stratus_amount;

        // Cumulus
        float cumulus = worley_noise(flt_coord + wind_offset.xy * 0.7, 4, 0.8);
        cumulus *= fbm(cloud_coord + wind_offset * 0.6, 5.0) - 0.8;
        cumulus *= 1.0 - min(1.0, 0.3*(1-cloud_coord.z) );
        cumulus *= 12.0;
        cloud_factor += max(0, cumulus) * TimeOfDay.Clouds.cumulus_amount;

        // Soft
        float soft = fbm(cloud_coord + wind_offset * 0.5, 3.0) - 0.55;
        soft *= 6.0 * distance(cloud_coord.z, 0.5);
        cloud_factor += max(0, soft) * TimeOfDay.Clouds.soft_amount;

        cloud_factor *= cloud_weight(cloud_coord.z);
        cloud_factor *= TimeOfDay.Clouds.cloud_intensity;
        cloud_factor = saturate(cloud_factor);
        imageStore(CloudVoxels, ivec3(coord, z), vec4(cloud_factor));
    }
}
