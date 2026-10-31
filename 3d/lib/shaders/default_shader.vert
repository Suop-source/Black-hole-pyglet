#version 150 core

// Vertex attributes
in vec3 position;
in vec3 translation;
in vec4 colors;
in vec3 normal;

uniform WindowBlock
{
    mat4 projection;
    mat4 view;
} window;

uniform mat4 m_rotation = mat4(1.0);
mat4 m_translate = mat4(1.0);

// Output variables down the OpenGL pipeline...
out vec3 o_position;
out vec4 o_color;
out vec3 o_normal; // NB! Normal attribute converted from vec3 to outputting as vec4
out vec4 o_fragPosition;

void main() {
    o_color    = colors;
    o_position = position;

    m_translate[3][0] = translation.x;
    m_translate[3][1] = translation.y;
    m_translate[3][2] = translation.z;

    // We fetch the rotation matrix from normal. This way, we prevent changing its direction.
    o_normal = mat3(transpose(inverse(m_translate * m_rotation))) * normal;
    o_fragPosition = m_translate * m_rotation * vec4(position, 1.0);

    gl_Position = window.projection * window.view * m_translate * m_rotation * vec4(position, 1.0);
}