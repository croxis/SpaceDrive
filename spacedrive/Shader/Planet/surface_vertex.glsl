#version 410

#pragma include "Includes/Configuration.include"
#pragma include "Includes/Structures/VertexOutput.struct"
#pragma include "Includes/Structures/PandaMaterial.struct"

// Matrices
uniform mat4 trans_model_to_world;
uniform mat4 tpose_world_to_model;

// Material properties
in vec4 p3d_Vertex;
in vec3 p3d_Normal;
in vec4 p3d_Color;

// Texture-Coordinate
in vec2 p3d_MultiTexCoord0;

// Outputs
layout(location=0) out VertexOutput vOutput;

uniform PandaMaterial p3d_Material;
uniform vec4 p3d_ColorScale;
uniform mat4 p3d_ModelViewProjectionMatrix;

// We need this for the velocity
uniform mat4 lastMVP;

uniform mat3 p3d_NormalMatrix;

void main() {
    // Start sphereization code
    // vertex must start with a z of 1, otherwise we must do it in shader
    vec4 vertex = vec4(normalize(p3d_Vertex.xyz), p3d_Vertex.w);
    //vec4 vertex = p3d_Vertex;//Shows it as a cube
    //vertex = p3d_Vertex;
    vec3 normal = vertex.xyz; // Works only for sphere
    //End spherization code

    // Start RenderPipeline code
    // Transform normal to world space
    vOutput.normalWorld   = normalize(trans_model_to_world * vec4(normal, 0) ).xyz;

    // Transform position to world space
    vOutput.positionWorld = (trans_model_to_world * vertex).xyz;

    // Pass texcoord to fragment shader
    vOutput.texcoord = p3d_MultiTexCoord0.xy;

    // Also pass diffuse to fragment shader
    vOutput.materialDiffuse = p3d_Material.diffuse * p3d_ColorScale * p3d_Color;
    vOutput.materialSpecular = p3d_Material.specular;
    vOutput.materialAmbient = p3d_Material.ambient.z;

    // Compute velocity in vertex shader, but it's important
    // to move the w-divide to the fragment shader
    vOutput.lastProjectedPos = lastMVP * vec4(vOutput.positionWorld, 1) * vec4(1,1,1,2);

    // Transform vertex to window space
    // Only required when not using tesselation shaders
    gl_Position = p3d_ModelViewProjectionMatrix * vertex;
}

