"""
Shared behaviour for widgets that use a consumable once per explorable map load.

Each widget supplies a regular and an infinite model ID. Their effects last for
the whole instance, so one use per load is enough.

Re-arming happens on real map loads rather than on `MapValid()`, because
`MapValid()` is also false during cinematics and a mission cutscene would
otherwise spend a second finite item in the same instance.
"""

import PyImGui

from Py4GWCoreLib import GLOBAL_CACHE, Color, ImGui, Map, Routines
from Py4GWCoreLib.enums_src.Model_enums import ModelID
from Py4GWCoreLib.py4gwcorelib_src.Console import Console, ConsoleLog
from Py4GWCoreLib.py4gwcorelib_src.Settings import Settings
from Py4GWCoreLib.py4gwcorelib_src.Timer import ThrottledTimer
from Py4GWCoreLib.py4gwcorelib_src.WidgetManager import get_widget_handler

SETTLE_DELAY_MS = 2000


class AutoConsumable:
    def __init__(
        self,
        module_name: str,
        item_label: str,
        item_name: str,
        regular_model: ModelID,
        infinite_model: ModelID,
        ini_name: str,
        notes: tuple[str, ...] = (),
    ) -> None:
        self.module_name = module_name
        self.item_label = item_label
        self.item_name = item_name
        self.regular_model = regular_model.value
        self.infinite_model = infinite_model.value
        self.ini_name = ini_name
        self.notes = notes
        self._handled_this_load = False
        self._settle_timer = ThrottledTimer(SETTLE_DELAY_MS)

    def _cfg(self) -> Settings:
        return Settings(self.ini_name, "account")

    def _prefer_infinite(self) -> bool:
        return self._cfg().get_bool("Main", "prefer_infinite", True)

    def _models_in_use_order(self) -> tuple[int, int]:
        if self._prefer_infinite():
            return self.infinite_model, self.regular_model
        return self.regular_model, self.infinite_model

    def _use_item(self) -> None:
        for model_id in self._models_in_use_order():
            item_id = GLOBAL_CACHE.Inventory.GetFirstModelID(model_id)
            if item_id:
                GLOBAL_CACHE.Inventory.UseItem(item_id)
                ConsoleLog(self.module_name, f"Used {self.item_label} (model {model_id}).", Console.MessageType.Info)
                return

    def update(self) -> None:
        if Map.IsMapLoading() or not Map.IsExplorable():
            self._handled_this_load = False
            self._settle_timer.Reset()
            return

        if self._handled_this_load or not Routines.Checks.Map.MapValid() or not self._settle_timer.IsExpired():
            return

        self._handled_this_load = True
        self._use_item()

    def configure(self) -> None:
        expanded, keep_open = ImGui.BeginWithClose(
            self.ini_name, f"{self.module_name} Configure", True, PyImGui.WindowFlags.AlwaysAutoResize
        )
        if expanded:
            prefer_infinite = self._prefer_infinite()
            new_prefer_infinite = PyImGui.checkbox(
                f"Prefer infinite {self.item_label}##{self.module_name}", prefer_infinite
            )
            if new_prefer_infinite != prefer_infinite:
                self._cfg().set_bool("Main", "prefer_infinite", new_prefer_infinite)

            PyImGui.text_wrapped(f"The other {self.item_label} is used when the preferred one is not in your bags.")
        ImGui.End(self.ini_name)

        if not keep_open:
            get_widget_handler().set_widget_configuring(self.module_name, False)

    def tooltip(self) -> None:
        PyImGui.begin_tooltip()

        title_color = Color(255, 200, 100, 255)
        ImGui.push_font("Regular", 20)
        PyImGui.text_colored(self.module_name, title_color.to_tuple_normalized())
        ImGui.pop_font()

        PyImGui.spacing()
        PyImGui.separator()
        PyImGui.spacing()

        PyImGui.text(f"Uses a {self.item_name} once when an explorable map loads.")
        PyImGui.bullet_text(f"Option: prefer the Infinite {self.item_name}")
        for note in self.notes:
            PyImGui.bullet_text(note)

        PyImGui.end_tooltip()
