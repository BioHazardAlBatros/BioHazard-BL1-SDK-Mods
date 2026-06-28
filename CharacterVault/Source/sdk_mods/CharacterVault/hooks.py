import unrealsdk
from mods_base import hook, get_pc, build_mod, ENGINE
from unrealsdk.hooks import Type, Block, add_hook, remove_hook
from unrealsdk.unreal import UObject, WrappedStruct
from unrealsdk import logging, load_package
from ui_utils import OptionBox, OptionBoxButton

from .vault_hunters import VaultHunter, _VAULT_HUNTERS
from .api import get_character_info_from_class_definition, get_character_id_from_class_definition

####### PT3 check #######
__PT3FOUND = False
try:
    __PT3FOUND = __import__("Playthrough 3").__version_info__ >= (1, 2, 0) # "Compatible PT3 version"
except:
    logging.info("[Character Vault]: Compatible Playthrough 3 mod was not detected.")
    pass
#########################

@hook(hook_func="WillowGame.WillowPlayerController:SpawningProcessComplete", hook_type=Type.POST)
def OnSpawn(WillowPlayerController: UObject, args: WrappedStruct, ret: any, func):
    CurrentVH = get_character_info_from_class_definition(WillowPlayerController)
    if CurrentVH.isCustom:
        WillowPlayerController.PlayerClass.CharacterName = CurrentVH.charID
    if CurrentVH.onStart != None:
        CurrentVH.onStart()

@hook(hook_func="WillowGame.WillowGFxLobbyLoadCharacter:SavesUpdated", hook_type=Type.PRE)
def PostSavesUpdated(obj: UObject, args: WrappedStruct, ret: any, func):
    SaveGameHelper = obj.SaveGameHelper
    if SaveGameHelper is None:
        return
    for playerSave in SaveGameHelper.SaveGames:
        if playerSave.CharacterClass == 4:  # CN_MAX
            classID = get_character_id_from_class_definition(playerSave.ClassName)
            if classID != -1:
                playerSave.CharacterClass = classID

@hook(hook_func="WillowGame.WillowGFxMenuHelperSaveGame:GetCharName", hook_type=Type.PRE)
def Display(obj: UObject, args: WrappedStruct, ret: any, func):
    classname = _VAULT_HUNTERS[args.ClassName].classname if args.bWantClassName else _VAULT_HUNTERS[args.ClassName].defaultName
    return (Block,classname)

@hook(hook_func="WillowGame.WillowItem:IsPlayerRestricted", hook_type=Type.PRE)
def IsPlayerRestricted(obj: UObject, args: WrappedStruct, ret: any, func):
    requiredClassID = obj.DefinitionData.ItemDefinition.RequiredCharacter
    if requiredClassID == 0:
        return (Block, False)
    WillowPlayerController = args.PawnToCheck.Controller
    if WillowPlayerController.Class.Name == "WillowMind":
        logging.info(obj)
        return None
    if WillowPlayerController is None or WillowPlayerController.PlayerClass is None:
        return None
    classID = WillowPlayerController.PlayerClass.CharacterName
    return (Block, (classID + 1) != requiredClassID)

@hook(hook_func="WillowGame.WillowItem:TranslateUseFailure", hook_type=Type.POST)
def TranslateUseFailure(obj: UObject, args: WrappedStruct, ret: any, func):
    if args.FailureFlag != 16:
        return
    args.Output = "Hello World %s"
    print(args)
    return

def OnCharacterSelected(dlg, chosenBtn, PT3Selected, WillowGFxLobby, ControllerID, HighLevelCharacter):
    if chosenBtn.name == "Cancel":
        return
    selected_info = None

    for info in _VAULT_HUNTERS:
        if info.classname == chosenBtn.name:
            selected_info = info
            break
    WillowPlayerController = get_pc()
    WillowPlayerController.ProfileLoad(selected_info.defaultProfile, True)    
    WSM = WillowPlayerController.GetWillowGlobals().GetWillowSaveGameManager()

    profile = WSM.GetCachedPlayerProfile(ControllerID)
    if profile: # and selected_info.isCustom:
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
    charData = unrealsdk.make_struct("PlayerSaveData",CharacterClass=selected_info.charID,ExpLevel=1,CharacterName=selected_info.classname, ClassName=selected_info.playerClassDefinition)
    li = unrealsdk.make_struct("LoadInfo")
    if not PT3Selected:
        WillowGFxLobby.LaunchSaveGame(0)
    else:
        WillowGFxLobby.FinishLoadGame(li) # giving control flow to the pt3 mod to set up the save for PT3
    return

def PT3SupportDlg(dlg, chosenBtn, WillowGFxLobby):
    PT3Selected = False
    HighLevelCharacter = False
    if chosenBtn.name == "Cancel":
        return
    if chosenBtn.name == "PT3 High Level Character":
        PT3Selected = True
        HighLevelCharacter = True
    if chosenBtn.name == "PT3 Character":
        PT3Selected = True
    SelectCharacterMenu(WillowGFxLobby, PT3Selected, HighLevelCharacter)
    return

def SelectCharacterMenu(WillowGFxLobby:UObject, PT3Selected=False, HighLevelCharacter=False):
    ControllerID = WillowGFxLobby.GetControllerId()
    buttons = []
    for info in _VAULT_HUNTERS:
        buttons.append(OptionBoxButton(name=info.classname,tip=info.charDesc))
    buttons.append(OptionBoxButton("Cancel", ""))    
    Dlg = OptionBox(title="Select Character Class",message="Choose a character class:",buttons=buttons,
        on_select=lambda dlg,chosenBtn: OnCharacterSelected(dlg,chosenBtn,PT3Selected,WillowGFxLobby,ControllerID,HighLevelCharacter),
        on_cancel=lambda _: None )
    Dlg.show()

@hook(hook_func="WillowGame.WillowGFxLobbyLoadCharacter:extNewCharacter", hook_type=Type.PRE)
def HandleNewCharacter(WillowGFxLobby: UObject, args: WrappedStruct, ret: any, func):
    if not __PT3FOUND:
        SelectCharacterMenu(WillowGFxLobby)
    else:
        difficultyButtons = [
        OptionBoxButton("Normal Character","You will start on Playthrough 1."),
        OptionBoxButton("PT3 Character","You will start on Playthrough 3."),
        OptionBoxButton("PT3 High Level Character","You will start on Playthrough 3 at a high level."),
        OptionBoxButton("Cancel",""),
        ]
        difficultyMessage = "Playthrough 3 was detected."
        difficultyTitle = "Type selection"
        diffDlg = OptionBox(title=difficultyTitle, message=difficultyMessage, buttons=difficultyButtons, 
            on_select=lambda dlg,chosenBtn: PT3SupportDlg(dlg,chosenBtn,WillowGFxLobby),
            on_cancel=lambda _:None )
        diffDlg.show()
    return Block

try:
    FOVMod = __import__("FOV and sprint rotation fix")
    def AdjustFOV(WillowPlayerController, __args, __ret, __func):
        CurrentVH = get_character_info_from_class_definition(WillowPlayerController)
        ENGINE.DynamicLoadObject(CurrentVH.playerClassDefinition, unrealsdk.find_class("PlayerClassDefinition"), False).FOV = FOVMod.WorldFOV.value
        FOVMod.WorldFOV.on_change(FOVMod.WorldFOV,FOVMod.WorldFOV.value)
    add_hook("WillowGame.WillowPlayerController:SpawningProcessComplete", Type.POST, "AdjustFOV", AdjustFOV)
except:
    logging.info("[Character Vault]: FOV and sprint rotation fix not detected.")
    pass