import unrealsdk
from mods_base import build_mod, ENGINE, BaseOption, SliderOption

chance = 1.0

def patch():
    global chance
    Kamikaze = ENGINE.DynamicLoadObject("dlc4_gd_Balance_Enemies.ClapTrap.Pawn_Balance_DLC4_Claptrap_Kamikaze",unrealsdk.find_class("AIPawnBalanceDefinition"),False)
    Kamikaze.DefaultItemPoolList[-1].PoolProbability.BaseValueConstant = chance
    Kamikaze.ObjectFlags ^= 0x4000
    Kamikaze = ENGINE.DynamicLoadObject("dlc4_gd_Balance_Enemies.ClapTrap.Pawn_Balance_DLC4_Claptrap_Kamikaze_radical",unrealsdk.find_class("AIPawnBalanceDefinition"),False)
    Kamikaze.DefaultItemPoolList[-1].PoolProbability.BaseValueConstant, chance = chance, Kamikaze.DefaultItemPoolList[-1].PoolProbability.BaseValueConstant
    Kamikaze.ObjectFlags ^= 0x4000


#gd_Balance.WeightingPlayerCount.WeaponsDropsPerPlayer.ConditionalInitialization.ConditionalExpressionList[0].BaseValueIfTrue.BaseValueConstant = 2.5
#gd_Balance.WeightingPlayerCount.WeaponsDropsPerPlayer.ConditionalInitialization.ConditionalExpressionList[1].BaseValueIfTrue.BaseValueConstant = 2.5
#gd_Balance.WeightingPlayerCount.WeaponsDropsPerPlayer.ConditionalInitialization.ConditionalExpressionList[2].BaseValueIfTrue.BaseValueConstant = 2.5

on_enable = patch
on_disable = patch

build_mod()

__version__: str
__version_info__: tuple[int, ...]
