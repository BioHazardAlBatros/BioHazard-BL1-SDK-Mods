import unrealsdk
from unrealsdk import logging, find_all, load_package,make_struct
from unrealsdk.hooks import Type, add_hook, remove_hook, Block
from unrealsdk.unreal import UObject, WrappedStruct, BoundFunction, UScriptStruct, WeakPointer
from mods_base import Game, Mod, get_pc,hook,ENGINE,EInputEvent,build_mod,keybind, BaseOption, BoolOption, SliderOption
from typing import Any

prepWorkDone = False
Globals = None
DLC1Globals = None
DLC2Globals = None
DLC3Globals = None
DLC4Globals = None

commDeckValueConstant = 11
def buffCommdecks(_: BoolOption, value: bool) -> None:
    global commDeckValueConstant
    CommDeckAttribute = ENGINE.DynamicLoadObject("gd_CommandDecks.Attributes.INI_SlotBaseGrade",unrealsdk.find_class("AttributeInitializationDefinition"), False)
    CommDeckFormula = CommDeckAttribute.ConditionalInitialization.ConditionalExpressionList
    CommDeckFormula[5].BaseValueIfTrue.BaseValueConstant, commDeckValueConstant = commDeckValueConstant, CommDeckFormula[5].BaseValueIfTrue.BaseValueConstant

def createBankSDU() -> None:
    MoxxiBank = ENGINE.DynamicLoadObject("dlc2_gd_Bank.A_Item", unrealsdk.find_class("Package"), False)
    MoxxiItems = ENGINE.DynamicLoadObject("dlc2_gd_items.ItemGrades_BankUpgrades", unrealsdk.find_class("Package"), False)
    MoxxiItempools = ENGINE.DynamicLoadObject("dlc2_gd_itempools.ShopPools", unrealsdk.find_class("Package"), False)
    MoxxiShop = ENGINE.DynamicLoadObject("dlc2_gd_balance_shopping.VendingMachineGrades.ObjectGrade_VendingMachine_Weapons", unrealsdk.find_class("InteractiveObjectBalanceDefinition"), False)
    MoxxiShop.ObjectFlags |= 0x4000
    SDUTemplate = ENGINE.DynamicLoadObject("dlc2_gd_Bank.A_Item.INV_BankUpgrade_10",unrealsdk.find_class("ItemDefinition"), False)

    AddedSlots = 256    
    NewSDU = unrealsdk.construct_object("ItemDefinition",MoxxiBank,"INV_BankUpgrade_11",0x4000,SDUTemplate)
    NewBehavior = unrealsdk.construct_object("Behavior_SetNumStashSlots",NewSDU,"Behavior_SetNumStashSlots_0",0x4000,SDUTemplate.Behaviors.OnUsed[0])
    NewSDU.BaseCashValueModifier = SDUTemplate.BaseCashValueModifier + 1
    NewSDU.CustomPresentations[0].Description = f"Purchase to increase your number of Bank Slots to {AddedSlots}."
    NewSDU.ItemName = "Bank Upgrade - Level MAX"
    NewSDU.Behaviors.OnUsed[0] = NewBehavior
    NewSDU.Behaviors.OnUsed[0].NewStashSlotCount = AddedSlots
    NewSDU.OnUseConstraints[0].ConstantOperand2 = AddedSlots

    ItemGradeTemplate = unrealsdk.find_object("InventoryBalanceDefinition","dlc2_gd_items.ItemGrades_BankUpgrades.ItemGrade_BankUpgrade_10")
    NewItemGrade = unrealsdk.construct_object("InventoryBalanceDefinition",MoxxiItems,"ItemGrade_BankUpgrade_11",0x4000,ItemGradeTemplate)
    NewItemGrade.InventoryDefinition = NewSDU

    ItemPoolTemplate = unrealsdk.find_object("ItemPoolDefinition","dlc2_gd_itempools.ShopPools.shoppool_BankUpgrade_10")
    NewItemPool = unrealsdk.construct_object("ItemPoolDefinition", MoxxiItempools,"shoppool_BankUpgrade_11",0x4000,ItemPoolTemplate)
    NewItemPool.BalancedItems[0].InvBalanceDefinition = NewItemGrade

    MoxxiShop.DefaultLoot[0].ItemAttachments.append(MoxxiShop.DefaultLoot[0].ItemAttachments[10])
    MoxxiShop.DefaultLoot[0].ItemAttachments[-1].ItemPool = NewItemPool
    return

#Broken in Enhanced
def changeShopTimer(_: SliderOption,value: int) -> None:
    if prepWorkDone is True:
        for global_var in [Globals, DLC1Globals, DLC2Globals, DLC3Globals, DLC4Globals]:
          global_var.MinutesBetweenShopResets = value
    return

def allowIcons(_: BoolOption, value: bool) -> None:
    if prepWorkDone is True:
        for global_var in [Globals, DLC1Globals, DLC2Globals, DLC3Globals, DLC4Globals]:
          global_var.bUsePC360Buttons = value
    return

