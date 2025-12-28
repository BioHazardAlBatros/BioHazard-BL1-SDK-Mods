import os
import unrealsdk#type: ignore

from pathlib import Path#type: ignore
from unrealsdk.hooks import Type, add_hook, remove_hook, Block#type: ignore
from unrealsdk.unreal import UObject, WrappedStruct, BoundFunction#type: ignore
from mods_base import hook, get_pc #type: ignore
from mods_base.options import BaseOption, BoolOption#type: ignore
from mods_base import SETTINGS_DIR, SliderOption#type: ignore
from mods_base import build_mod#type: ignore
from unrealsdk import logging, find_object#type: ignore

from ui_utils import OptionBox, OptionBoxButton

bGlobalPT3Unlocked = os.path.exists(SETTINGS_DIR / "PT3GlobalUnlocker")
bCreatingPT3Character = False

bPrepWorkDone = False

GameStage: SliderOption = SliderOption("Playthrough 3 Base Level",
            1.0,
            -15.0,
            15.0,
            1.0,
            False,
            description="The base level for enemies and missions will be set to character level plus this number.",
            on_change = lambda _, 
            new_value: SetGlobalGameStage(_, new_value))


GlobalsDef = None
GlobalGameStage = None
GlobalGameStageSetting = None

ResetRequested = False
BadlandsLoaded = False

ResetMissions = True
ResetLevel = False
ResetInventory = False
ResetWeaponProficiency = False
ResetAmmoSDU = False

WillowGFxLobbySinglePlayer = None
Intro = unrealsdk.find_object("MissionDefinition","Z0_Missions.Missions.M_IntroStateSaver")
DocIsIn = unrealsdk.find_object("MissionDefinition","Z0_Missions.Missions.M_AccessStores")
SkagsAtGate = unrealsdk.find_object("MissionDefinition","Z0_Missions.Missions.M_KillSkags_Zed")

def ResetPlaythrough3(PC:UObject):
    IntroStruct =unrealsdk.make_struct("MissionStatus",
                                        MissionDef=Intro,
                                        Status=4,
                                        Objectives=[],
                                        )
    DocIsInStruct =unrealsdk.make_struct("MissionStatus",
                                        MissionDef=DocIsIn,
                                        Status=4,
                                        Objectives=[],
                                        )

    PT3ResetData = unrealsdk.make_struct("MissionPlaythroughInfo",
                                        MissionList=[IntroStruct, DocIsInStruct],
                                        UnloadableDlcMissionList=[],
                                        ActiveMission=SkagsAtGate,
                                        PlayThroughNumber=2)


    if len(PC.MissionPlaythroughData) < 3:
        PC.AddPlaythrough(3)
    unrealsdk.find_all("MissionTracker")[1].MissionList.clear()
    PC.MissionPlaythroughData[2] = PT3ResetData
    KillSkags = unrealsdk.find_object("MissionDefinition","Z0_Missions.Missions.M_KillSkags_Zed")
    PC.AddMissionToTrack(KillSkags)
    PC.SetMissionStatus(PC.GetMissionIndexForMission(KillSkags), 1)
    PC.EchoPlaythroughData[2].echolist.clear()
    unrealsdk.find_all("EchoTracker")[1].EchoCallList.clear()

    print("Reset ran!")

