import os
import unrealsdk
from pathlib import Path
from mods_base import hook, get_pc, build_mod, SETTINGS_DIR, ENGINE
from unrealsdk.hooks import Type, Block
from unrealsdk.unreal import UObject, WrappedStruct, BoundFunction
from unrealsdk import logging, load_package,find_object
from ui_utils import OptionBox, OptionBoxButton
from typing import List, Dict, Optional, Callable

from .hooks import SetupNewCharacterMenu, HandleNewCharacter
from .vault_hunters import VaultHunter, _VAULT_HUNTERS

def add_custom_character_class(NewClassname:str, NewCharDesc: str, NewPlayerClassDefinition: str, BaseVanillaClass: int = 0, PlayerProfileDefinition:str = ""):
    if BaseVanillaClass < 0 or BaseVanillaClass > 3:
        BaseVanillaClass = 0
    
    newID = len(_VAULT_HUNTERS)
    _VAULT_HUNTERS.append(
    VaultHunter(
        charID = len(_VAULT_HUNTERS),
        classname = NewClassname,
        charDesc = NewCharDesc,
        playerClassDefinition = NewPlayerClassDefinition,
        defaultProfile = _VAULT_HUNTERS[BaseVanillaClass].defaultProfile,
        isCustom = True
    ))
    
    return newID

def get_character_definitions():
    return [vh.playerClassDefinition for vh in _VAULT_HUNTERS]

def get_character_count():
    return len(_VAULT_HUNTERS)

def get_character_info(charID: int):
    if 0 <= charID < len(_VAULT_HUNTERS):
        return _VAULT_HUNTERS[charID]
    return None

build_mod(
    hooks=[SetupNewCharacterMenu,HandleNewCharacter],
    options=[],
    settings_file=Path(f"{SETTINGS_DIR}/CustomCharacters.json")
)

__version__: str = "1.0.0"
__version_info__: tuple[int, ...] = (1, 0, 0)

logging.info(f"Custom Characters Loaded: {__version__}, {__version_info__}")