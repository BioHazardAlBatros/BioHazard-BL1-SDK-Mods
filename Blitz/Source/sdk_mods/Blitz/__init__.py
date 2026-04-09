import unrealsdk
from mods_base import hook, get_pc, build_mod, SETTINGS_DIR, ENGINE
from unrealsdk.hooks import Type, Block
from unrealsdk.unreal import UObject, WrappedStruct, BoundFunction
from unrealsdk import logging,find_object
from CharacterVault import add_custom_character_class

@hook( hook_func="WillowGame.WillowGFxMoviePressStart:extContinue", hook_type=Type.POST )
def ImportCharacter(obj: UObject, args: WrappedStruct, ret: any, func: BoundFunction):
    add_custom_character_class("Stormtrooper","Blitz The Stormtrooper","Blitz.Character.CharacterClass_Roland")
    Globals = find_object("GlobalsDefinition","gd_globals.General.Globals")
    Blitz1 = ENGINE.DynamicLoadObject("Blitz.Skills.Action.EndActionSkill", unrealsdk.find_class("SkillDefinition"), False)
    Blitz2 = ENGINE.DynamicLoadObject("Blitz.Skills.Action.AttemptGeminiDeploy", unrealsdk.find_class("SkillDefinition"), False)
    Globals.BasicSkills.append(Blitz1)
    Globals.BasicSkills.append(Blitz2)

# third person camera setup
#    player = get_pc().MyWillowPawn
#    player.CameraScale = 12.0
#    player.CameraScaleRight = 5.0
#    player.CameraScaleUp = 2.5

build_mod(hooks=[ImportCharacter])
logging.info(f"Character Vault: New Character Class from Blitz The Stormtrooper")