@hook(
    hook_func="WillowGame.WillowGFxMoviePressStart:extContinue",
    hook_type=Type.POST,
)
def PressStart(obj: UObject, args: WrappedStruct, ret: any, func: BoundFunction):
    global bPrepWorkDone

    global GlobalsDef
    global GlobalGameStage
    global GlobalGameStageSetting

    if bPrepWorkDone is False:
        bPrepWorkDone = True

        unrealsdk.load_package("gd_Balance_Enemies_Humans")
        unrealsdk.load_package("gd_Balance_HealthAndDamage")
        unrealsdk.load_package("gd_GameStages_PT3")

        unrealsdk.load_package("gd_Balance_Enemies_Humans.Bandits.Common.Pawn_Balance_Grunt_00_Intro")
        unrealsdk.load_package("gd_Balance_Enemies_Humans.Bandits.Common.Pawn_Balance_Elite_00_Intro")
        unrealsdk.load_package("gd_Balance_HealthAndDamage.HealthMultipliers.Enemy_Health_ByPlaythrough")
        unrealsdk.load_package("gd_Balance_HealthAndDamage.DamageMultipliers.Enemy_Damage_ByPlaythrough")
        unrealsdk.load_package("gd_Balance_HealthAndDamage.HealthMultipliers.Guardian_Shield_ByPlaythrough")

        unrealsdk.load_package("gd_GameStages_PT3.Attribute.GlobalGameStage")
        unrealsdk.load_package("gd_GameStages_PT3.Balance.Balance_P1_Arid")
        unrealsdk.load_package("gd_GameStages_PT3.Balance.Balance_P1_Headlands")
        unrealsdk.load_package("gd_GameStages_PT3.Balance.Balance_P1_Scrap")
        unrealsdk.load_package("gd_GameStages_PT3.Balance.Balance_P1_Thor")
        unrealsdk.load_package("gd_GameStages_PT3.DLC1.Balance.Balance_P1_DLC1")
        unrealsdk.load_package("gd_GameStages_PT3.DLC2.Balance.Balance_P1_DLC2")
        unrealsdk.load_package("gd_GameStages_PT3.DLC3.Balance.Balance_P1_DLC3")
        unrealsdk.load_package("gd_GameStages_PT3.DLC4.Balance.Balance_P1_DLC4")

        unrealsdk.load_package("gd_globals.General.Globals")
        unrealsdk.load_package("dlc1_PackageDefinition.CustomGlobals")
        unrealsdk.load_package("dlc2_packagedefinition.CustomGlobals")
        unrealsdk.load_package("dlc3_PackageDefinition.CustomGlobals")
        unrealsdk.load_package("dlc4_PackageDefinition.CustomGlobals")

        unrealsdk.load_package("gd_RegistrationStationList.Lookups.RegistrationStationLookup")
        unrealsdk.load_package("Z0_Missions.Missions.M_BuyGrenades")
        unrealsdk.load_package("Z0_Missions.Missions.M_JumpTheGap")

        unrealsdk.load_package("dlc1_gd_Balance_Enemies")
        unrealsdk.load_package("dlc2_gd_Balance_Enemies_Humans")
        unrealsdk.load_package("dlc2_gd_Balance_Creatures")
