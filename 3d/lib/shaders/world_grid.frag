#version 330 core

/**
 * Shader for rendering an infinite world grid.
 *
 * @details The code is taken from Marie at:
 * <a href="http://asliceofrendering.com/scene%20helper/2020/01/05/InfiniteGrid/">
 * asliceofrendering.com
 * </a>
 * License: <a href="https://github.com/BugzTroll/bugztroll.github.io/blob/master/LICENSE">
 * MIT License </a>
 *
 * @details It has been adjusted to suit the needs for this project.
 */

/*
layout(location = 1) in vec3 nearPoint;
layout(location = 2) in vec3 farPoint;
*/
in vec3 nearPoint;
in vec3 farPoint;
out vec4 outColor;

in mat4 fragView;
in mat4 fragProj;

// Near and far clip from camera frustum
uniform float u_nearClip = 0.01;
uniform float u_farClip = 100.0;

uniform vec3 lineColor = vec3(0.1);
uniform float tileScale = 1.0;

uniform float axisWidth = 0.5;
float aWidth = axisWidth / 2.0;

vec4 grid(vec3 fragPos3D, float scale, bool drawAxis) {
    vec2 coord = fragPos3D.xz * scale;
    vec2 derivative = fwidth(coord);
    vec2 grid = abs(fract(coord - 0.5) - 0.5) / derivative;
    float line = min(grid.x, grid.y);
    float minimumz = min(derivative.y, 1);
    float minimumx = min(derivative.x, 1);
    vec4 color = vec4(lineColor, 1.0 - min(line, 1.0));
    // z axis
    if(fragPos3D.x > -aWidth * minimumx && fragPos3D.x < aWidth * minimumx)
    color.z = 1.0;
    // x axis
    if(fragPos3D.z > -aWidth * minimumz && fragPos3D.z < aWidth * minimumz)
    color.x = 1.0;
    return color;
}
float computeDepth(vec3 pos) {
    vec4 clip_space_pos = fragProj * fragView * vec4(pos.xyz, 1.0);
    return (clip_space_pos.z / clip_space_pos.w);
}
float computeLinearDepth(vec3 pos) {
    vec4 clip_space_pos = fragProj * fragView * vec4(pos.xyz, 1.0);
    float clip_space_depth = (clip_space_pos.z / clip_space_pos.w) * 2.0 - 1.0; // put back between -1 and 1
    float linearDepth = (2.0 * u_nearClip * u_farClip) / (u_farClip + u_nearClip - clip_space_depth * (u_farClip - u_nearClip)); // get linear value between 0.01 and 100
    return linearDepth / u_farClip; // normalize
}
void main() {
    float t = -nearPoint.y / (farPoint.y - nearPoint.y);
    vec3 fragPos3D = nearPoint + t * (farPoint - nearPoint);

    gl_FragDepth = computeDepth(fragPos3D);

    float linearDepth = computeLinearDepth(fragPos3D);
    float fading = max(0, (0.5 - linearDepth));

    outColor = (grid(fragPos3D, 1/tileScale, true) + grid(fragPos3D, 1, true))* float(t > 0); // adding multiple resolution for the grid
    outColor.a *= fading;
}
