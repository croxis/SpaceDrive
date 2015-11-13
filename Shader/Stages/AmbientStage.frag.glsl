#version 400

#pragma include "Includes/Configuration.inc.glsl"
#pragma include "Includes/GBufferPacking.inc.glsl"
#pragma include "Includes/BRDF.inc.glsl"
#pragma include "Includes/Lights.inc.glsl"

in vec2 texcoord;
uniform sampler2D ShadedScene;
uniform sampler2D GBufferDepth;
uniform sampler2D GBuffer0;
uniform sampler2D GBuffer1;
uniform sampler2D GBuffer2;

uniform sampler2D PrefilteredBRDF;

uniform samplerCube DefaultEnvmap;
uniform vec3 cameraPosition;

#if HAVE_PLUGIN(Scattering)
    uniform samplerCube ScatteringCubemap;
#endif

#if HAVE_PLUGIN(TSAO)
    uniform sampler2D AmbientOcclusion;
#endif

out vec4 result;

float get_mipmap_for_roughness(samplerCube map, float roughness) {
    int cubemap_size = textureSize(map, 0).x;
    float num_mipmaps = 1 + floor(log2(cubemap_size));


    float reflectivity = saturate(1.0 - roughness);

    // Increase mipmap at extreme roughness, linear doesn't work well there
    // reflectivity += saturate(reflectivity - 0.9) * 2.0;

    return (num_mipmaps - reflectivity * 9.0);
}



void main() {

    ivec2 coord = ivec2(gl_FragCoord.xy);
    Material m = unpack_material(GBufferDepth, GBuffer0, GBuffer1, GBuffer2);

    vec3 view_vector = normalize(cameraPosition - m.position);
    vec4 ambient = vec4(0);

    #if !DEBUG_MODE

    if (!is_skybox(m, cameraPosition)) {
        float conv_roughness = ConvertRoughness(m.roughness);

        vec3 reflected_dir = reflect(-view_vector, m.normal);
        vec3 env_coord = fix_cubemap_coord(reflected_dir);


        // vec3 h = normalize(view_vector - reflected_dir);
        vec3 h = normalize(m.normal + view_vector);

        float NxV = saturate(dot(m.normal, view_vector));


        float mipmap_bias = saturate(pow(1.0 - NxV, 5.0)) * 3.0;
        mipmap_bias = 0.0;

        float env_mipmap = get_mipmap_for_roughness(DefaultEnvmap, m.roughness) + mipmap_bias;

        vec3 env_default_color = textureLod(DefaultEnvmap, env_coord, env_mipmap).xyz;
        vec3 env_amb = vec3(0);

        #if HAVE_PLUGIN(Scattering)

            vec3 scat_coord = reflected_dir;
            float scat_mipmap = get_mipmap_for_roughness(ScatteringCubemap, m.roughness) + mipmap_bias;
            vec3 env_scattering_color = textureLod(ScatteringCubemap, scat_coord, scat_mipmap).xyz;

            env_default_color = env_scattering_color * M_PI;

            // Cheap irradiance
            env_amb = textureLod(ScatteringCubemap, m.normal, 5).xyz;
            // env_amb *= 0;


        #endif

        // Get prefiltered BRDF
        vec2 prefilter_brdf = textureLod(PrefilteredBRDF, vec2(m.roughness, NxV), 0).xy;
        vec3 prefilter_color = prefilter_brdf.y + m.diffuse * prefilter_brdf.y;


        // Different terms for metallic and diffuse objects
        vec3 env_metallic = m.diffuse;
        // env_metallic *= 0.0 + pow(LxH, 2.0) * 1.0;
        env_metallic = pow(env_metallic, vec3(2.2));
        // env_metallic *= vec3(1.5, 1.1, 0.4);
        // env_metallic *= 1.2;

        vec3 env_diffuse = prefilter_color * 0.2;
        vec3 env_factor = mix(env_diffuse, env_metallic, m.metallic) * m.specular;

        vec3 diffuse_ambient = vec3(0.02) * m.diffuse * (1.0 - m.metallic);
        vec3 specular_ambient = env_factor * env_default_color * 0.1;

        ambient.xyz += diffuse_ambient + specular_ambient;
        ambient.xyz += env_amb * 0.05 * m.diffuse * (1.0 - m.metallic);

        #if HAVE_PLUGIN(TSAO)
            ambient.xyz = max(ambient.xyz, vec3(0));
            float occlusion = texelFetch(AmbientOcclusion, coord, 0).x;
            ambient *= pow(occlusion, 5.0);

        #endif

    }

    #endif

    ambient.w = 0.0;

    result = texture(ShadedScene, texcoord) * 1 +  ambient * 1;
}