#        unrealsdk.load_package("dlc4_gd_Balance_Enemies")

        unrealsdk.load_package("Z0_Missions.Missions.M_JumpTheGap")
        unrealsdk.load_package("Z0_Missions.Missions.M_JumpTheGap")

        FastTravelList = find_object("EmergencyTeleportOutpostLookup","gd_RegistrationStationList.Lookups.RegistrationStationLookup")
        FastTravelList.ObjectFlags |= 0x4000

        GlobalsDef = find_object("GlobalsDefinition","gd_globals.General.Globals")
        GlobalsDef.ObjectFlags |= 0x4000

        DLC1Globals = find_object("GlobalsDefinition","dlc1_PackageDefinition.CustomGlobals")
        DLC1Globals.ObjectFlags |= 0x4000

        DLC2Globals = find_object("GlobalsDefinition","dlc2_packagedefinition.CustomGlobals")
        DLC2Globals.ObjectFlags |= 0x4000

        DLC3Globals = find_object("GlobalsDefinition","dlc3_PackageDefinition.CustomGlobals")
        DLC3Globals.ObjectFlags |= 0x4000

        DLC4Globals = find_object("GlobalsDefinition","dlc4_PackageDefinition.CustomGlobals")
        DLC4Globals.ObjectFlags |= 0x4000

        GlobalGameStage = find_object("AttributeDefinition","gd_GameStages_PT3.Attribute.GlobalGameStage")
        GlobalGameStage.ObjectFlags |= 0x4000
        GlobalGameStageSetting = GameStage.value

        EnemyHealth = find_object("AttributeInitializationDefinition","gd_Balance_HealthAndDamage.HealthMultipliers.Enemy_Health_ByPlaythrough")
        EnemyHealth.ConditionalInitialization.ConditionalExpressionList.append(EnemyHealth.ConditionalInitialization.ConditionalExpressionList[1])
        EnemyHealth.ConditionalInitialization.ConditionalExpressionList[2].Expressions[0].ConstantOperand2 = 3

        EnemyDamage = find_object("AttributeInitializationDefinition","gd_Balance_HealthAndDamage.DamageMultipliers.Enemy_Damage_ByPlaythrough")
        EnemyDamage.ConditionalInitialization.ConditionalExpressionList.append(EnemyDamage.ConditionalInitialization.ConditionalExpressionList[1])
        EnemyDamage.ConditionalInitialization.ConditionalExpressionList[2].Expressions[0].ConstantOperand2 = 3

        GuardianShield = find_object("AttributeInitializationDefinition","gd_Balance_HealthAndDamage.HealthMultipliers.Guardian_Shield_ByPlaythrough")
        GuardianShield.ConditionalInitialization.ConditionalExpressionList.append(GuardianShield.ConditionalInitialization.ConditionalExpressionList[1])
        GuardianShield.ConditionalInitialization.ConditionalExpressionList[2].Expressions[0].ConstantOperand2 = 3

        BaseGameBalanceStruct = unrealsdk.make_struct("PlayThroughData",PlayThroughNumber=3)
        BaseGameBalanceStruct.BalanceDefinitions.append(find_object("GameBalanceDefinition","gd_gamestages_vs.Balance.Balance_Arena"))
        BaseGameBalanceStruct.BalanceDefinitions.append(find_object("GameBalanceDefinition","gd_GameStages_PT3.Balance.Balance_P1_Arid"))
        BaseGameBalanceStruct.BalanceDefinitions.append(find_object("GameBalanceDefinition","gd_GameStages_PT3.Balance.Balance_P1_Headlands"))
        BaseGameBalanceStruct.BalanceDefinitions.append(find_object("GameBalanceDefinition","gd_GameStages_PT3.Balance.Balance_P1_Scrap"))
        BaseGameBalanceStruct.BalanceDefinitions.append(find_object("GameBalanceDefinition","gd_GameStages_PT3.Balance.Balance_P1_Thor"))
        GlobalsDef.RegionBalanceData.append(BaseGameBalanceStruct)
        GlobalsDef.MaxAllowedPlayThroughs = 3

        DLC1BalanceStruct = unrealsdk.make_struct("PlayThroughData",PlayThroughNumber=3)
        DLC1BalanceStruct.BalanceDefinitions.append(find_object("GameBalanceDefinition","gd_GameStages_PT3.DLC1.Balance.Balance_P1_DLC1"))
        DLC1Globals.RegionBalanceData.append(DLC1BalanceStruct)

        DLC2BalanceStruct = unrealsdk.make_struct("PlayThroughData",PlayThroughNumber=3)
        DLC2BalanceStruct.BalanceDefinitions.append(find_object("GameBalanceDefinition","gd_GameStages_PT3.DLC2.Balance.Balance_P1_DLC2"))
        DLC2Globals.RegionBalanceData.append(DLC2BalanceStruct)

        DLC3BalanceStruct = unrealsdk.make_struct("PlayThroughData",PlayThroughNumber=3)
        DLC3BalanceStruct.BalanceDefinitions.append(find_object("GameBalanceDefinition","gd_GameStages_PT3.DLC3.Balance.Balance_P1_DLC3"))
        DLC3Globals.RegionBalanceData.append(DLC3BalanceStruct)

        DLC4BalanceStruct = unrealsdk.make_struct("PlayThroughData",PlayThroughNumber=3)
        DLC4BalanceStruct.BalanceDefinitions.append(find_object("GameBalanceDefinition","gd_GameStages_PT3.DLC4.Balance.Balance_P1_DLC4"))
        DLC4Globals.RegionBalanceData.append(DLC4BalanceStruct)

        Grunts =find_object("AIPawnBalanceDefinition","gd_Balance_Enemies_Humans.Bandits.Common.Pawn_Balance_Grunt_00_Intro")
        Grunts.ObjectFlags |= 0x4000
        Grunts.Grades[2].GameStageRequirement.MaxGameStage = 100
        Elites = find_object("AIPawnBalanceDefinition","gd_Balance_Enemies_Humans.Bandits.Common.Pawn_Balance_Elite_00_Intro")
        Elites.ObjectFlags |= 0x4000
        Elites.Grades[2].GameStageRequirement.MaxGameStage = 100
        
        FastTravelList.OutpostLookupList[3].MissionDependencies[0].MissionDefinition = find_object("MissionDefinition","Z0_Missions.Missions.M_BuyGrenades")
        FastTravelList.OutpostLookupList[26].MissionDependencies[0].MissionDefinition = find_object("MissionDefinition","Z0_Missions.Missions.M_JumpTheGap")

        #Ammo drop fixes
        unrealsdk.load_package("gd_ammodrops.AmmoPickup_Amounts.AmmoAmount_CombatRifle")
        unrealsdk.load_package("gd_ammodrops.AmmoPickup_Amounts.AmmoAmount_Grenades")
        unrealsdk.load_package("gd_ammodrops.AmmoPickup_Amounts.AmmoAmount_Launcher")
        unrealsdk.load_package("gd_ammodrops.AmmoPickup_Amounts.AmmoAmount_Repeater")
        unrealsdk.load_package("gd_ammodrops.AmmoPickup_Amounts.AmmoAmount_Revolver")
        unrealsdk.load_package("gd_ammodrops.AmmoPickup_Amounts.AmmoAmount_Shotgun")
        unrealsdk.load_package("gd_ammodrops.AmmoPickup_Amounts.AmmoAmount_SMG")
        unrealsdk.load_package("gd_ammodrops.AmmoPickup_Amounts.AmmoAmount_SniperRifle")

        CombatRifle_Ammo = unrealsdk.find_object("InventoryAttributeDefinition","gd_ammodrops.AmmoPickup_Amounts.AmmoAmount_CombatRifle")
        Grenade_Ammo = unrealsdk.find_object("InventoryAttributeDefinition","gd_ammodrops.AmmoPickup_Amounts.AmmoAmount_Grenades")
        Launcher_Ammo = unrealsdk.find_object("InventoryAttributeDefinition","gd_ammodrops.AmmoPickup_Amounts.AmmoAmount_Launcher")
        Repeater_Ammo = unrealsdk.find_object("InventoryAttributeDefinition","gd_ammodrops.AmmoPickup_Amounts.AmmoAmount_Repeater")
        Revolver_Ammo = unrealsdk.find_object("InventoryAttributeDefinition","gd_ammodrops.AmmoPickup_Amounts.AmmoAmount_Revolver")
        Shotgun_Ammo = unrealsdk.find_object("InventoryAttributeDefinition","gd_ammodrops.AmmoPickup_Amounts.AmmoAmount_Shotgun")
        SMG_Ammo = unrealsdk.find_object("InventoryAttributeDefinition","gd_ammodrops.AmmoPickup_Amounts.AmmoAmount_SMG")
        SniperRifle_Ammo = unrealsdk.find_object("InventoryAttributeDefinition","gd_ammodrops.AmmoPickup_Amounts.AmmoAmount_SniperRifle")


        CombatRifle_Ammo.ObjectFlags |= 0x4000
        Grenade_Ammo.ObjectFlags |= 0x4000
        Launcher_Ammo.ObjectFlags |= 0x4000
        Repeater_Ammo.ObjectFlags |= 0x4000
        Revolver_Ammo.ObjectFlags |= 0x4000
        Shotgun_Ammo.ObjectFlags |= 0x4000
        SMG_Ammo.ObjectFlags |= 0x4000
        SniperRifle_Ammo.ObjectFlags |= 0x4000

        CombatRifle_Ammo.ValueResolverChain[0].ValueExpressions.DefaultBaseValue.BaseValueConstant = 36
        CombatRifle_Ammo.ValueResolverChain[0].ValueExpressions.ConditionalExpressionList[0].BaseValueIfTrue.BaseValueConstant = 18
        CombatRifle_Ammo.ValueResolverChain[0].ValueExpressions.ConditionalExpressionList[0].Expressions[0].ConstantOperand2 = 1

        Grenade_Ammo.ValueResolverChain[0].ValueExpressions.DefaultBaseValue.BaseValueConstant = 1
        Grenade_Ammo.ValueResolverChain[0].ValueExpressions.ConditionalExpressionList[0].BaseValueIfTrue.BaseValueConstant = 1
        Grenade_Ammo.ValueResolverChain[0].ValueExpressions.ConditionalExpressionList[0].Expressions[0].ConstantOperand2 = 1

        Launcher_Ammo.ValueResolverChain[0].ValueExpressions.DefaultBaseValue.BaseValueConstant = 8
        Launcher_Ammo.ValueResolverChain[0].ValueExpressions.ConditionalExpressionList[0].BaseValueIfTrue.BaseValueConstant = 4
        Launcher_Ammo.ValueResolverChain[0].ValueExpressions.ConditionalExpressionList[0].Expressions[0].ConstantOperand2 = 1

        Repeater_Ammo.ValueResolverChain[0].ValueExpressions.DefaultBaseValue.BaseValueConstant = 36
        Repeater_Ammo.ValueResolverChain[0].ValueExpressions.ConditionalExpressionList[0].BaseValueIfTrue.BaseValueConstant = 18
        Repeater_Ammo.ValueResolverChain[0].ValueExpressions.ConditionalExpressionList[0].Expressions[0].ConstantOperand2 = 1

        Revolver_Ammo.ValueResolverChain[0].ValueExpressions.DefaultBaseValue.BaseValueConstant = 12
        Revolver_Ammo.ValueResolverChain[0].ValueExpressions.ConditionalExpressionList[0].BaseValueIfTrue.BaseValueConstant = 6
        Revolver_Ammo.ValueResolverChain[0].ValueExpressions.ConditionalExpressionList[0].Expressions[0].ConstantOperand2 = 1

        Shotgun_Ammo.ValueResolverChain[0].ValueExpressions.DefaultBaseValue.BaseValueConstant = 16
        Shotgun_Ammo.ValueResolverChain[0].ValueExpressions.ConditionalExpressionList[0].BaseValueIfTrue.BaseValueConstant = 8
        Shotgun_Ammo.ValueResolverChain[0].ValueExpressions.ConditionalExpressionList[0].Expressions[0].ConstantOperand2 = 1

        SMG_Ammo.ValueResolverChain[0].ValueExpressions.DefaultBaseValue.BaseValueConstant = 48
        SMG_Ammo.ValueResolverChain[0].ValueExpressions.ConditionalExpressionList[0].BaseValueIfTrue.BaseValueConstant = 24
        SMG_Ammo.ValueResolverChain[0].ValueExpressions.ConditionalExpressionList[0].Expressions[0].ConstantOperand2 = 1

        SniperRifle_Ammo.ValueResolverChain[0].ValueExpressions.DefaultBaseValue.BaseValueConstant = 12
        SniperRifle_Ammo.ValueResolverChain[0].ValueExpressions.ConditionalExpressionList[0].BaseValueIfTrue.BaseValueConstant = 6
        SniperRifle_Ammo.ValueResolverChain[0].ValueExpressions.ConditionalExpressionList[0].Expressions[0].ConstantOperand2 = 1

        PatchDLCEnemySpawn()

        get_pc().WorldInfo.ForceGarbageCollection()

