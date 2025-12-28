from dataclasses import dataclass

@dataclass
class VaultHunter:
    charID: int = 0
    classname: str = "Missing name"
    charDesc: str = "Missing description"
    playerClassDefinition: str = "gd_Roland.Character.CharacterClass_Roland"
    defaultProfile: str = "default roland"
    isCustom: bool = False


_VAULT_HUNTERS = [
    VaultHunter(charID=0,classname="Soldier",charDesc="Default Soldier",playerClassDefinition="gd_Roland.Character.CharacterClass_Roland",defaultProfile="default roland"),
    VaultHunter(charID=1,classname="Hunter",charDesc="Default Hunter",playerClassDefinition="gd_mordecai.Character.CharacterClass_Mordecai",defaultProfile="default mordecai"),
    VaultHunter(charID=2,classname="Siren",charDesc="Default Siren",playerClassDefinition="gd_lilith.Character.CharacterClass_Lilith",defaultProfile="default lilith"),
    VaultHunter(charID=3,classname="Berserker",charDesc="Default Berserker",playerClassDefinition="gd_Brick.Character.CharacterClass_Brick",defaultProfile="default brick"),
]