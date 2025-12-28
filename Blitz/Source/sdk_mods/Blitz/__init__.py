import os
import unrealsdk
from pathlib import Path
from mods_base import hook, get_pc, build_mod, SETTINGS_DIR, ENGINE
from unrealsdk.hooks import Type, Block
from unrealsdk.unreal import UObject, WrappedStruct, BoundFunction
from unrealsdk import logging, load_package,find_object
from ui_utils import OptionBox, OptionBoxButton
from typing import List, Dict, Optional, Callable
from CustomCharacters import add_custom_character_class
import sys

@hook(
    hook_func="WillowGame.WillowGFxMoviePressStart:extContinue",
    hook_type=Type.POST,
)
def Test(obj: UObject, args: WrappedStruct, ret: any, func: BoundFunction):
    add_custom_character_class("Stormtrooper","Blitz The Stormtrooper","Blitz.Character.CharacterClass_Roland")
    Globals = find_object("GlobalsDefinition","gd_globals.General.Globals")
    Blitz1 = ENGINE.DynamicLoadObject("Blitz.Skills.Action.EndActionSkill", unrealsdk.find_class("SkillDefinition"), False)
    Blitz2 = ENGINE.DynamicLoadObject("Blitz.Skills.Action.AttemptGeminiDeploy", unrealsdk.find_class("SkillDefinition"), False)
    Globals.BasicSkills.append(Blitz1)
    Globals.BasicSkills.append(Blitz2)


build_mod(
    hooks=[Test],
    options=[],
    settings_file=Path(f"{SETTINGS_DIR}/Blitz.json")
)

__version__: str = "1.0.0"
__version_info__: tuple[int, ...] = (1, 0, 0)

logging.info(f"Blitz Test Loaded: {__version__}, {__version_info__}")