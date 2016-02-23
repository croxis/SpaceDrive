"""

RenderPipeline

Copyright (c) 2014-2016 tobspr <tobias.springer1@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

"""

import importlib
import collections

from rplibs.six import iteritems, itervalues
from rplibs.yaml import load_yaml_file

from direct.stdpy.file import listdir, isdir, join, open

from rpcore.base_manager import BaseManager
from rpcore.native import NATIVE_CXX_LOADED
from rpcore.pluginbase.setting_types import make_setting_from_data
from rpcore.pluginbase.day_setting_types import make_daysetting_from_data

class PluginManager(BaseManager):

    """ This class manages all plugins. It provides functionality to load plugin
    settings, trigger callbacks on plugins, initialize the plugin instances
    and much more. """

    def __init__(self, pipeline):
        """ Constructs a new manager with no plugins loaded. To load settings
        and plugins, call load(). """
        BaseManager.__init__(self)
        self._pipeline = pipeline
        self._instances = {}
        self._settings = {}
        self._day_settings = {}
        self._enabled_plugins = set()

    def load(self):
        """ Loads all plugins and their settings, and also constructs instances
        of the main plugin classes for all enabled plugins """
        self.debug("Loading plugins")
        self._load_base_settings("$$plugins")
        self.load_setting_overrides("$$config/plugins.yaml")
        self.load_daytime_overrides("$$config/daytime.yaml")

        for plugin_id in self._settings:
            handle = self._load_plugin(plugin_id)
            if handle:
                self._instances[plugin_id] = handle
            else:
                self.disable_plugin(plugin_id)

    def disable_plugin(self, plugin_id):
        """ Disables a plugin, given its plugin_id. This will remove it from
        the list of enabled plugins, if it ever was there """
        if plugin_id in self._enabled_plugins:
            self.warn("Disabling", plugin_id)
            self._enabled_plugins.remove(plugin_id)
            for instance in itervalues(self._instances):
                if plugin_id in instance.required_plugins:
                    self.disable_plugin(instance.plugin_id)
        if plugin_id in self._instances:
            del self._instances[plugin_id]

    def unload(self):
        """ Unloads all plugins """
        self.debug("Unloading all plugins")
        self._instances = {}
        self._settings = {}
        self._day_settings = {}
        self._enabled_plugins = set()

    def do_update(self):
        """ Main update method """
        pass

    def _load_base_settings(self, plugin_dir):
        """ Loads the base settings of all plugins, even of disabled plugins.
        This is required to verify all overrides. """
        for entry in listdir(plugin_dir):
            abspath = join(plugin_dir, entry)
            if isdir(abspath) and entry not in ("__pycache__", "plugin_prefab"):
                self._load_plugin_settings(entry, abspath)

    def _load_plugin_settings(self, plugin_id, plugin_pth):
        """ Internal method to load all settings of a plugin, given its plugin
        id and path to the plugin base directory """
        config_file = join(plugin_pth, "config.yaml")
        config = load_yaml_file(config_file)
        # When you don't specify anything in the settings, instead of
        # returning an empty dictionary, pyyaml returns None
        config["settings"] = config["settings"] or {}
        config["daytime_settings"] = config["daytime_settings"] or {}
        settings = collections.OrderedDict(
            [(k, make_setting_from_data(v)) for k, v in config["settings"]])
        self._settings[plugin_id] = settings

        day_settings = collections.OrderedDict(
            [(k, make_daysetting_from_data(v)) for k, v in config["daytime_settings"]])
        self._day_settings[plugin_id] = day_settings

    def load_setting_overrides(self, override_path):
        """ Loads an override file for the settings, which contains values to
        override the settings with """
        overrides = load_yaml_file(override_path)
        self._enabled_plugins = set(overrides["enabled"] or [])
        for key, val in iteritems(overrides["overrides"] or {}):
            plugin_id, setting_id = key.split(".")
            if plugin_id not in self._settings:
                self.warn("Unkown plugin for override:", plugin_id)
                continue
            if setting_id not in self._settings[plugin_id]:
                self.warn("Unkown override:", plugin_id, ":", setting_id)
                continue
            self._settings[plugin_id][setting_id].set_value(val)

    def load_daytime_overrides(self, override_path):
        """ Loads an override file for the daytime settings, which contains
        values to override the settings with """
        overrides = load_yaml_file(override_path)
        for plugin_id, settings in iteritems(overrides["control_points"] or {}):
            for setting_id, control_points in iteritems(settings):
                if setting_id not in self._day_settings[plugin_id]:
                    self.warn("Unkown daytime override:", plugin_id, ":", setting_id)
                    continue
                self._day_settings[plugin_id][setting_id].set_control_points(control_points)

    def trigger_hook(self, hook_name):
        """ Triggers a given hook on all plugins, effectively calling all
        bound callbacks """
        hook_method = "on_{}".format(hook_name)
        for plugin_id in self._enabled_plugins:
            plugin_handle = self._instances[plugin_id]
            if hasattr(plugin_handle, hook_method):
                getattr(plugin_handle, hook_method)()

    def is_plugin_enabled(self, plugin_id):
        """ Returns whether a plugin is currently enabled and loaded """
        return plugin_id in self._enabled_plugins

    def get_plugin_handle(self, plugin_id):
        """ Returns a handle to a plugin given its plugin id. Throws an exception
        if plugin is not loaded, use is_plugin_enabled to check the plugins
        status first """
        return self._instances[plugin_id]

    def get_setting_handle(self, plugin_id, setting_id):
        """ Returns the handle to a setting """
        return self._settings[plugin_id][setting_id]

    @property
    def enabled_plugins(self):
        """ Returns a list of all enabled plugin ids """
        return self._enabled_plugins

    @property
    def plugin_instances(self):
        """ Returns a dictionary with all plugin ids and their instances """
        return self._instances

    @property
    def settings(self):
        """ Returns all settings as a dictionary """
        return self._settings

    @property
    def day_settings(self):
        """ Returns all time of day settings as a dictionary """
        return self._day_settings

    @property
    def num_day_settings(self):
        """ Returns the amount of day time settings """
        return sum((len(i) for i in itervalues(self._day_settings)))

    def init_defines(self):
        """ Initializes all plugin settings as a define, so they can be queried
        in a shader """
        for plugin_id in self._enabled_plugins:
            plugin_settings = self._settings[plugin_id]
            self._pipeline.stage_mgr.define("HAVE_PLUGIN_{}".format(plugin_id), 1)
            for setting_id, setting in iteritems(plugin_settings):
                # Only store settings which either never change, or trigger
                # a shader reload when they change
                if setting.shader_runtime or not setting.runtime:
                    setting.write_defines(
                        plugin_id, setting_id, self._pipeline.stage_mgr.define)

    def _load_plugin(self, plugin_id):
        """ Internal method to load a plugin """
        plugin_class = "..plugins.{}.plugin".format(plugin_id)
        module = importlib.import_module(plugin_class, package=__package__)
        instance = module.Plugin(self._pipeline)
        if instance.native_only and not NATIVE_CXX_LOADED:
            if plugin_id in self._enabled_plugins:
                self.warn("Cannot load", plugin_id, "since it requires the C++ modules.")
                self._enabled_plugins.remove(plugin_id)
        for required_plugin in instance.required_plugins:
            if required_plugin not in self._enabled_plugins:
                if plugin_id in self._enabled_plugins:
                    self.warn("Cannot load", plugin_id, "since it requires", required_plugin)
                self._enabled_plugins.remove(plugin_id)
                break
        return instance

    def save_overrides(self, override_file):
        """ Saves all overrides to the given file """
        output = "# Autogenerated by the plugin configurator\n"
        output += "# Any formatting and comments will be lost\n\n"
        output += "enabled:\n"
        for plugin_id in self._settings:
            output += "   {}- {}\n".format(
                " # " if plugin_id not in self._enabled_plugins else " ", plugin_id)
        output += "\n\n"
        output += "overrides:\n"
        for plugin_id, plugin_settings in iteritems(self._settings):
            for setting_id, setting_handle in iteritems(plugin_settings):
                output += "    {}.{}: {}\n".format(
                    plugin_id, setting_id, setting_handle.value)
        with open(override_file, "w") as handle:
            handle.write(output)

    def save_daytime_overrides(self, override_file):
        """ Saves all time of day overrides to the given file """
        output = "# Autogenerated by the time of day editor\n"
        output += "# Any formatting and comments will be lost\n\n"
        output += "control_points:\n"
        for plugin_id, settings in iteritems(self._day_settings):
            if settings:
                output += " " * 4 + plugin_id + ":\n"
                for setting_id, setting_handle in iteritems(settings):
                    output += " " * 8 + setting_id + ": "
                    output += setting_handle.serialize() + "\n"
        with open(override_file, "w") as handle:
            handle.write(output)

    def set_plugin_enabled(self, plugin_id, enabled=True):
        """ Sets whether a plugin is enabled or not, thus should be loaded when
        the pipeline starts or not """
        if enabled:
            self._enabled_plugins.add(plugin_id)
        else:
            self._enabled_plugins.remove(plugin_id)

    def reset_plugin_settings(self, plugin_id):
        """ Resets all settings of a given plugin """
        for setting in self._settings[plugin_id].values():
            setting.value = setting.default

    def on_setting_changed(self, plugin_id, setting_id, value):
        """ Callback when a setting got changed. This will update the setting,
        and also call the callback for that setting, in case the plugin defined
        one. """
        if plugin_id not in self._settings or setting_id not in self._settings[plugin_id]:
            self.warn("Got invalid setting change:", plugin_id, "/", setting_id)
            return

        setting = self._settings[plugin_id][setting_id]
        setting.set_value(value)

        if plugin_id not in self._enabled_plugins:
            return

        if setting.runtime or setting.shader_runtime:
            update_method = self._instances[plugin_id], "update_" + setting_id
            if hasattr(*update_method):
                getattr(*update_method)()

        if setting.shader_runtime:
            self.init_defines()
            self._pipeline.stage_mgr.write_autoconfig()
            self._instances[plugin_id].reload_shaders()
