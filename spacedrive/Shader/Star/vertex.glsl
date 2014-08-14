#version 410

#include "Includes/Configuration.include"
#include "Includes/VertexOutput.include"

layout(std140) uniform;

// Matrices
uniform mat4 trans_model_to_world;

// Material properties
in vec4 p3d_Vertex;
in vec3 p3d_Normal;
in vec2 p3d_MultiTexCoord0;


// Outputs
layout(location=0) out VertexOutput vOutput;
layout(location=8) out vec4 viewer;
layout(location=12) out vec3 center;
layout(location=15) out vec3 viewDir;


uniform Projection
{
	//mat4 cameraToClipMatrix;
	mat4 trans_myCamera_to_clip_of_myCamera;
};

//trans_myCamera_to_clip_of_myCamera ^^^
//https://www.panda3d.org/manual/index.php/Shaders_and_Coordinate_Spaces

// We get the material info from panda as a struct
struct PandaMaterial {
    vec4 diffuse;
    vec3 specular;
    vec4 ambient;
};
uniform PandaMaterial p3d_Material;

uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat4 p3d_ModelViewMatrixInverse;

// We need this for the velocity
uniform mat4 lastMVP;

uniform mat3 p3d_NormalMatrix;


uniform float sphereRadius;
uniform vec3 cameraSpherePos;

void main()
{

    // Transform normal to world space
    vOutput.normalWorld   = normalize(trans_model_to_world * vec4(p3d_Normal, 0) ).xyz;
    //vOutput.normalWorld   = p3d_Normal;

    // Transform position to world space
    vOutput.positionWorld = (trans_model_to_world * p3d_Vertex).xyz;

    // Pass texcoord to fragment shader
    // vOutput.texcoord = p3d_MultiTexCoord0.xy;
    vOutput.texcoord = p3d_MultiTexCoord0.xy;

    // Also pass diffuse to fragment shader
    vOutput.materialDiffuse = p3d_Material.diffuse;
    vOutput.materialSpecular = p3d_Material.specular;
    vOutput.materialAmbient = p3d_Material.ambient.z;

    // Compute velocity in vertex shader, but it's important
    // to move the w-divide to the fragment shader
    vOutput.lastProjectedPos = lastMVP * vec4(vOutput.positionWorld, 1) * vec4(1,1,1,2);

    //gl_Position = trans_myCamera_to_clip_of_myCamera * cameraCornerPos;
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;

    viewer = p3d_ModelViewMatrixInverse * vec4(0.0, 0.0, 0.0, 1.0);
    //viewDir = (p3d_Vertex + p3d_ModelViewMatrixInverse * vec4(p3d_MultiTexCoord0.xy * radius * 3.0, -radius, 0.0) - viewer).xyz;
    viewDir = (p3d_Vertex + p3d_ModelViewMatrixInverse * vec4(p3d_MultiTexCoord0.xy * 3.0, -1, 0.0) - viewer).xyz;
    center = (p3d_Vertex - viewer).xyz;

}