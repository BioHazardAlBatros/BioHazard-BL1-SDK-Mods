import unrealsdk#type: ignore
from unrealsdk import logging, find_all, load_package,make_struct,find_object,construct_object, find_class #type: ignore
from unrealsdk.hooks import Type, add_hook, remove_hook, Block, log_all_calls,prevent_hooking_direct_calls #type: ignore
from unrealsdk.unreal import UObject, WrappedStruct, BoundFunction, UScriptStruct#type: ignore
from mods_base import get_pc,hook,ENGINE,EInputEvent,keybind,SETTINGS_DIR, MODS_DIR,build_mod,keybind, BaseOption, BoolOption, SliderOption#type: ignore
from typing import Any

oidShopCooldown = SliderOption(
    "Shop Reset in Minutes",
    20,
    5,
    20,
    1,
    True,
    description="Choose how fast you want to reset the shops.\nDefault Value: 20",
    on_change = lambda _, 
    new_value: UpdateShops(_, new_value)
)

oidGamepadIcons = BoolOption(
    "Use Xbox 360 Buttons",
    False,
    "On",
    "Off",
    description="With this enabled, game will use gamepad icons.",
    on_change = lambda _,
    new_value: UpdateIcons(_, new_value)
)

oidTimeCycle = SliderOption(
    "DayNight Cycle Multiplier",
    1.0,
    1.0,
    100.0,
    2.0,
    True,
    description="Choose how fast you want to see day cycle.\nDefault Value: 1.0",
    on_change = lambda _, 
    new_value: UpdateTimeCycle(_, new_value)
)

bPrepWorkDone = False
Globals = None
DLC1Globals = None
DLC2Globals = None
DLC3Globals = None
DLC4Globals = None

def keep_alive(in_object:UObject):
    in_object.ObjectFlags |= 0x4000

def PressStart() -> None:
    global bPrepWorkDone

    global Globals
    global DLC1Globals
    global DLC2Globals
    global DLC3Globals
    global DLC4Globals

    if bPrepWorkDone is False:
        bPrepWorkDone = True

        load_package("gd_globals.General.Globals")
        load_package("dlc1_PackageDefinition.CustomGlobals")
        load_package("dlc2_packagedefinition.CustomGlobals")
        load_package("dlc3_PackageDefinition.CustomGlobals")
        load_package("dlc4_PackageDefinition.CustomGlobals")
        
        createBankSDU()
        Globals = find_object("GlobalsDefinition","gd_globals.General.Globals")
        keep_alive(Globals)
        DLC1Globals = find_object("GlobalsDefinition","dlc1_PackageDefinition.CustomGlobals")
        keep_alive(DLC1Globals)
        DLC2Globals = find_object("GlobalsDefinition","dlc2_packagedefinition.CustomGlobals")
        keep_alive(DLC2Globals)
        DLC3Globals = find_object("GlobalsDefinition","dlc3_PackageDefinition.CustomGlobals")
        keep_alive(DLC3Globals)
        DLC4Globals = find_object("GlobalsDefinition","dlc4_PackageDefinition.CustomGlobals")
        keep_alive(DLC4Globals)

    UpdateShops(oidShopCooldown,oidShopCooldown.value)
    UpdateIcons(oidGamepadIcons,oidGamepadIcons.value)
    UpdateTimeCycle(oidTimeCycle,oidTimeCycle.value)

def createBankSDU() -> None:
    load_package("dlc2_gd_Bank")
    load_package("dlc2_gd_items")
    load_package("dlc2_gd_itempools")
    load_package("dlc2_gd_balance_shopping")
    load_package("gd_CommandDecks")

# Actually game stage in the game is always higher by 2, but it's level requirements are always lowered by this constant bonus
#    LevelBonus = find_object("AttributeDefinition","gd_Balance.LevelLimits.Proficiency_Gear_LevelBonus")
#    LevelBonus.ValueResolverChain[0].ConstantValue = 2

