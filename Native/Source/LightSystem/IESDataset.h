#pragma once

#include "pandabase.h"
#include "pta_float.h"
#include "pointerToArray.h"

class IESDataset {

    PUBLISHED:
        IESDataset();
        ~IESDataset();
    
        void set_vertical_angles(const PTA_float &vertical_angles);
        void set_horizontal_angles(const PTA_float &horizontal_angles);
		void set_candela_values(const PTA_float &candela_values);

    protected:

		float get_candela_value(size_t vertical_angle_idx, size_t horizontal_angle_idx);

        PTA_float _vertical_angles;
        PTA_float _horizontal_angles;
        PTA_float _candela_values;

  
};


