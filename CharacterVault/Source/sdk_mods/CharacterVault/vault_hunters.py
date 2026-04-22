from dataclasses import dataclass
from typing import Callable, Optional, Dict

@dataclass
class VaultHunter:
    charID: int = 0
    classname: str = "Missing class name"
    charDesc: str = "Missing description"
    playerClassDefinition: str = "gd_Roland.Character.CharacterClass_Roland"
    defaultName : str = "Missing default name"
    defaultProfile: str = "default roland"
    isCustom: bool = False
    onStart: Optional[Callable] = None

_VAULT_HUNTERS = [
    VaultHunter(charID=0,classname="Soldier",charDesc="Default Soldier",playerClassDefinition="gd_Roland.Character.CharacterClass_Roland",defaultName="Roland",defaultProfile="default roland"),
    VaultHunter(charID=1,classname="Hunter",charDesc="Default Hunter",playerClassDefinition="gd_mordecai.Character.CharacterClass_Mordecai",defaultName="Mordecai",defaultProfile="default mordecai"),
    VaultHunter(charID=2,classname="Siren",charDesc="Default Siren",playerClassDefinition="gd_lilith.Character.CharacterClass_Lilith",defaultName="Lilith",defaultProfile="default lilith"),
    VaultHunter(charID=3,classname="Berserker",charDesc="Default Berserker",playerClassDefinition="gd_Brick.Character.CharacterClass_Brick",defaultName="Brick",defaultProfile="default brick"),
]

_CLASS_IDS: Dict[str, int] = {
    vh.playerClassDefinition: vh.charID
    for vh in _VAULT_HUNTERS
}