from .DLCEnemyGroups import DLCEnemyDefinitionsList
def PatchDLCEnemySpawn():
    def PatchGroup(AIPawnBalance : UObject):
        AIPawnBalance.Grades[0].GameStageRequirement.MinGameStage = 1
        AIPawnBalance.ObjectFlags |= 0x4000

    for GroupName in DLCEnemyDefinitionsList:
        PatchGroup(unrealsdk.find_object("AIPawnBalanceDefinition",GroupName))
    return

def BuildResetMenu():
    global ResetMissions, ResetLevel, ResetInventory, ResetWeaponProficiency, ResetAmmoSDU

    LastSelectedOptionName = None
    ConfirmTip = "Are you sure you want to reset this character data?"
    OptionsTip = f"""Current settings:
Reset Missions - {ResetMissions}
Reset Level - {ResetLevel}
Reset Inventory - {ResetInventory}
Reset Weapon Proficiency - {ResetWeaponProficiency}
Reset Ammo & Grenade Upgrades - {ResetAmmoSDU}"""

    Buttons = [
        OptionBoxButton("Reset",ConfirmTip),
        OptionBoxButton("Customize reset options",OptionsTip),
        OptionBoxButton("Cancel","")
        ]
    Dlg = OptionBox(title="Reset Confirmation", message="Confirm reset or customize what to reset.", buttons=Buttons, on_select=HandleResetMenu, on_cancel=lambda _:None)
    Dlg.show()
    return

