import unrealsdk
from mods_base import hook, get_pc, build_mod, ENGINE
from unrealsdk.hooks import Type, Block, add_hook, remove_hook
from unrealsdk.unreal import UObject, WrappedStruct
from unrealsdk import logging, load_package
from ui_utils import OptionBox, OptionBoxButton

from .vault_hunters import VaultHunter, _VAULT_HUNTERS
from .api import get_character_info_from_class_definition, get_character_id_from_class_definition, get_asset_path
from .badapple import ShowApple

ASType = unrealsdk.find_enum("ASType")

def ReplaceClassRequirementString(obj, path, item):
    if item is None or "WillowWeapon" in item.Class.Name:
        return
    req_id = item.DefinitionData.ItemDefinition.RequiredCharacter - 1
    template = obj.LocText("ClassRequirement","StatusMenu","WillowGame")[1]
    obj.SetVariableString(path, template % _VAULT_HUNTERS[req_id].classname)

def RewardsScreen(obj, args, ret, func):
    if obj.CardContents.Inv:
        ReplaceClassRequirementString(obj, "reward.card1.classreq.requirement.text", obj.CardContents.Inv)

def InventoryVendorScreen(obj, args, ret, func):
    ItemFrozenOnTheRight = ("Vending" in obj.Class.Name and obj.bOnItemOfTheDay) or ("Status" in obj.Class.Name and not obj.bInListView)
    if not obj.IsComparing():
        ReplaceClassRequirementString(obj, "topLevel_mc.card1.classreq.requirement.text", obj.DEBUGGetSelectedInventory())
        return
    ReplaceClassRequirementString(obj, "topLevel_mc.card2.classreq.requirement.text", obj.ActiveTextList.GetHighlightedObject())
    ReplaceClassRequirementString(obj, "topLevel_mc.card1.classreq.requirement.text", obj.FrozenThing)

def BankScreen(obj, args, ret, func):
    ReplaceClassRequirementString(obj, "currentPage.card1.classreq.requirement.text", obj.LeftSideTextList.GetHighlightedObject())
    ReplaceClassRequirementString(obj, "currentPage.card2.classreq.requirement.text", obj.RightSideTextList.GetHighlightedObject())

def PickupScreen(obj, args, ret, func):
    if obj.bReadyToDisplay and obj.MyHUDOwner.ItemComparison[0]:
        ReplaceClassRequirementString(obj, "inventory.card1.classreq.requirement.text", obj.MyHUDOwner.ItemComparison[0])

#def load_custom_icon(hud: UObject, asset : str, movie_path : str):
#    asset_path = get_asset_path(asset)
#    hud.SingleArgInvokeS(f"{movie_path}.loadMovie",asset_path)
#    hud.SingleArgInvokeS(f"{movie_path}.gotoAndStop","ready")


def UpdateActionSkill(obj, args, ret, func):
    PlayerController = obj.WPlayerOwner[args.PlayerNum]
    if PlayerController is None or PlayerController.PlayerClass is None:
        return
    classID = PlayerController.PlayerClass.CharacterName
    if classID < 4:
        return
    # to do: figure out how to preserve animation and text
    # the animation is broken, but present in the file
    # other notable paths
    # p1.coop1.character, p1.coop2.character, p1.coop3.character, p1.dying1
    #obj.SetVariableBool("p1.character.flash._visible",False)
    obj.SingleArgInvokeS("p1.character.gotoAndStop","roland")
    #ShowApple(obj)
    #load_custom_icon(obj,"frames.swf","p1.character.flash","plswork",9) # overlays on top, no matter what, doesn't have animation
    

def UpdateActiveActionSkill(obj,args, ret, func):
    if obj.PlayerClass is None or obj.PlayerClass.CharacterName < 4:
        return
    # to do: the action bar doesn't reappear after closing inventory
    # to do: figure out how to replace to custom action bar
    #if args.bActivated:
    obj.MyHud.HUDMovie.SingleArgInvokeS("p1.dying1.gotoAndStop","roland_action")