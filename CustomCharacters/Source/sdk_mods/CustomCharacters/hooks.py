import os
import unrealsdk
from pathlib import Path
from mods_base import hook, get_pc, build_mod, SETTINGS_DIR, ENGINE
from unrealsdk.hooks import Type, Block
from unrealsdk.unreal import UObject, WrappedStruct, BoundFunction
from unrealsdk import logging, load_package,find_object
from ui_utils import OptionBox, OptionBoxButton
from typing import List, Dict, Optional, Callable

from .vault_hunters import VaultHunter, _VAULT_HUNTERS

@hook(
    hook_func="WillowGame.WillowGFxLobbyLoadCharacter:extNewCharacter",
    hook_type=Type.PRE,
)
def HandleNewCharacter(obj: UObject, args: WrappedStruct, ret: any, func):
    global _VAULT_HUNTERS
    PT3Selected = args.MenuTag == "newCharPT3"
    WillowGFxLobby = obj
    ControllerID = WillowGFxLobby.GetControllerId()

    def OnCharacterSelected(dlg, chosenBtn):
        nonlocal PT3Selected, WillowGFxLobby,ControllerID
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
            customClass = ENGINE.DynamicLoadObject(selected_info.playerClassDefinition, unrealsdk.find_class("PlayerClassDefinition"), False)
            if customClass:
                profile.PlayerClassDefinition = customClass
    
        if PT3Selected:
            profile.PlaythroughsCompleted = 2
            profile.PlotMissionNumber = 1
            profile.LastVisitedTeleporter = "Fyrestone"
            profile.InventorySlotData.InventorySlotMax_Misc = 72
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
    return Block

__PT3FOUND = os.path.exists(SETTINGS_DIR / "PT3GlobalUnlocker")
@hook(
    hook_func="WillowGame.WillowGFxLobbyLoadCharacter:SetupNewCharacterMenu",
    hook_type=Type.POST,
)
def SetupNewCharacterMenu(obj: UObject, args: WrappedStruct, ret: any, func):
   global __PT3FOUND
   if __PT3FOUND:
       obj.menuAddItem(args.menuDepth, "New Character PT3", "newCharPT3", "extNewCharacter", "Focus:extFocusItem")