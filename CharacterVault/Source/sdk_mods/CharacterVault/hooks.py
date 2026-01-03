import os
import unrealsdk
from pathlib import Path
from mods_base import hook, get_pc, build_mod, SETTINGS_DIR, ENGINE
from unrealsdk.hooks import Type, Block, Unset
from unrealsdk.unreal import UObject, WrappedStruct, BoundFunction
from unrealsdk import logging, load_package,find_object
from ui_utils import OptionBox, OptionBoxButton
from typing import List, Dict, Optional, Callable

from .vault_hunters import VaultHunter, _VAULT_HUNTERS

Custom = "Custom"
@hook(
    hook_func="WillowGame.WillowGFxMenuHelperSaveGame:GetCharName",
    hook_type=Type.PRE,
)
def Display(obj: UObject, args: WrappedStruct, ret: any, func):
    global Custom
    # ClassName is an enum of 5 possible values
    if args.ClassName == 4:
        return (Block, Custom)
    classname = _VAULT_HUNTERS[args.ClassName].classname if args.bWantClassName else _VAULT_HUNTERS[args.ClassName].defaultName
    return (Block,classname)

def SelectCharacter(obj:UObject,PT3Selected=False,HighLevelCharacter=False):
    WillowGFxLobby = obj
    ControllerID = WillowGFxLobby.GetControllerId()

    def OnCharacterSelected(dlg, chosenBtn):
        nonlocal PT3Selected, WillowGFxLobby, ControllerID, HighLevelCharacter
        if chosenBtn.name == "Cancel":
            return        
        selected_info = None
        for info in _VAULT_HUNTERS:
            if info.classname == chosenBtn.name:
                selected_info = info
                break
        WPC = get_pc()
        if WPC == None:
            return
        WPC.ProfileLoad(selected_info.defaultProfile, True)    
        WSM = WPC.GetWillowGlobals().GetWillowSaveGameManager()
        profile = WSM.GetCachedPlayerProfile(ControllerID)
        if profile and selected_info.isCustom:
            profile.PlayerClassDefinition= ENGINE.DynamicLoadObject(selected_info.playerClassDefinition, unrealsdk.find_class("PlayerClassDefinition"), False)
    
        if PT3Selected:
            profile.PlaythroughsCompleted = 2
            profile.PlotMissionNumber = 1
            profile.LastVisitedTeleporter = "Fyrestone"
            profile.InventorySlotData.InventorySlotMax_Misc = 72
            if HighLevelCharacter:
                profile.ExpPoints = 3429728 # ExpLevel = 50
        profile.UIPreferences.CharacterName = selected_info.defaultName
        WSM.SetCachedPlayerProfile(ControllerID, profile)    
        charData = unrealsdk.make_struct("PlayerSaveData",CharacterClass=selected_info.charID,ExpLevel=1,CharacterName=selected_info.classname)
        li = unrealsdk.make_struct("LoadInfo")
        if not PT3Selected:
            WillowGFxLobby.LaunchSaveGame(0)
        else:
            WillowGFxLobby.FinishLoadGame(li)
            
    buttons = []    
    for info in _VAULT_HUNTERS:
        buttons.append(OptionBoxButton(name=info.classname,tip=info.charDesc))
    buttons.append(OptionBoxButton("Cancel", ""))    
    menu_title = "Select Character Class" if not PT3Selected else "Select PT3 Character Class"
    Dlg = OptionBox(title=menu_title,message="Choose a character class:",buttons=buttons,on_select=OnCharacterSelected,on_cancel=lambda _: None)
    Dlg.show()


__PT3FOUND = False
try:
    unrealsdk.load_package("gd_GameStages_PT3")
    __PT3FOUND = True
except:
    pass

@hook(
    hook_func="WillowGame.WillowGFxLobbyLoadCharacter:extNewCharacter",
    hook_type=Type.PRE,
)
def HandleNewCharacter(obj: UObject, args: WrappedStruct, ret: any, func):
    global _VAULT_HUNTERS

    PT3Selected = False
    HighLevelCharacter = False

    def PT3SupportDlg(dlg, chosenBtn):
        nonlocal PT3Selected,HighLevelCharacter, obj
        if chosenBtn.name == "Cancel":
            return
        if chosenBtn.name == "PT3 High Level Character":
            PT3Selected = True
            HighLevelCharacter = True
        if chosenBtn.name == "PT3 Character":
            PT3Selected = True
        SelectCharacter(obj,PT3Selected,HighLevelCharacter)

    if __PT3FOUND:
        difficultyButtons = [
        OptionBoxButton("Normal Character","You will start on Playthrough 1."),
        OptionBoxButton("PT3 Character","You will start on Playthrough 3."),
        OptionBoxButton("PT3 High Level Character","You will start on Playthrough 3 at a high level."),
        OptionBoxButton("Cancel",""),
        ]
        difficultyMessage = "Playthrough 3 was detected."
        difficultyTitle = "Type selection"
        diffDlg = OptionBox(title=difficultyTitle, message=difficultyMessage, buttons=difficultyButtons,on_select=PT3SupportDlg,on_cancel=lambda _:None)
        diffDlg.show()
    else:
        SelectCharacter(obj)

    return Block

#Very crash prone
@hook(
    hook_func="WillowGame.WillowGFxLobbyLoadCharacter:SetupNewCharacterMenu",
    hook_type=Type.POST,
)
def SetupNewCharacterMenu(obj: UObject, args: WrappedStruct, ret: any, func):
   global __PT3FOUND
   if __PT3FOUND:
       obj.menuAddItem(args.menuDepth, "New Character PT3", "newCharPT3", "extNewCharacter", "Focus:extFocusItem")
       obj.menuAddItem(args.menuDepth, "New 50 LVL Character PT3", "newCharPT3LVL50", "extNewCharacter", "Focus:extFocusItem")