import unrealsdk
from mods_base import build_mod, ENGINE
from unrealsdk import logging
from typing import List, Dict, Optional, Callable

from .hooks import HandleNewCharacter, Display
from .vault_hunters import VaultHunter, _VAULT_HUNTERS

def add_custom_character_class(NewClassname:str, NewCharDesc: str, NewPlayerClassDefinition: str, NewName:str,BaseVanillaClass: int = 0):
    if BaseVanillaClass < 0 or BaseVanillaClass > 3:
        BaseVanillaClass = 0
    
    newID = len(_VAULT_HUNTERS)
    _VAULT_HUNTERS.append(
    VaultHunter(
        charID = len(_VAULT_HUNTERS),
        classname = NewClassname,
        charDesc = NewCharDesc,
        playerClassDefinition = NewPlayerClassDefinition,
        defaultName = NewName,
        defaultProfile = _VAULT_HUNTERS[BaseVanillaClass].defaultProfile,
        isCustom = True
    ))
    
    return newID

def get_character_definitions():
    return [vh.playerClassDefinition for vh in _VAULT_HUNTERS]

## Probably redundant ##

def get_character_count():
    return len(_VAULT_HUNTERS)

def get_character_info(charID: int):
    if 0 <= charID < len(_VAULT_HUNTERS):
        return _VAULT_HUNTERS[charID]
    return None

####

build_mod(hooks=[HandleNewCharacter,Display])

__version__: str
__version_info__: tuple[int, ...]

logging.info(f"Character Vault Loaded: {__version__}, {__version_info__}")