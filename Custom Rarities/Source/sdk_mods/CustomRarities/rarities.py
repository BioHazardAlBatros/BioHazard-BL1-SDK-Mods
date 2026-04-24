from dataclasses import dataclass

DROP_ShortLived = 0
DROP_LongLived = 1
DROP_LiveForever = 2

@dataclass
class Rarity:
    MinLevel: int = 0
    MaxLevel: int = 0
    Color: int = 0x0
    DropLifeSpanType: int = DROP_ShortLived

ModifiedRarities = [
    Rarity(MinLevel = -1, MaxLevel = 1,   Color = 0xFFFFFFFF,DropLifeSpanType=DROP_ShortLived),
    Rarity(MinLevel = 2,  MaxLevel = 3,   Color = 0xFFFFFFFF,DropLifeSpanType=DROP_ShortLived),
    Rarity(MinLevel = 4,  MaxLevel = 6,   Color = 0x01A2F885,DropLifeSpanType=DROP_ShortLived),
    Rarity(MinLevel = 9,  MaxLevel = 11,  Color = 0xFF4A8AFF,DropLifeSpanType=DROP_LongLived),
    Rarity(MinLevel = 19, MaxLevel = 29,  Color = 0xFF7C2CAD,DropLifeSpanType=DROP_LiveForever),
    Rarity(MinLevel = 50, MaxLevel = 65,  Color = 0xFFFFB400,DropLifeSpanType=DROP_LiveForever),
    Rarity(MinLevel = 66, MaxLevel = 80,  Color = 0xFFFF9600,DropLifeSpanType=DROP_LiveForever),
    Rarity(MinLevel = 81, MaxLevel = 100, Color = 0xFFDC7800,DropLifeSpanType=DROP_LiveForever),
    Rarity(MinLevel = 170,MaxLevel = 170, Color = 0xFF3DD20B,DropLifeSpanType=DROP_LiveForever),
    Rarity(MinLevel = 171,MaxLevel = 171, Color = 0xFFCF4747,DropLifeSpanType=DROP_ShortLived),
    Rarity(MinLevel = 180,MaxLevel = 181, Color = 0xFFFFDB0D,DropLifeSpanType=DROP_ShortLived),
    Rarity(MinLevel = 182,MaxLevel = 190, Color = 0xFFFFDB0D,DropLifeSpanType=DROP_ShortLived),
    Rarity(MinLevel = 500,MaxLevel = 500, Color = 0x0000FFFF,DropLifeSpanType=DROP_LiveForever),
    Rarity(MinLevel = 15, MaxLevel = 18,  Color = 0xFFB572DC,DropLifeSpanType=DROP_LiveForever),
    Rarity(MinLevel = 12, MaxLevel = 14,  Color = 0xFF0058FD,DropLifeSpanType=DROP_LongLived),
    Rarity(MinLevel = 7,  MaxLevel = 8,   Color = 0x013DD20B,DropLifeSpanType=DROP_LiveForever),
    Rarity(MinLevel = 101,MaxLevel = 150, Color = 0x0000FFFF,DropLifeSpanType=DROP_LiveForever),
    Rarity(MinLevel = 151,MaxLevel = 169, Color = 0x0000B7B7,DropLifeSpanType=DROP_LiveForever),
    Rarity(MinLevel = 30, MaxLevel = 49,  Color = 0x00C10000,DropLifeSpanType=DROP_LiveForever)
]

VanillaRarities = [
    Rarity(MinLevel = -1, MaxLevel = 1,   Color = 0xFFFFFFFF,DropLifeSpanType=DROP_ShortLived),
    Rarity(MinLevel = 2,  MaxLevel = 4,   Color = 0xFFFFFFFF,DropLifeSpanType=DROP_ShortLived),
    Rarity(MinLevel = 5,  MaxLevel = 10,  Color = 0x013DD20B,DropLifeSpanType=DROP_LongLived),
    Rarity(MinLevel = 11, MaxLevel = 15,  Color = 0xFF2F78FF,DropLifeSpanType=DROP_LiveForever),
    Rarity(MinLevel = 16, MaxLevel = 49,  Color = 0xFF9132C8,DropLifeSpanType=DROP_LiveForever),
    Rarity(MinLevel = 50, MaxLevel = 60,  Color = 0xFFFFB400,DropLifeSpanType=DROP_LiveForever),
    Rarity(MinLevel = 61, MaxLevel = 65,  Color = 0xFFFF9600,DropLifeSpanType=DROP_LiveForever),
    Rarity(MinLevel = 66, MaxLevel = 100, Color = 0xFFDC7800,DropLifeSpanType=DROP_LiveForever),
    Rarity(MinLevel = 101,MaxLevel = 169, Color = 0x0000FFFF,DropLifeSpanType=DROP_LiveForever),
    Rarity(MinLevel = 170,MaxLevel = 170, Color = 0xFF3DD20B,DropLifeSpanType=DROP_LiveForever),
    Rarity(MinLevel = 171,MaxLevel = 171, Color = 0xFFCF4747,DropLifeSpanType=DROP_ShortLived),
    Rarity(MinLevel = 180,MaxLevel = 181, Color = 0xFFFFDB0D,DropLifeSpanType=DROP_ShortLived),
    Rarity(MinLevel = 182,MaxLevel = 190, Color = 0xFFFFDB0D,DropLifeSpanType=DROP_ShortLived),
    Rarity(MinLevel = 500,MaxLevel = 500, Color = 0x0000FFFF,DropLifeSpanType=DROP_LiveForever)
]
