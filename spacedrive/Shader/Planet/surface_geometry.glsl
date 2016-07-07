#version 150

#include "Includes/VertexOutput.include"

layout(triangles) in;
layout(triangle_strip, max_vertices=3) out;

in VertexOutput vInput[3];

out VertexOutput vOutput;

 void main()
{
  for(int i = 0; i < gl_in.length(); i++)
  {
     // copy attributes
    gl_Position = gl_in[i].gl_Position;
    vOutput.positionWorld = vInput[i].positionWorld;
    vOutput.normalWorld = vInput[i].normalWorld;
    vOutput.texcoord = vInput[i].texcoord;

    vOutput.materialDiffuse = vInput[i].materialDiffuse;
    vOutput.materialSpecular = vInput[i].materialSpecular;
    vOutput.materialAmbient = vInput[i].materialAmbient;

    vOutput.tangentWorld = vInput[i].tangentWorld;
    vOutput.binormalWorld = vInput[i].binormalWorld;

    vOutput.lastProjectedPos = vInput[i].lastProjectedPos;

    // done with the vertex
    EmitVertex();
  }
  EndPrimitive();
}