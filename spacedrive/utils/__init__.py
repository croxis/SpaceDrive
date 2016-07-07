__author__ = 'croxis'

def convertToPatches(model):
    """Sets up a model for autotesselation."""
    for node in model.find_all_matches("**/+GeomNode"):
        geom_node = node.node()
        num_geoms = geom_node.get_num_geoms()
        for i in range(num_geoms):
            geom_node.modify_geom(i).make_patches_in_place()