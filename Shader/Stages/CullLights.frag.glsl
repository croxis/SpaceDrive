#version 430

#pragma include "Includes/Configuration.inc.glsl"
#pragma include "Includes/PositionReconstruction.inc.glsl"
#pragma include "Includes/LightCulling.inc.glsl"
#pragma include "Includes/LightData.inc.glsl"
#pragma include "Includes/Structures/Frustum.struct.glsl"

out vec4 result;

uniform isamplerBuffer CellListBuffer;
uniform writeonly iimageBuffer perCellLightsBuffer;


uniform samplerBuffer AllLightsData;
uniform int maxLightIndex;

// #define PROJ_MAT trans_view_of_mainCam_to_clip_of_mainCam
#define PROJ_MAT currentProjMat
// uniform mat4 PROJ_MAT;
uniform mat4 currentViewMatZup;

void main() {

    int sliceWidth = 512;
    ivec2 coord = ivec2(gl_FragCoord.xy);
    int idx = coord.x + coord.y * sliceWidth + 1;
    int numTotalCells = texelFetch(CellListBuffer, 0).x;

    if (idx > numTotalCells) {
        result = vec4(0.2, 0, 0, 1);
        return;
    }

    int packedCellData = texelFetch(CellListBuffer, idx).x;

    int cellX = packedCellData & 0x3FF;
    int cellY = (packedCellData >> 10) & 0x3FF;
    int cellSlice = (packedCellData >> 20) & 0x3FF;

    float min_distance = get_distance_from_slice(cellSlice);
    float max_distance = get_distance_from_slice(cellSlice + 1);

    int storageOffs = (MAX_LIGHTS_PER_CELL+1) * idx;
    int numRenderedLights = 0;

    // Per tile bounds
    ivec2 precomputeSize = ivec2(LC_TILE_AMOUNT_X, LC_TILE_AMOUNT_Y);
    ivec2 patchSize = ivec2(LC_TILE_SIZE_X, LC_TILE_SIZE_Y);
    ivec2 virtualScreenSize = precomputeSize * patchSize;
    vec2 tileScale = vec2(virtualScreenSize) / vec2( 2.0 * patchSize);
    vec2 tileBias = tileScale - vec2(cellX, cellY) - 0.5;

    // Build frustum
    // Based on http://gamedev.stackexchange.com/questions/67431/deferred-tiled-shading-tile-frusta-calculation-in-opengl
    // (Which is based on DICE's presentation)
    vec4 frustumRL = vec4(-PROJ_MAT[0][0] * tileScale.x, PROJ_MAT[0][1], tileBias.x, PROJ_MAT[0][3]);
    vec4 frustumTL = vec4(PROJ_MAT[1][0], -PROJ_MAT[1][1] * tileScale.y, tileBias.y, PROJ_MAT[3][3]);
    const vec4 frustumOffset = vec4(PROJ_MAT[3][0], PROJ_MAT[3][1], -1.0f, PROJ_MAT[3][3]);

    // Calculate frustum planes
    Frustum frustum;
    frustum.right  = normalize_without_w(frustumOffset - frustumRL);
    frustum.left   = normalize_without_w(frustumOffset + frustumRL);
    frustum.top    = normalize_without_w(frustumOffset - frustumTL);
    frustum.bottom = normalize_without_w(frustumOffset + frustumTL);

    frustum.nearPlane = vec4(0, 0, -1.0, -min_distance);
    frustum.farPlane = vec4(0, 0, 1.0, max_distance);



    // Compute aspect ratio
    float aspect = float(precomputeSize.y) / precomputeSize.x;
    vec3 aspect_mul = vec3(1, aspect, 1 );

    // Increase the frustum size by a small bit, because we trace at the corners,
    // since using this way we could miss some small parts of the sphere. With this
    // bias we should be fine, except for very small spheres, but those will be
    // out of the culling range then anyays
    float cull_bias = 0.2;

    // Compute corner ray directions
    vec3 ray_dir_tr = vec3( float(cellX+1+cull_bias) / precomputeSize.x, float(cellY+1+cull_bias) / precomputeSize.y, 0.0) * 2 - 1;
    vec3 ray_dir_tl = vec3( float(cellX+0-cull_bias) / precomputeSize.x, float(cellY+1+cull_bias) / precomputeSize.y, 0.0) * 2 - 1;
    vec3 ray_dir_br = vec3( float(cellX+1+cull_bias) / precomputeSize.x, float(cellY+0-cull_bias) / precomputeSize.y, 0.0) * 2 - 1;
    vec3 ray_dir_bl = vec3( float(cellX+0-cull_bias) / precomputeSize.x, float(cellY+0-cull_bias) / precomputeSize.y, 0.0) * 2 - 1;

    // Normalize ray directions, and account for the aspect ratio
    ray_dir_tr = normalize(ray_dir_tr * aspect_mul);
    ray_dir_tl = normalize(ray_dir_tl * aspect_mul);
    ray_dir_br = normalize(ray_dir_br * aspect_mul);
    ray_dir_bl = normalize(ray_dir_bl * aspect_mul);

    // Cull all lights
    for (int i = 0; i < maxLightIndex + 1 && numRenderedLights < MAX_LIGHTS_PER_CELL; i++) {

        // Fetch data of current light
        LightData light_data = read_light_data(AllLightsData, i * 4);
        int light_type = get_light_type(light_data);

        // Skip Null-Lights
        if (light_type < 1) continue;

        // Get Light position and project it to view space
        vec3 light_pos = get_light_position(light_data);
        vec4 light_pos_view = currentViewMatZup * vec4(light_pos, 1);

        bool visible = false;

        /*
            
            Point Lights

        */
        if (light_type == LT_POINT_LIGHT) {
            float radius = get_pointlight_radius(light_data);

            #if 0
                // Fast but inaccurate intersection, cull against frustum planes
                visible = sphere_frustum_intersection(frustum, light_pos_view, radius);
            #else
                // Slower but more accurate intersection, traces a ray at the corners of
                // each frustum.
                visible =            viewspace_ray_sphere_distance_intersection(light_pos_view.xyz, radius, ray_dir_tl, min_distance, max_distance);
                visible = visible || viewspace_ray_sphere_distance_intersection(light_pos_view.xyz, radius, ray_dir_tr, min_distance, max_distance);
                visible = visible || viewspace_ray_sphere_distance_intersection(light_pos_view.xyz, radius, ray_dir_bl, min_distance, max_distance);
                visible = visible || viewspace_ray_sphere_distance_intersection(light_pos_view.xyz, radius, ray_dir_br, min_distance, max_distance);
            #endif
        }

        // Write the light to the light buffer
        // TODO: Might have a seperate list for different light types, gives better performance
        if (visible) {
            numRenderedLights ++;
            imageStore(perCellLightsBuffer, storageOffs + numRenderedLights, ivec4(i));
        }
    }

    imageStore(perCellLightsBuffer, storageOffs, ivec4(numRenderedLights));
    result = vec4(vec3(idx / 100.0 ), 1.0);
}