def BuildResetOptionsMenu(LastButton: OptionBoxButton = None):
    global ResetMissions, ResetLevel, ResetInventory, ResetWeaponProficiency, ResetAmmoSDU

    OptionsTip = f"""Current settings:
Reset Missions - {ResetMissions}
Reset Level - {ResetLevel}
Reset Inventory - {ResetInventory}
Reset Weapon Proficiency - {ResetWeaponProficiency}
Reset Ammo & Grenade Upgrades - {ResetAmmoSDU}"""

    Buttons = [
        OptionBoxButton("Reset mission data", ""),
        OptionBoxButton("Reset character level", ""),
        OptionBoxButton("Reset inventory", ""),
        OptionBoxButton("Reset weapon proficiency", ""),
        OptionBoxButton("Reset ammo and grenade upgrades", ""),
        OptionBoxButton("Done","")
        ]
    Dlg = OptionBox(title="Choose what to reset", message=OptionsTip, buttons=Buttons, on_select=HandleResetOptionsMenu, on_cancel=lambda _:BuildResetMenu())
    Dlg.show(LastButton)
    return

def HandleResetMenu(Dialogue: OptionBox, ChosenBtn: OptionBoxButton):
    global ResetRequested, ResetLevel, GlobalsDef, SkagsAtGate, GlobalGameStage, GlobalGameStageSetting
    if ChosenBtn.name == "Reset":
        ResetRequested = True
        PlayerLevel = (get_pc().GetWillowGlobals().GetWillowSaveGameManager().GetCachedPlayerProfile(WillowGFxLobbySinglePlayer.GetControllerId()).ExpLevel) if not ResetLevel else 1
        GlobalGameStage.ValueResolverChain[0].ConstantValue = max(PlayerLevel + GlobalGameStageSetting, 1)
        add_hook("WillowGame.WillowPlayerController:TeleportPlayerToHoldingCell", Type.POST, "ResetLoad", ResetPT3)
        GlobalsDef.FastTravelMission = SkagsAtGate
        WillowGFxLobbySinglePlayer.LaunchSaveGame(2)
    elif ChosenBtn.name == "Customize reset options":
        BuildResetOptionsMenu()
    return