kamikazeChance = 1.0 
def patchKamikazes(_: BoolOption, value: bool) -> None:
    global kamikazeChance
    Kamikaze = ENGINE.DynamicLoadObject("dlc4_gd_Balance_Enemies.ClapTrap.Pawn_Balance_DLC4_Claptrap_Kamikaze",unrealsdk.find_class("AIPawnBalanceDefinition"),False)
    Kamikaze.DefaultItemPoolList[-1].PoolProbability.BaseValueConstant = kamikazeChance
    Kamikaze.ObjectFlags ^= 0x4000
    Kamikaze = ENGINE.DynamicLoadObject("dlc4_gd_Balance_Enemies.ClapTrap.Pawn_Balance_DLC4_Claptrap_Kamikaze_radical",unrealsdk.find_class("AIPawnBalanceDefinition"),False)
    Kamikaze.DefaultItemPoolList[-1].PoolProbability.BaseValueConstant, kamikazeChance = kamikazeChance, Kamikaze.DefaultItemPoolList[-1].PoolProbability.BaseValueConstant
    Kamikaze.ObjectFlags ^= 0x4000

@hook("WillowGame.Behavior_SetNumStashSlots:ApplyBehaviorToContext", Type.POST)
def BankUpgradeBypass(obj: UObject, __args: WrappedStruct, __ret: Any, __func: BoundFunction) -> None:
    player = __args.MyInstigatorObject.InvManager.StashSlots = obj.NewStashSlotCount
    return

ShopResetTimerOption = SliderOption(
    "Shop Reset in Minutes",
    20,
    5,
    20,
    1,
    True,
    description="Choose how fast you want to reset the shops.\nDefault Value: 20",
    on_change_while_enabled=changeShopTimer
)

AllowGamepadIconsOption = BoolOption(
    "Allow Xbox 360 Buttons",
    True,
    "On",
    "Off",
    description="With this enabled, game will be allowed to use gamepad icons.",
    on_change_while_enabled=allowIcons
)

BuffEndGameCommdecksOption = BoolOption(
    "Buff Endgame Command Decks",
    True,
    "On",
    "Off",
    description="With this enabled, every single commdeck in the game will be more powerful.",
    on_change_while_enabled=buffCommdecks
)

GuaranteedKamikazeDropsOption = BoolOption(
    "Guaranteed Kamikaze Drops",
    True,
    "On",
    "Off",
    description="With this enabled, every claptrap kamikaze in the game will have a guaranteed rare item drop (Makes finding all rare collectables from the DLC really easy).",
    on_change_while_enabled=patchKamikazes
)

NewBankSDUOption = BoolOption(
    "New Bank SDU in Shop",
    True,
    "On",
    "Off",
    description="With this enabled, there will be a new level of Bank SDU in Marcuses's Ammo Vendor that will give you a total of 256 gear slot for your bank."
)

MiniModCollection = [ShopResetTimerOption, BuffEndGameCommdecksOption, GuaranteedKamikazeDropsOption, NewBankSDUOption]
#BL1 Specific Mods
if Game.get_current().name == "BL1":
    MiniModCollection.append(AllowGamepadIconsOption)
#BL1E Specific Mods
#if Game.get_current().name == "BL1E":


def patch(enabled: bool):
    #BL1 Specific Mods
    if Game.get_current().name == "BL1":
        allowIcons(AllowGamepadIconsOption,AllowGamepadIconsOption.value if enabled else False)
    #BL1E Specific Mods
    #if Game.get_current().name == "BL1E":
    changeShopTimer(ShopResetTimerOption,ShopResetTimerOption.value if enabled else 20)
    buffCommdecks(BuffEndGameCommdecksOption,BuffEndGameCommdecksOption.value if enabled else False)
    patchKamikazes(GuaranteedKamikazeDropsOption,GuaranteedKamikazeDropsOption.value if enabled else False)
    prepWorkDone = enabled

def on_enable():
    global Globals, DLC1Globals, DLC2Globals, DLC3Globals, DLC4Globals, prepWorkDone
    Globals = ENGINE.DynamicLoadObject("gd_globals.General.Globals",unrealsdk.find_class("GlobalsDefinition"),False)
    DLC1Globals = ENGINE.DynamicLoadObject("dlc1_PackageDefinition.CustomGlobals",unrealsdk.find_class("GlobalsDefinition"),False)
    DLC2Globals = ENGINE.DynamicLoadObject("dlc2_packagedefinition.CustomGlobals",unrealsdk.find_class("GlobalsDefinition"),False)
    DLC3Globals = ENGINE.DynamicLoadObject("dlc3_PackageDefinition.CustomGlobals",unrealsdk.find_class("GlobalsDefinition"),False)
    DLC4Globals = ENGINE.DynamicLoadObject("dlc4_PackageDefinition.CustomGlobals",unrealsdk.find_class("GlobalsDefinition"),False)
    Globals.ObjectFlags |= 0x4000
    DLC1Globals.ObjectFlags |= 0x4000
    DLC2Globals.ObjectFlags |= 0x4000
    DLC3Globals.ObjectFlags |= 0x4000
    DLC4Globals.ObjectFlags |= 0x4000
    createBankSDU()
    patch(True)

on_disable = lambda: patch(False)

__version__: str
__version_info__: tuple[int, ...]
    
build_mod(options=MiniModCollection,hooks=[BankUpgradeBypass])