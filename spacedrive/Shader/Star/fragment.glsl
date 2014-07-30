#version 330
in vec2 mapping;

out vec4 outputColor;

uniform float sphereRadius;
uniform vec3 cameraSpherePos;
uniform vec3 blackbody;

layout(std140) uniform;

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

    vec4 accumLighting = vec4(1,1,1,1);

    //outputColor = sqrt(accumLighting); //2.0 gamma correction
    outputColor = vec4(blackbody, 1.0);
}