def HandleResetOptionsMenu(Dialogue: OptionBox, ChosenBtn: OptionBoxButton):
    global ResetMissions, ResetLevel, ResetInventory, ResetWeaponProficiency, ResetAmmoSDU
    if ChosenBtn.name == "Reset mission data":
        ResetMissions = not ResetMissions
        BuildResetOptionsMenu(ChosenBtn)
    elif ChosenBtn.name == "Reset character level":
        ResetLevel = not ResetLevel
        BuildResetOptionsMenu(ChosenBtn)
    elif ChosenBtn.name == "Reset inventory":
        ResetInventory = not ResetInventory
        BuildResetOptionsMenu(ChosenBtn)
    elif ChosenBtn.name == "Reset weapon proficiency":
        ResetWeaponProficiency = not ResetWeaponProficiency
        BuildResetOptionsMenu(ChosenBtn)
    elif ChosenBtn.name == "Reset ammo and grenade upgrades":
        ResetAmmoSDU = not ResetAmmoSDU
        BuildResetOptionsMenu(ChosenBtn)
    elif ChosenBtn.name == "Done":
        BuildResetMenu()
    return

def SetGlobalGameStage(_: SliderOption, new_value: float):
    global GlobalGameStage, GlobalGameStageSetting
    if get_pc().Pawn:
        PlayerLevel = get_pc().Pawn.GetExpLevel()
        GlobalGameStage.ValueResolverChain[0].ConstantValue = max(PlayerLevel + new_value,1)
    GlobalGameStageSetting = new_value
    return

@hook(
    hook_func="WillowGame.WillowGFxLobbySinglePlayer:FinishLoadGame",
    hook_type=Type.PRE,
)
def FinishLoadGame(obj: UObject, args: WrappedStruct, ret: any, func: BoundFunction):
    global bGlobalPT3Unlocked, bCreatingPT3Character
    global WillowGFxLobbySinglePlayer
    global ResetRequested
    WillowGFxLobbySinglePlayer = obj
    Profile = None
    Dlg = None
    ResetRequested = False

    Profile = get_pc().GetWillowGlobals().GetWillowSaveGameManager().GetCachedPlayerProfile(obj.GetControllerId())

###    
    if Profile != None and bCreatingPT3Character:
        bCreatingPT3Character = False
        PlayerLevel = 1
        GlobalGameStage.ValueResolverChain[0].ConstantValue = max(1 + GlobalGameStageSetting,1)
        Profile.PlaythroughsCompleted = 2
        Profile.PlotMissionNumber = 1
        Profile.LastVisitedTeleporter = "Fyrestone"
        Profile.InventorySlotData.InventorySlotMax_Misc=72
#        Profile.PlayerClassDefinition
        add_hook("WillowGame.WillowPlayerController:ClientSetProfileLoaded", Type.POST, "FirstLoad", FirstLoadPT3)
        GlobalsDef.FastTravelMission = SkagsAtGate
        get_pc().GetWillowGlobals().GetWillowSaveGameManager().SetCachedPlayerProfile(obj.GetControllerId(),Profile)

        WillowGFxLobbySinglePlayer.LaunchSaveGame(2)
        return Block
###
        
    if Profile != None and Profile.SaveGameId != -1:
        if Profile.PlaythroughsCompleted == 1:
            Dlg = obj.GetWillowOwner().GFxUIManager.ShowDialog()
            Dlg.AutoLocEnable("WillowMenu", "dlgDifficultySelect")

            Dlg.AppendButton('Dif2', 'Playthrough 2', "", obj.OnChooseDifficulty_Click)
            Dlg.AppendButton('Dif1', 'Playthrough 1', "", obj.OnChooseDifficulty_Click)
            Dlg.AutoAppendButton('Cancel')
            Dlg.ApplyLayout()
            Dlg.SetDefaultButton('Dif2', False)

        elif Profile.PlaythroughsCompleted > 1 and Profile.TotalPlayTime > 0:
            Dlg = obj.GetWillowOwner().GFxUIManager.ShowDialog()
            Dlg.AutoLocEnable("WillowMenu", "dlgDifficultySelect")

            Dlg.AppendButton('Dif3', 'Playthrough 3', "(Press R to Reset)", Dlg.OnButtonClicked)
            Dlg.AppendButton('Dif2', 'Playthrough 2', "", obj.OnChooseDifficulty_Click)
            Dlg.AppendButton('Dif1', 'Playthrough 1', "", obj.OnChooseDifficulty_Click)

            Dlg.AutoAppendButton('Cancel')
            Dlg.ApplyLayout()
            Dlg.SetDefaultButton('Dif2', False)
            if not bGlobalPT3Unlocked:
                Path(SETTINGS_DIR / "PT3GlobalUnlocker").touch() # Unlocks option to create New PT3 Characters
                bGlobalPT3Unlocked = True  
        else:
            obj.LaunchSaveGame(Profile.PlaythroughsCompleted)

    else:
        obj.LaunchNewGame()
    return Block


