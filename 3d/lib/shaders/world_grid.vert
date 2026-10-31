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

in vec3 position;

out vec3 nearPoint;
out vec3 farPoint;

out mat4 fragProj;
out mat4 fragView;

uniform WindowBlock
{
    mat4 projection;
    mat4 view;
} window;

/**
 * Unproject point from clip space to world space.
 */
vec3 UnprojectPoint(float x, float y, float z, mat4 view, mat4 projection) {
    mat4 viewInv = inverse(view);
    mat4 projInv = inverse(projection);
    vec4 unprojectedPoint =  viewInv * projInv * vec4(x, y, z, 1.0);
    return unprojectedPoint.xyz / unprojectedPoint.w;
}

// normal vertice projection
void main() {
    fragProj = window.projection;
    fragView = window.view;

    nearPoint = UnprojectPoint(position.x, position.y, 0.0, window.view, window.projection).xyz; // unprojecting on the near plane
    farPoint = UnprojectPoint(position.x, position.y, 1.0, window.view, window.projection).xyz; // unprojecting on the far plane
    gl_Position = vec4(position, 1.0);
}