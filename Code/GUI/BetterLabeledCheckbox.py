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

from panda3d.core import Vec3

from ..Util.DebugObject import DebugObject
from .BetterCheckbox import BetterCheckbox
from .BetterOnscreenText import BetterOnscreenText
import direct.gui.DirectGuiGlobals as DGG


class BetterLabeledCheckbox(DebugObject):

    """ This is a checkbox, combined with a label. The arguments are
    equal to the Checkbox and OnscreenText arguments. """

    def __init__(self, parent=None, x=0, y=0, chb_callback=None,
                 chb_args=None, chb_checked=True, text="", text_size=18,
                 radio=False, text_color=None, expand_width=100, enabled=True):
        DebugObject.__init__(self)
        if chb_args is None:
            chb_args = []

        if text_color is None:
            text_color = Vec3(1)

        if not enabled:
            text_color = Vec3(1.0, 0, 0.28)

        self._checkbox = BetterCheckbox(
            parent=parent, x=x, y=y, enabled=enabled,
            callback=chb_callback, extra_args=chb_args,
            checked=chb_checked, radio=radio, expand_width=expand_width)
        self._text = BetterOnscreenText(x=x + 26, y=y + 10 + text_size // 4,
                                        text=text, align="left", parent=parent,
                                        size=text_size, color=text_color, may_change=True)

        if enabled:
            self._checkbox._node.bind(DGG.WITHIN, self._on_node_enter)
            self._checkbox._node.bind(DGG.WITHOUT, self._on_node_leave)

    def _on_node_enter(self, *args):
        """ Internal callback when the node gets hovered """
        self._text._node["fg"] = (0.5, 0.5, 0.5, 1.0)

    def _on_node_leave(self, *args):
        """ Internal callback when the node gets no longer hovered """
        self._text._node["fg"] = (0.4, 0.4, 0.4, 1.0)

    def get_checkbox(self):
        """ Returns a handle to the checkbox """
        return self._checkbox

    def get_label(self):
        """ Returns a handle to the label """
        return self._text
