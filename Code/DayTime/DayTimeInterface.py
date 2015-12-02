
from direct.stdpy.file import join, isfile, open

from ..Util.DebugObject import DebugObject
from ..External.PyYAML import YAMLEasyLoad

class DayTimeInterface(DebugObject):

    """ This class manages the time of day. It stores and controls the settings
    which change over the time of day, and also handles loading and saving
    of them """

    def __init__(self, interface):
        """ Constructs a new DayTime, the interface should be a handle to a
        BasePluginInterface or any derived class of that """
        DebugObject.__init__(self)
        self._interface = interface
        self._base_dir = "."

    def set_base_dir(self, directory):
        """ Sets the base directory of the pipeline, in case its not the current
        working directory """
        self._base_dir = directory

    def load(self):
        """ Loads all daytime settings and overrides """
        # The plugin config does the actual work of loading the settings.
        # We just have to take care of the overrides:
        self._load_overrides()

    def _load_overrides(self):
        """ Loads the overrides from the daytime config file """
        cfg_file = join(self._base_dir, "Config/daytime.yaml")

        if not isfile(cfg_file):
            self.error("Could not load daytime overrides, file not found: ", cfg_file)
            return False

        yaml = YAMLEasyLoad(cfg_file)

        if "control_points" not in yaml:
            self.error("Root entry 'control_points' not found in daytime settings!")
            return False

        control_points = yaml["control_points"]

        # When there are no points, the object will be just none instead of an
        # empty dict
        if control_points is None:
            return

        available_plugins = self._interface.get_available_plugins()

        for plugin_id, cvs in control_points.items():

            # Skip invalid plugin ids
            if plugin_id not in available_plugins:
                self.warn("Skipping invalid plugin with id", plugin_id)
                continue

            # Skip disabled plugins
            plugin_handle = self._interface.get_plugin_handle(plugin_id)
            if not plugin_handle:
                continue

            plugin_handle.get_config().apply_daytime_curves(cvs)

    def write_configuration(self):
        """ Writes the time of day configuration """

        yaml = "\n\n"
        yaml += "# This file was autogenerated by the Time of Day Editor\n"
        yaml += "# Please avoid editing this file manually, instead use \n"
        yaml += "# the Time of Day Editor located at Toolkit/DayTimeEditor/.\n"
        yaml += "# Any comments and formattings in this file will be lost!\n"
        yaml += "\n\n"

        yaml += "control_points: \n"

        for plugin in self._interface.get_plugin_instances():
            mod_str = ""
            for setting_id, handle in plugin.get_config().get_daytime_settings().items():
                if handle.was_modified():
                    mod_str += "        " + setting_id + ": " + handle.serialize() + "\n"

            if mod_str:
                yaml += "    " + plugin.get_id() + ":\n"
                yaml += mod_str

        yaml += "\n\n"

        cfg_file = join(self._base_dir, "Config/daytime.yaml")

        try:
            with open(cfg_file, "w") as handle:
                handle.write(yaml)
        except IOError as msg:
            self.debug("Failed to write config file:", msg)
