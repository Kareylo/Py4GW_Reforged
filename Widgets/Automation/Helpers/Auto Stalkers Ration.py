from Py4GWCoreLib.enums_src.Model_enums import ModelID
from Sources.inventory_managment.auto_consumable import AutoConsumable

MODULE_NAME = "Auto Stalkers Ration"
MODULE_ICON = "Assets/Textures/Module_Icons/Pycons.png"

_consumable = AutoConsumable(
    module_name=MODULE_NAME,
    item_label="ration",
    item_name="Stalker's Ration",
    regular_model=ModelID.Stalkers_Ration,
    infinite_model=ModelID.Infinite_Stalkers_Ration,
    ini_name="Widgets/AutoStalkersRation/AutoStalkersRation.ini",
)


def update() -> None:
    _consumable.update()


def configure() -> None:
    _consumable.configure()


def tooltip() -> None:
    _consumable.tooltip()
