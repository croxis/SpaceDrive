#version 410

#include "Includes/VertexOutput.include"

// Input from the vertex shader
layout(location=0) in VertexOutput vOutput;
layout(location=8) in vec2 mapping;

// Texture Samplers
uniform sampler2D p3d_Texture0;
uniform sampler2D p3d_Texture1;
uniform sampler2D p3d_Texture2;
uniform sampler2D p3d_Texture3;

out vec4 outputColor;

uniform float sphereRadius;
uniform vec3 cameraSpherePos;
uniform vec3 blackbody;

layout(std140) uniform;

// This is required for the materials
#include "Includes/MaterialPacking.include"

// Also this enables us to compute the tangent in
// the fragment shader
#include "Includes/TangentFromDDX.include"

#include "Includes/TangentFromDDX.include"


void Impostor(out vec3 cameraPos, out vec3 cameraNormal)
{
    float lensqr = dot(mapping, mapping);
    if(lensqr > 1.0)
        discard;

    cameraNormal = vec3(mapping, sqrt(1.0 - lensqr));
    cameraPos = (cameraNormal * sphereRadius) + cameraSpherePos;
}

void main()
{
    vec3 cameraPos;
    vec3 cameraNormal;

    Impostor(cameraPos, cameraNormal);

    // Create a material to store the properties on
    Material m;

    vec4 sampledDiffuse = texture(DIFFUSE_TEX, vOutput.texcoord);

    vec4 sampledNormal  = texture(NORMAL_TEX, vOutput.texcoord);
    float bumpFactor = vOutput.materialDiffuse.w;
    vec3 detailNormal = sampledNormal.rgb * 2.0 - 1.0;
    detailNormal = mix(vec3(0,0,1), detailNormal, bumpFactor);
    detailNormal = normalize(detailNormal);

    //vec3 normal = vOutput.normalWorld;
    vec3 normal = cameraNormal;
    vec3 tangent; vec3 binormal;
    reconstructTanBin(tangent, binormal);

    vec3 mixedNormal = normalize(
        tangent * detailNormal.x + binormal * detailNormal.y + normal * detailNormal.z
    );

    //outputColor = sqrt(accumLighting); //2.0 gamma correction
    //m.baseColor = vec4(blackbody, 1.0);
    m.baseColor = blackbody * vOutput.materialDiffuse.rgb;
    m.roughness = 0;
    m.metallic = 0;
    m.specular = 0;
    m.position = vOutput.positionWorld;
    m.normal = normal;
    renderMaterial(m);
    //outputColor = vec4(1.0);
}