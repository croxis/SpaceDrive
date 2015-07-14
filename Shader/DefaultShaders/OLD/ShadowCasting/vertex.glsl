#version 400

in vec4 p3d_Vertex;
uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat4 trans_model_to_world;

out vec4 worldPos;

void main() {
    worldPos = trans_model_to_world * p3d_Vertex;
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;   
}