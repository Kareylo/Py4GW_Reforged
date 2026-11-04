"""
Auto Compass widget.

Uses a Bird's Eye Compass once each time an explorable map loads. The effect
lasts for the whole instance, so one use per load is enough.

The widget re-arms on real map loads rather than on `MapValid()`, because
`MapValid()` is also false during cinematics and a mission cutscene would
otherwise spend a second finite compass in the same instance.
"""

import PyImGui

from Py4GWCoreLib import GLOBAL_CACHE, Color, ImGui, Map, Routines
from Py4GWCoreLib.enums_src.Model_enums import ModelID
from Py4GWCoreLib.py4gwcorelib_src.Console import Console, ConsoleLog
from Py4GWCoreLib.py4gwcorelib_src.Settings import Settings
from Py4GWCoreLib.py4gwcorelib_src.Timer import ThrottledTimer
from Py4GWCoreLib.py4gwcorelib_src.WidgetManager import get_widget_handler

MODULE_NAME = "Auto Compass"
MODULE_ICON = "Assets/Textures/Module_Icons/Compass+.png"

INI_NAME = "Widgets/AutoCompass/AutoCompass.ini"
SETTLE_DELAY_MS = 2000

_handled_this_load = False
_settle_timer = ThrottledTimer(SETTLE_DELAY_MS)


def _cfg() -> Settings:
    return Settings(INI_NAME, "account")


def _prefer_infinite() -> bool:
    return _cfg().get_bool("Main", "prefer_infinite", True)


def _models_in_use_order() -> tuple[int, int]:
    regular = ModelID.Birds_Eye_Compass.value
    infinite = ModelID.Infinite_Birds_Eye_Compass.value
    return (infinite, regular) if _prefer_infinite() else (regular, infinite)


def _use_compass() -> None:
    for model_id in _models_in_use_order():
        item_id = GLOBAL_CACHE.Inventory.GetFirstModelID(model_id)
        if item_id:
            GLOBAL_CACHE.Inventory.UseItem(item_id)
            ConsoleLog(MODULE_NAME, f"Used compass (model {model_id}).", Console.MessageType.Info)
            return


def update() -> None:
    global _handled_this_load

    if Map.IsMapLoading() or not Map.IsExplorable():
        _handled_this_load = False
        _settle_timer.Reset()
        return

    if _handled_this_load or not Routines.Checks.Map.MapValid() or not _settle_timer.IsExpired():
        return

    _handled_this_load = True
    _use_compass()


def configure() -> None:
    expanded, keep_open = ImGui.BeginWithClose(
        INI_NAME, f"{MODULE_NAME} Configure", True, PyImGui.WindowFlags.AlwaysAutoResize
    )
    if expanded:
        prefer_infinite = _prefer_infinite()
        new_prefer_infinite = PyImGui.checkbox("Prefer infinite compass##auto_compass", prefer_infinite)
        if new_prefer_infinite != prefer_infinite:
            _cfg().set_bool("Main", "prefer_infinite", new_prefer_infinite)

        PyImGui.text_wrapped("The other compass is used when the preferred one is not in your bags.")
    ImGui.End(INI_NAME)

    if not keep_open:
        get_widget_handler().set_widget_configuring(MODULE_NAME, False)


def tooltip() -> None:
    PyImGui.begin_tooltip()

    title_color = Color(255, 200, 100, 255)
    ImGui.push_font("Regular", 20)
    PyImGui.text_colored(MODULE_NAME, title_color.to_tuple_normalized())
    ImGui.pop_font()

    PyImGui.spacing()
    PyImGui.separator()
    PyImGui.spacing()

    PyImGui.text("Uses a Bird's Eye Compass once when an explorable map loads.")
    PyImGui.bullet_text("Option: prefer the Infinite Bird's Eye Compass")
    PyImGui.bullet_text("Solo missions and PvP areas refuse the compass")

    PyImGui.end_tooltip()
