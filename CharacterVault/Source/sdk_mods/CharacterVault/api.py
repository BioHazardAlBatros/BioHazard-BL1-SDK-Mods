import unrealsdk
from mods_base import build_mod, ENGINE
from unrealsdk import logging
from unrealsdk.unreal import UObject
from typing import List, Dict, Optional, Callable
from .vault_hunters import VaultHunter, _VAULT_HUNTERS, _CLASS_IDS

def add_custom_character_class(NewClassname:str, NewCharDesc: str, NewPlayerClassDefinition: str, NewName:str,BaseVanillaClass: int = 0, SpawnCallback: Optional[Callable] = None) -> int:
    HasClassExclusiveNewItems = BaseVanillaClass < 0 or BaseVanillaClass > 3
    if HasClassExclusiveNewItems:
        BaseVanillaClass = 0
    
    newID = len(_VAULT_HUNTERS)
    _CLASS_IDS[NewPlayerClassDefinition] = newID
    _VAULT_HUNTERS.append(
    VaultHunter(
        charID = newID,
        classname = NewClassname,
        charDesc = NewCharDesc,
        playerClassDefinition = NewPlayerClassDefinition,
        defaultName = NewName,
        defaultProfile = _VAULT_HUNTERS[BaseVanillaClass].defaultProfile,
        isCustom = HasClassExclusiveNewItems,
        onStart = SpawnCallback
    ))
   
    logging.info(f"[Character Vault]: New vault hunter available - {NewCharDesc}")
    return newID

def get_character_definitions():
    return [vh.playerClassDefinition for vh in _VAULT_HUNTERS]

def get_character_count() -> int:
    return len(_VAULT_HUNTERS)

def get_character_id_from_class_definition(playerClassDefinition: str) -> int:
    return _CLASS_IDS.get(playerClassDefinition, -1)

def get_character_info(charID: int):
    if 0 <= charID < len(_VAULT_HUNTERS):
        return _VAULT_HUNTERS[charID]
    return None

def get_character_info_from_class_definition(WillowPlayerController: UObject) -> int:
    return get_character_info(get_character_id_from_class_definition(WillowPlayerController.PlayerClass._path_name()))
