
#include "RPLight.h"


RPLight::RPLight(LightType light_type) {
    _light_type = light_type;
    _dirty = false;
    _slot = -1;
    _position.set(0, 0, 0);
    _color.set(1, 1, 1);
    _ies_profile = -1;
}


void RPLight::write_to_command(GPUCommand &cmd) {
    cmd.push_int(_slot);

    // Start of light data
    cmd.push_int(_light_type);
    cmd.push_int(_ies_profile);
    cmd.push_vec3(_position);
    cmd.push_vec3(_color);
}


RPLight::~RPLight() {
    // Default ctor, for now
}
