/*
############################################################################################

  Software: ArteMotion
  Company: Brosky Media GmBH
  Developed By: Ravi Sharma
  Year: 2022

############################################################################################
*/
#version 330 core

in vec3 aPos;

uniform mat4 uproj;
uniform mat4 uview;
uniform mat4 umodel;

uniform vec3 uX_Range;
uniform vec3 uY_Range;
uniform vec3 uZ_Range;
uniform vec3 uGridColor;

out vec4 v_color; //Interpolated fragment color (out)

vec4 get_color()
{
  vec3 red = vec3(1.0, 0.0, 0.0);
  vec3 green = vec3(0.0, 1.0, 0.0);
  vec3 blue = vec3(0.0, 0.0, 1.0);

  if (aPos.xy == vec2(uX_Range.x, uY_Range.x) || aPos.xy == vec2(uX_Range.y, uY_Range.x) ||
      aPos.xy == vec2(uX_Range.z, uY_Range.x) || aPos.xy == vec2(uX_Range.x, uY_Range.z) ||
      aPos.xy == vec2(uX_Range.y, uY_Range.z) || aPos.xy == vec2(uX_Range.z, uY_Range.z))
    return vec4(green, 1.0); // Z axis
  else if (aPos.xz == vec2(uX_Range.x, uZ_Range.x) || aPos.xz == vec2(uX_Range.x, uZ_Range.y) ||
           aPos.xz == vec2(uX_Range.x, uZ_Range.z) || aPos.xz == vec2(uX_Range.y, uZ_Range.x) ||
           aPos.xz == vec2(uX_Range.y, uZ_Range.y) || aPos.xz == vec2(uX_Range.y, uZ_Range.z) ||
           aPos.xz == vec2(uX_Range.z, uZ_Range.x) || aPos.xz == vec2(uX_Range.z, uZ_Range.y) ||
           aPos.xz == vec2(uX_Range.z, uZ_Range.z))
    return vec4(blue, 1.0); // Y axis
  else if (aPos.yz == vec2(uY_Range.x, uZ_Range.x) || aPos.yz == vec2(uY_Range.x, uZ_Range.y) ||
           aPos.yz == vec2(uY_Range.x, uZ_Range.z) || aPos.yz == vec2(uY_Range.z, uZ_Range.x) ||
           aPos.yz == vec2(uY_Range.z, uZ_Range.y) || aPos.yz == vec2(uY_Range.z, uZ_Range.z))
    return vec4(red, 1.0); // X axis
  else
    return vec4(uGridColor, 1.0);
}

void main()
{
  v_color = get_color();
  gl_Position = uproj * uview * umodel * vec4(aPos, 1.0);
}