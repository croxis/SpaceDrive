#version 440

#pragma include "Includes/Configuration.inc.glsl"

out vec4 result;

uniform layout(rgba16f) imageBuffer ExposureStorage;
uniform sampler2D DownscaledTex;

uniform float frameDelta;

float make_log(float x) {
    // return log(1 + 64*x) / log(65.0);
    return (exp(6*x)-1) / (exp(7)-1);
}

void main() {

    // Manually do the last downscale step
    ivec2 texsize = textureSize(DownscaledTex, 0).xy;
    float avg_luminance = 0.0;
    for (int x = 0; x < texsize.x; ++x) {
        for (int y = 0; y < texsize.y; ++y) {
            avg_luminance += texelFetch(DownscaledTex, ivec2(x, y), 0).x;
        }
    }
    avg_luminance /= float(texsize.x * texsize.y);
    avg_luminance /= 0.2;

    float min_exp = make_log(GET_SETTING(ColorCorrection, min_exposure));
    float max_exp = make_log(GET_SETTING(ColorCorrection, max_exposure));
    float exp_bias = GET_SETTING(ColorCorrection, exposure_bias) * 10.0;

    avg_luminance = max(min_exp, min(max_exp, 1.0 / (avg_luminance) + exp_bias));

    // Transition between the last and current value smoothly
    float cur_luminance = imageLoad(ExposureStorage, 0).x;
    float adaption_rate = GET_SETTING(ColorCorrection, brightness_adaption_rate);

    if (cur_luminance < avg_luminance) {
        adaption_rate = GET_SETTING(ColorCorrection, darkness_adaption_rate);
    }


    float adjustment = saturate(frameDelta * adaption_rate);
    float new_luminance = mix(cur_luminance, avg_luminance, adjustment);

    imageStore(ExposureStorage, 0, vec4(new_luminance));


    result = vec4(new_luminance, 0, 0, 1);
}