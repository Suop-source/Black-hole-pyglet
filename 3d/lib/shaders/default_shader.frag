#version 150 core

in vec3 o_position;
in vec4 o_color;
in vec3 o_normal;
in vec4 o_fragPosition;

out vec4 color;

// Phong
uniform vec3 u_diffuseColor = vec3(1.0f);
// uniform vec3 u_ambientColor        = vec3(1.0f);  // Receives main:ambientColorCycle

uniform vec3 u_specularColor  = vec3(1.0f);  // Receives main:glm::vec4(...)

uniform GlobalState
{
    vec3 light_position;
    vec3 camera_position;
} globalState;

void main() {
    vec4 baseColor;

    baseColor = o_color;

    // Diffuse computations
    vec3 norm = normalize(o_normal);
    vec3 lightDirection = normalize((globalState.light_position.xyz) - o_fragPosition.xyz);
    vec3 diffuseColor = max(dot(norm, lightDirection), 0.0f) * u_diffuseColor;

    // Specular computations
    vec3 reflectedLight    = normalize(reflect(-lightDirection, norm));
    vec3 observerDirection = normalize(globalState.camera_position - o_fragPosition.xyz);

    /*
     * Specular formula: (Source: issue 22 by Rafael Palomar)
     *
     * Where str is specFactor, ref is reflectedLight, obs is
     * observerDirection, n is arbitrary shininess factor, and "."
     * signifies dot product. Here split across 2 lines of code.
     *
     * This comment doesn't necessarily need to be here.
     * If it's not of convenience feel free to remove.
     *
     * S = str . (ref . obs)^n
     */
    float specFactor = pow(max(dot(observerDirection, reflectedLight), 0.0f), 12);
    vec3  specular = specFactor * u_specularColor;

    // Compute the final colors
    color = baseColor * vec4(diffuseColor + specular, 1); // Lighting added to the computation


    // The below code only shows the base colour. Use for debugging.
    // color = baseColor;
}