import unrealsdk
from mods_base import hook, get_pc, build_mod, ENGINE
from unrealsdk.hooks import Type, Block
from unrealsdk.unreal import UObject, WrappedStruct
from unrealsdk import logging, load_package
from ui_utils import OptionBox, OptionBoxButton
#from typing import List, Dict, Optional, Callable

from .vault_hunters import VaultHunter, _VAULT_HUNTERS

#########################
__PT3FOUND = False
try:
    unrealsdk.load_package("gd_GameStages_PT3")
    assert __import__("Playthrough 3").__version_info__ >= (1, 2, 0) #, "Unsupported PT3 version detected"
    __PT3FOUND = True
except:
    logging.info("[Character Vault]: Compatible Playthrough 3 mod was not detected.")
    pass
#########################

@hook(
    hook_func="WillowGame.WillowGFxMenuHelperSaveGame:GetCharName",
    hook_type=Type.PRE,
)
def Display(obj: UObject, args: WrappedStruct, ret: any, func):
    if args.ClassName == 4:
        return (Block, "Custom")
    classname = _VAULT_HUNTERS[args.ClassName].classname if args.bWantClassName else _VAULT_HUNTERS[args.ClassName].defaultName
    return (Block,classname)

def SelectCharacterMenu(WillowGFxLobby:UObject,PT3Selected=False,HighLevelCharacter=False):
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

        WillowPlayerController = get_pc()
#        if WillowPlayerController == None:
#            return
        WillowPlayerController.ProfileLoad(selected_info.defaultProfile, True)    
        WSM = WillowPlayerController.GetWillowGlobals().GetWillowSaveGameManager()

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
            WillowGFxLobby.FinishLoadGame(li) # giving control flow to the pt3 mod to set up the save for PT3
        return
            
    buttons = []
    for info in _VAULT_HUNTERS:
        buttons.append(OptionBoxButton(name=info.classname,tip=info.charDesc))
    buttons.append(OptionBoxButton("Cancel", ""))    
    Dlg = OptionBox(title="Select Character Class",message="Choose a character class:",buttons=buttons,on_select=OnCharacterSelected,on_cancel=lambda _: None)
    Dlg.show()

@hook(
    hook_func="WillowGame.WillowGFxLobbyLoadCharacter:extNewCharacter",
    hook_type=Type.PRE,
)
def HandleNewCharacter(WillowGFxLobby: UObject, args: WrappedStruct, ret: any, func):
    PT3Selected = False
    HighLevelCharacter = False

    def PT3SupportDlg(dlg, chosenBtn):
        nonlocal PT3Selected,HighLevelCharacter, WillowGFxLobby
        if chosenBtn.name == "Cancel":
            return
        if chosenBtn.name == "PT3 High Level Character":
            PT3Selected = True
            HighLevelCharacter = True
        if chosenBtn.name == "PT3 Character":
            PT3Selected = True
        SelectCharacterMenu(WillowGFxLobby, PT3Selected, HighLevelCharacter)

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
        SelectCharacterMenu(WillowGFxLobby)

    return Block