@hook(
    hook_func="WillowGame.WillowPlayerController:OnExpLevelChange",
    hook_type=Type.POST,
)
def OnExpLevelChange(obj: UObject, args: WrappedStruct, ret: any, func: BoundFunction):
    if obj.WorldInfo.NetMode == 3:
        return
    global GlobalGameStage, GlobalGameStageSetting
    BodyInterface = obj.Pawn.QueryInterface(unrealsdk.find_class('IBodyPawn'))
    if BodyInterface:
        WPawn = BodyInterface.GetAWillowPawn()

    if obj.GetCurrentPlaythrough() == 2 and WPawn:
        GlobalGameStage.ValueResolverChain[0].ConstantValue = max(WPawn.GetExpLevel() + GlobalGameStageSetting,1)

@hook(
    hook_func="WillowGame.WillowGFxDialogBox:OnButtonClicked",
    hook_type=Type.POST,
)
def OnButtonClicked(obj: UObject, args: WrappedStruct, ret: any, func: BoundFunction):
    global WillowGFxLobbySinglePlayer, GlobalsDef, SkagsAtGate, GlobalGameStage, GlobalGameStageSetting
    
    if obj.DialogResult == 'Dif3':
        PlayerLevel = get_pc().GetWillowGlobals().GetWillowSaveGameManager().GetCachedPlayerProfile(obj.GetControllerId()).ExpLevel
        GlobalGameStage.ValueResolverChain[0].ConstantValue = max(PlayerLevel + GlobalGameStageSetting,1)
        add_hook("WillowGame.WillowPlayerController:ClientSetProfileLoaded", Type.POST, "FirstLoad", FirstLoadPT3)
        GlobalsDef.FastTravelMission = SkagsAtGate
        WillowGFxLobbySinglePlayer.LaunchSaveGame(2)

    elif obj.DialogResult == 'Dif1' or obj.DialogResult == 'Dif2':
        unrealsdk.load_package('I1_Missions.Missions.M_Powerlines')
        GlobalsDef.FastTravelMission = unrealsdk.find_object('MissionDefinition','I1_Missions.Missions.M_Powerlines')
    return

@hook(
    hook_func="WillowGame.WillowGFxDialogBox:HandleInputKey",
    hook_type=Type.PRE,
)
def HandleInputKey(obj: UObject, args: WrappedStruct, ret: any, func: BoundFunction):
    if args.ukey == "R" and obj.Buttons and obj.Buttons[0].Tag == 'Dif3':
        if obj.CurrentSelection == 0:
            BuildResetMenu()


def ResetPT3(
    obj: UObject,
    __args: WrappedStruct,
    __ret: any,
    __func: BoundFunction,
) -> None:
    global ResetRequested, ResetLevel, ResetMissions, ResetInventory, ResetAmmoSDU, ResetWeaponProficiency, BadlandsLoaded

    if not ResetRequested:
        return

    PC = get_pc()

    if ResetAmmoSDU is True:
        for i in range(len(PC.AmmoResourceUpgrades)):
            logging.info(f"{PC.AmmoResourceUpgrades[i]}")
        ResetAmmoSDU = False

    if ResetWeaponProficiency is True:
       #PlayerSkills stores data used by the game, ProficiencySkills stores the UI data
        for skill in PC.ProficiencySkills:
            PC.PlayerSkills[skill.PlayerSkillIndex].PointsToNextGrade = skill.PointsToNextGrade = 2400
            PC.PlayerSkills[skill.PlayerSkillIndex].GradePoints = skill.GradePoints = 0
            PC.PlayerSkills[skill.PlayerSkillIndex].Grade = skill.Grade=0
        ResetWeaponProficiency = False
           
    if ResetLevel is True:
#       PC.GetInventoryPawn().InvManager.SetWeaponReadyMax(2)  # is it possible to get all slots back in PT3?
        PC.ResetAndChangeExpLevel(1)
        ResetLevel = False

    if ResetInventory is True:
        PC.PlayerReplicationInfo.SetCurrencyOnHand(67)
        PC.GetInventoryPawn().InvManager.DiscardInventory(True)
