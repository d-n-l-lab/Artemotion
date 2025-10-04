/*
############################################################################################

  Software: ArteMotion
  Company: Brosky Media GmBH
  Developed By: Ravi Sharma
  Year: 2022

############################################################################################
*/
#version 330 core

in vec3 aCurvePos;

uniform mat4 uproj;
uniform mat4 uview;
uniform mat4 umodel;

out vec4 v_color; //Interpolated gragment color (out)

void main()
{
  gl_Position = uproj * uview * umodel * vec4(aCurvePos, 1.0);
  v_color = vec4(0.25, 0.59, 0.75, 1.0);
}