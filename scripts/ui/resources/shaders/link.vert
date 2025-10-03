/*
############################################################################################

  Software: ArteMotion
  Company: Brosky Media GmBH
  Developed By: Ravi Sharma
  Year: 2022

############################################################################################
*/
#version 400 core

in vec3 aMeshPos;

uniform vec4 uLinkColor;

uniform mat4 uproj;
uniform mat4 uview;
uniform mat4 umodel;

out vec4 v_color; //Interpolated fragment color (out)

void main()
{
  v_color = uLinkColor;
  gl_Position = uproj * uview * umodel * vec4(aMeshPos, 1.0);
}