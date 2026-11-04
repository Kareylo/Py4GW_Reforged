from Py4GWCoreLib.enums_src.Model_enums import ModelID
from Sources.inventory_managment.auto_consumable import AutoConsumable

MODULE_NAME = "Auto Compass"
MODULE_ICON = "Assets/Textures/Module_Icons/Compass+.png"

_consumable = AutoConsumable(
    module_name=MODULE_NAME,
    item_label="compass",
    item_name="Bird's Eye Compass",
    regular_model=ModelID.Birds_Eye_Compass,
    infinite_model=ModelID.Infinite_Birds_Eye_Compass,
    ini_name="Widgets/AutoCompass/AutoCompass.ini",
    notes=("Solo missions and PvP areas refuse the compass",),
)


def update() -> None:
    _consumable.update()


def configure() -> None:
    _consumable.configure()


def tooltip() -> None:
    _consumable.tooltip()
