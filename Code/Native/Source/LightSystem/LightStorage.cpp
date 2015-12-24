

#include "LightStorage.h"


LightStorage::LightStorage() {

    // Allocate containers
    _lights = new RPLight*[MAX_LIGHT_COUNT];
    _shadow_sources = new ShadowSource*[MAX_SHADOW_SOURCES];
    
    // Reset containers
    for (int i = 0; i < MAX_LIGHT_COUNT; ++i)
        _lights[i] = NULL;
    for (int i = 0; i < MAX_SHADOW_SOURCES; ++i)
        _shadow_sources[i] = NULL;

    _num_stored_lights = 0;
    _max_light_index = 0;
    _max_source_index = 0;
    _num_stored_sources = 0;
    _cmd_list = NULL;
    _shadow_atlas = new ShadowAtlas(4096);
}

LightStorage::~LightStorage() {
    delete [] _lights;
    delete [] _shadow_sources;
}

void LightStorage::set_command_list(GPUCommandList *cmd_list) {
    _cmd_list = cmd_list;
}


void LightStorage::add_light(PT(RPLight) light) {
    if (light->has_slot()) {
        cerr << "LightStorage: cannot add light since it already has a slot!" << endl;
        return;
    }

    // Reference the light, since we store it
    light->ref();
    int slot = find_light_slot();

    // In case we found no slot, emit an error
    if (slot < 0) {
        cerr << "LightStorage: All light slots used!" << endl;
        return;
    }

    _num_stored_lights ++;
    _max_light_index = max(_max_light_index, slot);

    _lights[slot] = light;
    light->assign_slot(slot);
    // light->unset_dirty_flag();

    // Light casts shadows
    if (light->get_casts_shadows()) {
        setup_shadows(light);
    }

    // GPUCommand cmd_add(GPUCommand::CMD_store_light);
    // light->write_to_command(cmd_add);
    // _cmd_list->add_command(cmd_add);
}


void LightStorage::setup_shadows(RPLight* light) {
    cout << "setting up shadows for light" << endl;
    light->init_shadow_sources();

    for (int i = 0; i < light->get_num_shadow_sources(); ++i) {
        ShadowSource* source = light->get_shadow_source(i);
        
        int slot = find_shadow_slot();
        if (slot < 0) {
            cerr << "Could not attach shadow source, out of slots!" << endl;
            return;
        }   

        // Assign the slot
        _shadow_sources[slot] = source;
        source->set_slot(slot);

        // Update maximum source index
        _max_source_index = max(_max_source_index, slot);
    }
}


void LightStorage::remove_light(PT(RPLight) light) {
    if (!light->has_slot()) {
        cerr << "Cannot detach light, light has no slot!" << endl;
        return;
    }

    _lights[light->get_slot()] = NULL;

    GPUCommand cmd_remove(GPUCommand::CMD_remove_light);
    cmd_remove.push_int(light->get_slot());
    _cmd_list->add_command(cmd_remove);

    _num_stored_lights --;

    // Correct max light index
    if (light->get_slot() == _max_light_index) {
        update_max_light_index();
    }

    light->remove_slot();

    // TODO: Cleanup shadow sources

    // Since we referenced the light when we stored it, we
    // have to decrease the reference aswell
    light->unref();
}



void LightStorage::update() {

    // Find all dirty lights and update them
    for (size_t i = 0; i <= _max_light_index; ++i) {
        if (_lights[i] && _lights[i]->is_dirty()) {

            // Update shadow sources in case the light is dirty
            _lights[i]->update_shadow_sources();
            GPUCommand cmd_update(GPUCommand::CMD_store_light);
            _lights[i]->write_to_command(cmd_update);
            _lights[i]->unset_dirty_flag();
            _cmd_list->add_command(cmd_update);
        }
    }

    vector<ShadowSource*> _sources_to_update;
    _sources_to_update.reserve(_max_source_index);

    // Find all dirty shadow sources and make a list of them
    for (size_t i = 0; i <= _max_source_index; ++i) {
        if (_shadow_sources[i] && _shadow_sources[i]->needs_update()) {
            _sources_to_update.push_back(_shadow_sources[i]);

            // Since we will update the source, we will also find a new spot for it,
            // so unregister the old spot
            if (_shadow_sources[i]->has_region()) {
                _shadow_atlas->free_region(_shadow_sources[i]->get_region());
            }
        }
    }

    // TODO: Sort the list of sources to update by their resolution, so that
    // big sources come first.

    // Now find an atlas spot for all regions
    for (size_t i = 0; i < _sources_to_update.size(); ++i) {
        ShadowSource *source = _sources_to_update[i];
        size_t num_tiles = _shadow_atlas->get_required_tiles(source->get_resolution());
        LVecBase4i new_region = _shadow_atlas->find_and_reserve_region(num_tiles, num_tiles);
        source->set_region(new_region);

        // TODO: Reserve a display region from the atlas, get the source mvp, and
        // do something fancy with it
        // mvp = source->get_mvp();
        // atlas->add_source(mvp, new_region)
    }


}
