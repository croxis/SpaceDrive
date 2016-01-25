#version 430

// Shader used for Voxelization, required for GI

%DEFINES%

#define IS_VOXELIZE_SHADER 1

#define USE_TIME_OF_DAY
#pragma include "Includes/Configuration.inc.glsl"
#pragma include "Includes/Shadows.inc.glsl"
#pragma include "Includes/Structures/VertexOutput.struct.glsl"
#pragma include "Includes/Structures/MaterialOutput.struct.glsl"

%INCLUDES%
%INOUT%

layout(location=0) in VertexOutput vOutput;
layout(location=4) flat in MaterialOutput mOutput;

// Voxel data
uniform vec3 voxelGridPosition;
uniform writeonly image3D RESTRICT VoxelGridDest;

uniform samplerCube ScatteringIBLDiffuse;
uniform samplerCube ScatteringIBLSpecular;

uniform sampler2D p3d_Texture0;

#if HAVE_PLUGIN(Scattering)
    uniform sampler2DShadow VXGISunShadowMap;
    uniform mat4 VXGISunShadowMVP;
#endif

void main() {
    vec3 basecolor = texture(p3d_Texture0, vOutput.texcoord).xyz;
    basecolor *= mOutput.color;

    // Simplified ambient term
    vec3 ambient_diff = texture(ScatteringIBLDiffuse, vOutput.normal).xyz;
    vec3 ambient_spec = textureLod(ScatteringIBLSpecular, vOutput.normal, 6).xyz;

    vec3 ambient = ambient_diff * basecolor * (1 - mOutput.metallic);
    ambient += ambient_spec * basecolor * mOutput.metallic;
    ambient *= 0.1;

    vec3 shading_result = ambient;

    // Sun shading
    #if HAVE_PLUGIN(Scattering)

        vec3 sun_vector = sun_azimuth_to_angle(
            TimeOfDay.Scattering.sun_azimuth,
            TimeOfDay.Scattering.sun_altitude);

        vec3 sun_color = TimeOfDay.Scattering.sun_color *
            TimeOfDay.Scattering.sun_intensity * 45.0;

        // Get sun shadow term
        vec3 biased_position = vOutput.position + vOutput.normal * 0.2;

        const float slope_bias = 1.0 * 0.05;
        const float normal_bias =1.0 * 0.005;
        const float fixed_bias = 0.1 * 0.001;
        vec3 biased_pos = get_biased_position(
            vOutput.position, slope_bias, normal_bias, vOutput.normal, sun_vector);

        vec3 projected = project(VXGISunShadowMVP, biased_position);
        projected.z -= fixed_bias;
        float shadow_term = texture(VXGISunShadowMap, projected).x;
        shading_result += saturate(dot(sun_vector, vOutput.normal)) * sun_color * shadow_term * basecolor;


    #endif

    // Tonemapping to pack color
    shading_result = shading_result / (1.0 + shading_result);

    // Get destination voxel
    const int resolution = GET_SETTING(VXGI, grid_resolution);
    const float ws_size = GET_SETTING(VXGI, grid_ws_size);
    vec3 vs_coord = (vOutput.position + vOutput.normal * 0.0 - voxelGridPosition + ws_size) / (2.0 * ws_size);
    ivec3 vs_icoord = ivec3(vs_coord * resolution + 1e-5);

    // Write voxel
    imageStore(VoxelGridDest, vs_icoord, vec4(shading_result, 1.0));
}

