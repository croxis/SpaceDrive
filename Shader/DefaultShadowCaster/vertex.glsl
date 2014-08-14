#version 400

in vec4 p3d_Vertex;
in vec2 p3d_MultiTexCoord0;
in vec3 p3d_Normal;
uniform mat4 trans_model_to_world;
out vec4 worldPosition;
out vec2 vtxTexcoord;
out vec3 vtxNormal;
out vec3 vtxDiffuseMultiplier;

void main() {
    vec4 worldPos = trans_model_to_world * p3d_Vertex;
    
    // Depth offset??
    // vec4 worldNormal = trans_model_to_world * vec4(p3d_Normal, 0);
    // worldPos -= worldNormal;

    vtxDiffuseMultiplier = vec3(1);

    // For testing
    if (worldPos.z < 0.1) {
        vtxDiffuseMultiplier = vec3(0,0,0);
    }

    vtxTexcoord = p3d_MultiTexCoord0;
    gl_Position = worldPos;
    
    vec4 normalWorld = normalize(trans_model_to_world * vec4(p3d_Normal, 0));
    vtxNormal = normalWorld.xyz;
}