#    CommDecks = find_object("ItemPoolDefinition","gd_itempools.GeneralItemPools.Pool_ComDecks").BalancedItems
#    CommDeckTest = find_object("InventoryBalanceDefinition","gd_itemgrades.Gear.ItemGrade_Gear_ComDeck_Roland")
#    for playerClass in CommDecks:
#      keep_alive(playerClass.InvBalanceDefinition)
#      for Manufacturer in playerClass.InvBalanceDefinition.Manufacturers:
#        Manufacturer.Grades[5].GradeModifiers.ExpLevel=60
#        logging.info(f"{Manufacturer.Grades[5].GradeModifiers.ExpLevel}")

    Test2 = find_object("AttributeInitializationDefinition","gd_CommandDecks.Attributes.INI_SlotBaseGrade").ConditionalInitialization.ConditionalExpressionList
#    Test2.append(Test2[5])
#    Test2[5].Expressions[0].ConstantOperand2 = 61
# 11 -> 5 & 6
    Test2[5].BaseValueIfTrue.BaseValueConstant = 11
#    Test2[len(Test2)-1].BaseValueIfTrue.BaseValueConstant = 11

    MoxxiBank = find_object("Package","dlc2_gd_Bank.A_Item")
    keep_alive(MoxxiBank)
    MoxxiItems = find_object("Package","dlc2_gd_items.ItemGrades_BankUpgrades")
    keep_alive(MoxxiItems)
    MoxxiItempools = find_object("Package","dlc2_gd_itempools.ShopPools")
    keep_alive(MoxxiItempools)
    MoxxiShop = find_object("InteractiveObjectBalanceDefinition","dlc2_gd_balance_shopping.VendingMachineGrades.ObjectGrade_VendingMachine_Weapons")
    keep_alive(MoxxiShop)
    SDUTemplate = find_object("ItemDefinition","dlc2_gd_Bank.A_Item.INV_BankUpgrade_10")
    SDUTemplate.BaseCashValueModifier = 0
    
    NewSDU = construct_object("ItemDefinition",MoxxiBank,"INV_BankUpgrade_11",0x4000,SDUTemplate)
    NewBehavior = construct_object("Behavior_SetNumStashSlots",NewSDU,"Behavior_SetNumStashSlots_0",0x4000,SDUTemplate.Behaviors.OnUsed[0])
    AddedSlots = 256
    NewSDU.ItemName = "Bank Upgrade - Level 11"
    NewSDU.Behaviors.OnUsed[0] = NewBehavior
    NewSDU.Behaviors.OnUsed[0].NewStashSlotCount = AddedSlots
    NewSDU.OnUseConstraints[0].ConstantOperand2 = AddedSlots
    NewSDU.BaseCashValueModifier = 0
    NewSDU.CustomPresentations[0].Description = f"Purchase to increase your number of Bank Slots to {AddedSlots}."    

    ItemGradeTemplate = find_object("InventoryBalanceDefinition","dlc2_gd_items.ItemGrades_BankUpgrades.ItemGrade_BankUpgrade_10")
    NewItemGrade = construct_object("InventoryBalanceDefinition",MoxxiItems,"ItemGrade_BankUpgrade_11",0x4000,ItemGradeTemplate)
    NewItemGrade.InventoryDefinition = NewSDU

    ItemPoolTemplate = find_object("ItemPoolDefinition","dlc2_gd_itempools.ShopPools.shoppool_BankUpgrade_10")
    NewItemPool = construct_object("ItemPoolDefinition", MoxxiItempools,"shoppool_BankUpgrade_11",0x4000,ItemPoolTemplate)
    NewItemPool.BalancedItems[0].InvBalanceDefinition = NewItemGrade

    MoxxiShop.DefaultLoot[0].ItemAttachments.append(MoxxiShop.DefaultLoot[0].ItemAttachments[10])
    MoxxiShop.DefaultLoot[0].ItemAttachments[len(MoxxiShop.DefaultLoot[0].ItemAttachments)-1].ItemPool = NewItemPool

    NewSDU = construct_object("ItemDefinition",MoxxiBank,"INV_BankUpgrade_12",0x4000,SDUTemplate)
    NewBehavior = construct_object("Behavior_SetNumStashSlots",NewSDU,"Behavior_SetNumStashSlots_0",0x4000,SDUTemplate.Behaviors.OnUsed[0])
    AddedSlots = 1
    NewSDU.ItemName = "Bank Upgrade - Reduce to 1 slot"
    NewSDU.Behaviors.OnUsed[0] = NewBehavior
    NewSDU.Behaviors.OnUsed[0].NewStashSlotCount = AddedSlots
    NewSDU.OnUseConstraints[0].ConstantOperand2 = 43
    NewSDU.BaseCashValueModifier = 0
    NewSDU.CustomPresentations[0].Description = f"Purchase to decrease your number of Bank Slots to {AddedSlots}."    

    ItemGradeTemplate = find_object("InventoryBalanceDefinition","dlc2_gd_items.ItemGrades_BankUpgrades.ItemGrade_BankUpgrade_10")
    NewItemGrade = construct_object("InventoryBalanceDefinition",MoxxiItems,"ItemGrade_BankUpgrade_12",0x4000,ItemGradeTemplate)
    NewItemGrade.InventoryDefinition = NewSDU

    ItemPoolTemplate = find_object("ItemPoolDefinition","dlc2_gd_itempools.ShopPools.shoppool_BankUpgrade_10")
    NewItemPool = construct_object("ItemPoolDefinition", MoxxiItempools,"shoppool_BankUpgrade_12",0x4000,ItemPoolTemplate)
    NewItemPool.BalancedItems[0].InvBalanceDefinition = NewItemGrade

    MoxxiShop.DefaultLoot[0].ItemAttachments.append(MoxxiShop.DefaultLoot[0].ItemAttachments[10])
    MoxxiShop.DefaultLoot[0].ItemAttachments[len(MoxxiShop.DefaultLoot[0].ItemAttachments)-1].ItemPool = NewItemPool
    return