#        PC.GetInventoryPawn().InvManager.Stash_Reset()
        ResetInventory = False

    if ResetMissions is True and BadlandsLoaded is True:    
        ResetMissions = False
        BadlandsLoaded = False
        ResetPlaythrough3(PC)
        PC.ServerTeleportPlayerToOutpost("Fyrestone")
        return

    if ResetMissions is True and BadlandsLoaded is False:
        if not PC.WorldInfo.GetMapName() == "Arid_Arena_Coliseum_P":
            PC.ServerTeleportPlayerToOutpost("PitArena")
        else:
            PC.ServerTeleportPlayerToOutpost("RuinsArena")
        BadlandsLoaded = True
        return
    
    ResetMissions = True    
    ResetRequested = False
    remove_hook("WillowGame.WillowPlayerController:TeleportPlayerToHoldingCell", Type.POST, "ResetLoad")
    

def FirstLoadPT3(
    obj: UObject,
    __args: WrappedStruct,
    __ret: any,
    __func: BoundFunction,
) -> None:
    global ResetRequested
    PC = get_pc()
    if ResetRequested is False and PC.IsMissionInStatus(unrealsdk.find_object("MissionDefinition","Z0_Missions.Missions.M_IntroStateSaver"), 4) is False:
        ResetPlaythrough3(PC)
        PC.ServerTeleportPlayerToOutpost("Fyrestone")
    remove_hook("WillowGame.WillowPlayerController:ClientSetProfileLoaded", Type.POST, "FirstLoad")

###
@hook(
    hook_func="WillowGame.WillowGFxLobbyLoadCharacter:extCharacterSelected",
    hook_type=Type.PRE,
)
def CharacterSelected(obj: UObject, args: WrappedStruct, ret: any, func):
    global bGlobalPT3Unlocked, bCreatingPT3Character, PT3CharacterClass
    
    if not bGlobalPT3Unlocked:
        return None    

    if args.charIdx >= 100:
        try:
            classID = args.charIdx - 100            
            bCreatingPT3Character = True
            WPC = obj.GetWillowOwner()
            WillowSaveGameManager = WPC.GetWillowGlobals().GetWillowSaveGameManager()
            default_profiles = ["default roland","default mordecai", "default lilith","default brick"]
            logging.info(f"Default profile picked - {default_profiles[classID]}, ID {classID}")
            WPC.ProfileLoad(default_profiles[classID], True)
            char_data = unrealsdk.make_struct("PlayerSaveData",CharacterClass=classID,ExpLevel=1,CharacterName=default_profiles[classID])
            li = unrealsdk.make_struct("LoadInfo", LoadSucceeded=True, CharacterData = char_data)                                        
            obj.FinishLoadGame(li)          
            return Block
            
        except Exception as e:
            logging.error(f"Error creating PT3 character: {e}")
            bCreatingPT3Character = False
    
    return None


@hook(
    hook_func="WillowGame.WillowGFxLobbyLoadCharacter:SetupNewCharacterMenu",
    hook_type=Type.POST,
)
def SetupNewCharacterMenu(obj: UObject, args: WrappedStruct, ret: any, func: BoundFunction):
    global bGlobalPT3Unlocked
    obj.menuAddItem(args.menuDepth, "$WillowMenu.FESelChar.NewChar PT3", "newChar", "extNewCharacter", "Focus:extFocusItem")
    if bGlobalPT3Unlocked:
        WillowGFxMenuHelperSaveGame = unrealsdk.find_class("WillowGFxMenuHelperSaveGame")
        if WillowGFxMenuHelperSaveGame:
            for classID in range(4):
                className = WillowGFxMenuHelperSaveGame.ClassDefaultObject.GetCharName(classID, True, "")
                obj.menuAddCharacterItem(
                    args.menuDepth,
                    100 + classID,
                    1,
                    className,
                    "New Character PT3",
                    "extCharacterSelected",
                    "Focus:extFocusItem"
                )
###

__version__: str
__version_info__: tuple[int, ...]

build_mod(
    hooks=[OnButtonClicked, FinishLoadGame, HandleInputKey, OnExpLevelChange, PressStart, SetupNewCharacterMenu,CharacterSelected],
    options=[GameStage],
    settings_file=Path(f"{SETTINGS_DIR}/PT3.json"),
)

logging.info(f"Playthrough 3 Loaded: {__version__}, {__version_info__}")
if bGlobalPT3Unlocked:
   logging.info(f"Playthrough 3 Unlocker File Detected!")
