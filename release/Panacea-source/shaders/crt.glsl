#version 330 core
uniform sampler2D Texture;

in vec2 v_text;
out vec4 color;

const float CURVE = 0.8;
const float SCAN = 0.55;
const float MASK = 0.35;
const float BRIGHTNESS = 1.35;
const float VIGNETTE = 1.4;

void main() {
    vec2 center = vec2(0.5, 0.5);
    vec2 off_center = v_text - center;

    off_center *= 1.0 + CURVE * pow(abs(off_center.yx), vec2(2.5));
    vec2 uv = center + off_center;

    if (uv.x > 1.0 || uv.x < 0.00 || uv.y > 1.0 || uv.y < 0.0) {
        color = vec4(0.0, 0.0, 0.0, 1.0);
        return;
    }

    vec3 col = texture(Texture, uv).rgb;

    float row = fract(uv.y * float(textureSize(Texture, 0).y));
    float scan = 1.0 - SCAN * pow(abs(row - 0.5) * 2.0, 2.0);
    col *= scan;

    int c = int(mod(gl_FragCoord.x, 3.0));
    vec3 mask = vec3(1.0 - MASK);
    mask[c] = 1.0;
    col *= mask;

    vec2 d = v_text - center;
    col *= 1.0 - VIGNETTE * dot(d, d);

    color = vec4(col * BRIGHTNESS, 1.0);
}