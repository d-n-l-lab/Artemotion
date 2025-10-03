/*
############################################################################################

  Software: ArteMotion
  Company: Brosky Media GmBH
  Developed By: Ravi Sharma
  Year: 2022

############################################################################################
*/
#version 400 core

in vec4 v_color;

out vec4 frag_color;

void main()
{
  gl_FragColor = v_color;
}