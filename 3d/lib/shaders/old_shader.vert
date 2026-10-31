#version 150 core
in vec3 position;
in vec3 translation;
in vec4 colors;

out vec4 vertex_colors;

uniform WindowBlock
{
    mat4 projection;
    mat4 view;
} window;

uniform mat4 m_rotation = mat4(1.0);
mat4 m_translate = mat4(1.0);

void main()
{
    m_translate[3][0] = translation.x;
    m_translate[3][1] = translation.y;
    m_translate[3][2] = translation.z;
    gl_Position = window.projection * window.view * m_translate * m_rotation * vec4(position, 1.0);
    vertex_colors = colors;
}