import time
import wx
import bitstring
import dictionaries

image_base = 0x401200

class UnitTable():
	def __init__(self, bitStream: bitstring.ConstBitStream):
		self.npcFunc, self.surfaceNo, self.spriteX, self.spriteY, self.spriteW, self.spriteH, self.style, self.priority,\
		self.unitCollW, self.unitCollH, self.mapCollW, self.mapCollH, self.health, self.coins, self.bonusChance, self.name =\
		bitStream.readlist('uintle:32, uintle:16, uintle:16, uintle:16, uintle:16, uintle:16, uintle:8, uintle:8,\
		uintle:8,uintle:8,uintle:8,uintle:8,uintle:16,intle:16,uintle:32,uintle:32')

		self.nameString = ""
		if (self.name != 0):
			searchBase = self.name - image_base
			temppos = bitStream.pos
			bitStream.pos = searchBase * 8
			self.nameString = bytearray.fromhex(str(bitStream.readto("0x00", bytealigned=True))[2:]).decode()[:-1]
			bitStream.pos = temppos

		#print(str(self.npcFunc)+"/"+str(self.npcFunc.to_bytes(4, 'little')))
		#print(str(self.surfaceNo)+"/"+str(self.surfaceNo.to_bytes(2, 'little')))

		#print(str(self.bonusChance)+"/"+str(self.bonusChance.to_bytes(4, 'little')))
		#print(str(self.name)+"/"+str(self.name.to_bytes(4, 'little')))
		#input()

def PrintUnitTableEntry(table: UnitTable, index: int = 0):
	print("NPC No. "+str(index))
	print(f"Function: {hex(table.npcFunc)}, Sprite surface: {dictionaries.spriteSurfaceDict[table.surfaceNo]},")
	print(f"Rect X: {table.spriteX}, Rect Y: {table.spriteY},")
	print(f"Rect Width: {table.spriteW}, Rect Height: {table.spriteH},")
	print(f"Style: {dictionaries.styleDict[table.style]}, lkFU priority: {table.priority},")
	print(f"Unit Hitbox Width: {table.unitCollW}, Unit Hitbox Height: {table.unitCollH},")
	print(f"Map Hitbox Width: {table.mapCollW}, Map Hitbox Height: {table.mapCollH},")
	if table.coins in dictionaries.coinDict.keys():
		print(f"HP: {table.health}, Coins: {dictionaries.coinLabelList[dictionaries.coinDict[table.coins]]},")
	else:
		print(f"HP: {table.health}, Coins: {table.coins},")
	print(f"Bonus: {dictionaries.bonusDict[table.bonusChance]},")
	print(f"Name Pointer: {hex(table.name)}, Namestring: {table.nameString}")


interger = int(0x1029).to_bytes(2, "little", signed=True)
for x in range(len(interger)):
	print(hex(interger[x]))
