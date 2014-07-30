#version 330

layout(std140) uniform;

out vec2 mapping;
in vec4 p3d_Vertex;

uniform Projection
{
	//mat4 cameraToClipMatrix;
	mat4 trans_myCamera_to_clip_of_myCamera;
};

//trans_myCamera_to_clip_of_myCamera ^^^
//https://www.panda3d.org/manual/index.php/Shaders_and_Coordinate_Spaces


uniform float sphereRadius;
uniform vec3 cameraSpherePos;
uniform mat4 p3d_ModelViewProjectionMatrix;

void main()
{
    vec2 offset;
    switch(gl_VertexID)
    {
    case 0:
        //Bottom-left
        mapping = vec2(-1.0, -1.0);
        offset = vec2(-sphereRadius, -sphereRadius);
        break;
    case 1:
        //Top-left
        mapping = vec2(-1.0, 1.0);
        offset = vec2(-sphereRadius, sphereRadius);
        break;
    case 2:
        //Bottom-right
        mapping = vec2(1.0, -1.0);
        offset = vec2(sphereRadius, -sphereRadius);
        break;
    case 3:
        //Top-right
        mapping = vec2(1.0, 1.0);
        offset = vec2(sphereRadius, sphereRadius);
        break;
    }

    vec4 cameraCornerPos = vec4(cameraSpherePos, 1.0);
    cameraCornerPos.xy += offset;

    //gl_Position = trans_myCamera_to_clip_of_myCamera * cameraCornerPos;
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
}