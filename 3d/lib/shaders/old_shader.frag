#version 150 core
in vec4 vertex_colors;
out vec4 final_color;

void main()
{
    final_color = vertex_colors; //vec4(1.0, 1.0, 1.0, 1.0);
    // No GL_ALPHA_TEST in core, use shader to discard.
    if(final_color.a < 0.01){
        discard;
    }
}