def UpdateShops(_: SliderOption,val: int) -> None:
    global bPrepWorkDone
    global Globals
    global DLC1Globals
    global DLC2Globals
    global DLC3Globals
    global DLC4Globals
    if bPrepWorkDone is True:
        for global_var in [Globals, DLC1Globals, DLC2Globals, DLC3Globals, DLC4Globals]:
          global_var.MinutesBetweenShopResets = val
    return

def UpdateIcons(_: BoolOption, value: bool) -> None:
    if bPrepWorkDone is True:
        for global_var in [Globals, DLC1Globals, DLC2Globals, DLC3Globals, DLC4Globals]:
          global_var.bUsePC360Buttons = value
    return

def UpdateTimeCycle(_: SliderOption,newTime: float) -> None:
    global bPrepWorkDone
    global Globals
    global DLC1Globals
    global DLC2Globals
    global DLC3Globals
    global DLC4Globals
    newTime = newTime / 10.0
    if bPrepWorkDone is True:
        for global_var in [Globals, DLC1Globals, DLC2Globals, DLC3Globals, DLC4Globals]:
          global_var.DayNightCycleRate = newTime
    return

@hook("WillowGame.Behavior_SetNumStashSlots:ApplyBehaviorToContext", Type.POST)
def BankUpgradeBypass(obj: UObject, __args: WrappedStruct, __ret: Any, __func: BoundFunction) -> None:
    player = __args.MyInstigatorObject.InvManager.StashSlots = obj.NewStashSlotCount
    return
   
#
#UWillowWeapon:execCreateWeaponFromMemento
#@hook("WillowGame.WillowWeapon.CreateWeaponFromMemento:CreateWeaponFromMemento", Type.POST)
#def Test(obj: UObject, __args: WrappedStruct, __ret: Any, __func: BoundFunction) -> None:
#    logging.info(f"Successfull hook to WillowGame.WillowWeapon.CreateWeaponFromMemento:CreateWeaponFromMemento")


__version__: str
__version_info__: tuple[int, ...]
    
build_mod(options=[oidShopCooldown,oidTimeCycle,oidGamepadIcons],on_enable=PressStart)