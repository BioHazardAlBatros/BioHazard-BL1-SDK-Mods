import unrealsdk
from mods_base import build_mod, ENGINE
from unrealsdk import logging
from unrealsdk.hooks import Type, Block, add_hook, remove_hook
from typing import List, Dict, Optional, Callable

from .hooks import HandleNewCharacter, Display, PostSavesUpdated, OnSpawn, IsPlayerRestricted,TranslateUseFailure
from .vault_hunters import VaultHunter, _VAULT_HUNTERS
from .api import add_custom_character_class, get_character_definitions, get_character_count,get_character_info
from .ui import InventoryVendorScreen, BankScreen, PickupScreen, RewardsScreen

add_hook("WillowGame.ItemPickupGFxMovie:UpdateCompareAgainstThing", Type.POST, "pickup", PickupScreen)
add_hook("WillowGame.StatusMenuExGFxMovie:UpdateCardPanelWithCurrentActiveListEntry", Type.POST, "inv_mouse", InventoryVendorScreen)
add_hook("WillowGame.StatusMenuExGFxMovie:extCard2Visible", Type.POST, "inv_compare", InventoryVendorScreen)
add_hook("WillowGame.StatusMenuExGFxMovie:UpdateCardPanelWithCurrentCell", Type.POST, "inv_equip", InventoryVendorScreen)
add_hook("WillowGame.VendingMachineGFxMovie:UpdateCardPanelWithCurrentActiveListEntry", Type.POST, "vendor_mouse", InventoryVendorScreen)
add_hook("WillowGame.VendingMachineGFxMovie:extCard2Visible", Type.POST, "vendor_compare", InventoryVendorScreen)
add_hook("WillowGame.VendingMachineGFxMovie:UpdateCardPanelWithItemOfTheDay", Type.POST, "vendor_item", InventoryVendorScreen)
add_hook("WillowGame.BankGFxMovie:UpdateCardPanelWithCurrentActiveListEntry", Type.POST, "bank_mouse", BankScreen)
add_hook("WillowGame.BankGFxMovie:extCard2Visible", Type.POST, "bank_compare", BankScreen)
add_hook("WillowGame.QuestAcceptGFxMovie:extSetUpRewardsPage", Type.POST, "rewards_screen", RewardsScreen)


build_mod(hooks=[HandleNewCharacter,Display,PostSavesUpdated,OnSpawn,IsPlayerRestricted,TranslateUseFailure])

__version__: str
__version_info__: tuple[int, ...]

logging.info(f"Character Vault Loaded: {__version__}, {__version_info__}")