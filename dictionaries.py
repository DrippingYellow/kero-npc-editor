from enum import IntEnum

class FieldUnitType(IntEnum):
	NPC = 0
	BULLET = 1
	PARTICLE = 2
	BONUS = 3
	NOTIFY = 4
	SUBUNIT = 5

iconFilepaths = [
	"images/icon_npc.png",
	"images/icon_bullet.png",
	"images/icon_particle.png",
	"images/icon_bonus.png",
	"images/icon_notify.png",
	"images/icon_subunit.png"
]

fieldUnitLabels = [
	"NPC",
	"Bullet",
	"Particle",
	"Bonus",
	"Notify",
	"Sub-Unit"
]

coinLabelList = [
	"No coins",
	"1 Coin, No 1UP",
	"10 Coins, No 1UP",
	"1 Coin, 1UP",
	"10 Coins, 1UP",
	"20 Coins, 1UP",
	"50 Coins, 1UP",
	"Foliage Placeholder?",
	"10 Coins (Stage 7)",
	"Projectile Placeholder?"
]

coinDict = {
	0: 0,
	1: 1,
	10: 2,
	-1: 3,
	-10: 4,
	-20: 5,
	-50: 6,
	-0x3FD: 7,
	-0x3FE: 8,
	-0x3FF: 9
}

styleDict = [
	"None",
	"Small (normal)",
	"Medium (normal)",
	"Large (normal)",
	"Small (black)",
	"Medium (black)",
	"Large (black)",
	"Droplet",
	"Foliage",
	"Fireball",
]

bulletStyleDict = [
	"None",
	"Pea Shooter",
	"Fan",
	"Bubble",
	"Flame",
	"Kuro Blaster"

]

bonusDict = [
	"0 - Doesn't drop",
	"1 - Rarely drops",
	"2 - Occasionally drops",
	"3 - Often drops",
	"4 - Almost always drops",
	"5 - Guaranteed drops"
]

spriteSurfaceDict = [
	"Wallpaper Spritesheet",
	"Background Tileset",
	"Middleground Tileset",
	"Global NPC Spritesheet",
	"Level NPC Spritesheet",
	"Player Character Spritesheet",
	"Particle & Bullet Spritesheet",
	"Foreground Tileset",
	"Mobile Buttons Spritesheet",
	"Item Spritesheet",
	"Language-Specific Spritesheet",
	"Item (duplicate?)",
	"Font Spritesheet",
]

maxUnits = [
	634, # NPC
	36,  # BULLET
	92,  # PARTICLE
	11,  # BONUS
	6,   # NOTIFY
	9    # SUBUNIT
]

npcTable = []
bulletTable = []
particleTable = []
bonusTable = []
notifyTable = []
subUnitTable = []

unitTables = [
	npcTable,
	bulletTable,
	particleTable,
	bonusTable,
	notifyTable,
	subUnitTable
]

