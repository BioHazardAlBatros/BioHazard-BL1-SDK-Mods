import unrealsdk
from mods_base import hook, get_pc, build_mod, ENGINE
from unrealsdk.hooks import Type, Block, add_hook, remove_hook
from unrealsdk.unreal import UObject, WrappedStruct
from unrealsdk import logging, load_package
from ui_utils import OptionBox, OptionBoxButton

from .vault_hunters import VaultHunter, _VAULT_HUNTERS
from .api import get_character_info_from_class_definition, get_character_id_from_class_definition

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