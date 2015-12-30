
#include "RPPointLight.h"


/**
 * @brief Constructs a new point light
 * @details This contructs a new point light with default settings. By default
 *   the light is set to be an infinitely small point light source. You can
 *   change this with RPPointLight::set_inner_radius.   
 */
RPPointLight::RPPointLight() : RPLight(RPLight::LT_point_light) {
    _radius = 10.0;
    _inner_radius = 0.0;
}

/**
 * @brief Writes the light to a GPUCommand
 * @details This writes the point light data to a GPUCommand.
 * @see RPLight::write_to_command
 * 
 * @param cmd The target GPUCommand
 */
void RPPointLight::write_to_command(GPUCommand &cmd) {
    RPLight::write_to_command(cmd);
    cmd.push_float(_radius);
    cmd.push_float(_inner_radius);    
}

/**
 * @brief Inits the shadow sources of the light
 * @details This inits all required shadow sources for the point light.
 * @see RPLight::init_shadow_sources
 */
void RPPointLight::init_shadow_sources() {
    nassertv(_shadow_sources.size() == 0);
    // Create 6 shadow sources, one for each direction
    for(size_t i = 0; i < 6; ++i) {
        _shadow_sources.push_back(new ShadowSource());
    }
}

/**
 * @brief Updates the shadow sources
 * @details This updates all shadow sources of the light.
 * @see RPLight::update_shadow_sources
 */
void RPPointLight::update_shadow_sources() {
    LVecBase3f directions[6] = {
        LVecBase3f( 1,  0,  0),
        LVecBase3f(-1,  0,  0),
        LVecBase3f( 0,  1,  0),
        LVecBase3f( 0, -1,  0),
        LVecBase3f( 0,  0,  1),
        LVecBase3f( 0,  0, -1)
    };

    // Increase fov to prevent artifacts at the shadow map transitions
    const float fov = 90.0f + 3.0f;
    for (size_t i = 0; i < _shadow_sources.size(); ++i) {
        _shadow_sources[i]->set_resolution(get_shadow_map_resolution());
        _shadow_sources[i]->set_perspective_lens(fov, _near_plane, _radius,
                                                _position, directions[i]);
    }
}
