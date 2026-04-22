import unrealsdk
from mods_base import hook, get_pc, build_mod, SETTINGS_DIR, ENGINE
from unrealsdk.hooks import Type, Block
from unrealsdk.unreal import UObject, WrappedStruct, BoundFunction
from unrealsdk import logging,find_object, find_class
from CharacterVault import add_custom_character_class

BlitzCharID = None

def load_obj(objname,classobj):
    return ENGINE.DynamicLoadObject(objname, classobj, False)

@hook( hook_func="WillowGame.WillowGFxMoviePressStart:extContinue", hook_type=Type.POST )
def ModifyGlobals(obj: UObject, args: WrappedStruct, ret: any, func: BoundFunction):
    if BlitzCharID == None:
        return
    Globals = find_object("GlobalsDefinition","gd_globals.General.Globals")
    Blitz1 = load_obj("Blitz.Skills.Action.EndActionSkill", unrealsdk.find_class("SkillDefinition"))
    Blitz2 = load_obj("Blitz.Skills.Action.AttemptGeminiDeploy", unrealsdk.find_class("SkillDefinition"))
    Globals.BasicSkills.append(Blitz1)
    Globals.BasicSkills.append(Blitz2)
    ItemDefinition = find_class("ItemDefinition")
    E1 = load_obj("Blitz.Artifacts.A_Item.ElementalArtifact_Blitz",ItemDefinition)
    E2 = load_obj("Blitz.Artifacts.A_Item.ElementalArtifact_Blitz_Gemini",ItemDefinition)
    E3 = load_obj("Blitz.Artifacts.A_Item.ElementalArtifact_Blitz_HoverTurret",ItemDefinition)
    E4 = load_obj("Blitz.Artifacts.A_Item.ElementalArtifact_Blitz_Qi",ItemDefinition)
    COMs = load_obj("Blitz.COMs.A_Item.Item_CommandDeck_Blitz",ItemDefinition)
    E1.ObjectFlags |= 0x4000
    E2.ObjectFlags |= 0x4000
    E3.ObjectFlags |= 0x4000
    E4.ObjectFlags |= 0x4000
    COMs.ObjectFlags |= 0x4000
    # 0 - Any, 1 - Roland, 2 - Lilith, 3 - Mordecai, 4 - Brick, so offset by 1 is required
    E1.RequiredCharacter = BlitzCharID + 1
    E2.RequiredCharacter = BlitzCharID + 1
    E3.RequiredCharacter = BlitzCharID + 1
    E4.RequiredCharacter = BlitzCharID + 1
    COMs.RequiredCharacter = BlitzCharID + 1
    return

def OnPlayerSpawn():
    pawn = get_pc().MyWillowPawn
    pawn.CameraScale = 2.0
    pawn.CameraScaleUp = 2.3
    pawn.CameraScaleRight = 2.0

BlitzCharID = add_custom_character_class("Stormtrooper","Blitz The Stormtrooper","Blitz.Character.CharacterClass_Roland", "Blitz", BaseVanillaClass = 4, SpawnCallback = OnPlayerSpawn)
#BlitzCharID = add_custom_character_class("%d\0","Blitz The Stormtrooper","Blitz.Character.CharacterClass_Roland", "Blitz", BaseVanillaClass = 4, SpawnCallback = OnPlayerSpawn)

build_mod(hooks=[ModifyGlobals])