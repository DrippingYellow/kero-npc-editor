import os
import wx
import dictionaries
#from PIL import Image, ImageDraw
from typing import Any
from read_file import UnitTable, PrintUnitTableEntry
from bitstring import ConstBitStream

def DisableLabeledControls(windows: Any):
	for x in range(len(windows)):
		windows[x].Disable()

def EnableLabeledControls(windows: Any):
	for x in range(len(windows)):
		windows[x].Enable()

class LabeledControl:
	def __init__(self, parent: wx.Window, control: wx.Window, label: wx.Window, proportion: int = 1, flag: int = 0, border: int = 0, userData: Any | None = None):
		self.control = control
		self.label = label
		self.parent = parent

		self.gridSizer = wx.FlexGridSizer(2, 1, 0, 5)
		self.gridSizer.Add(self.label, 1, flag, border, userData)
		self.gridSizer.Add(self.control, proportion, flag, border, userData)

		parent.controlBoxes.append(self.control)

	def AddToSizer(self, sizer: wx.Sizer, proportion: int = 1, flag: int = 0, border: int = 0, userData: Any | None = None):
		sizer.Add(self.gridSizer, proportion, flag, border, userData)
	
	def SetValue(self, value: Any):
		self.control.SetValue(value)

	def SetLabel(self, string: str):
		self.label.SetLabel(string)

	def GetValue(self):
		self.control.GetValue()
		return
	
	def GetSelection(self):
		self.control.GetSelection()

	def SetSelection(self, integer):
		self.control.SetSelection(integer)
	
	def BindControl(self, event, handler, id = wx.ID_ANY, id2 = wx.ID_ANY):
		self.parent.Bind(event, handler, self.control, id, id2)

class MainFrame(wx.Frame):
	def __init__(self, parent):
		wx.Frame.__init__(self, parent, title="Kero NPC Editor", size=(600,500), style=wx.ICONIZE|wx.CLOSE_BOX|wx.MINIMIZE_BOX)
		self.nb = wx.Notebook(self)

		self.stream_pos = 0
		self.filename = "."
		self.dirname = "."
		self.default_particle_function = 0xFFFFFFFF

		notebookIcons = []

		for x in range(len(dictionaries.FieldUnitType)):
			notebookIcons.append(wx.Image(dictionaries.iconFilepaths[x], wx.BITMAP_TYPE_PNG, x))
			bitmap = wx.Bitmap(notebookIcons[x])

		self.nb.SetImages(notebookIcons)

		for x in range(len(dictionaries.FieldUnitType)):
			self.nb.AddPage(EditorPanel(self.nb, x), dictionaries.fieldUnitLabels[x], imageId=x)


		self.Bind(wx.EVT_CLOSE, self.OnClose, self)
		self.Show()

		fileopen = wx.Menu()
		menuOpen = fileopen.Append(wx.ID_OPEN, item="Open", helpString="Open a Kero Blaster executable")
		fileopen.AppendSeparator()
		self.menuSave = fileopen.Append(wx.ID_SAVE, item="Save", helpString="Save your changes")

		self.menuBar = wx.MenuBar()
		self.menuBar.Append(fileopen, "File")

		self.SetMenuBar(self.menuBar)
		self.Bind(wx.EVT_MENU, self.OnOpen, menuOpen)
		self.Bind(wx.EVT_MENU, self.OnSave, self.menuSave)

		self.menuSave.Enable(False) # No Disable function for this particular class apparently

	def OnClose(self, e):
		print("Poopoo")
		self.Destroy()

	def OnOpen(self, e):
		fileDialog = wx.FileDialog(self, "Choose a Kero Blaster executable file.", self.dirname, self.filename, style=wx.FD_OPEN)
		if (fileDialog.ShowModal() == wx.ID_CANCEL):
			self.Destroy()
			return

		old_filename = self.filename
		old_dirname = self.dirname
		self.filename = fileDialog.GetFilename()
		self.dirname = fileDialog.GetDirectory()
		
		try:
			stream = ConstBitStream(filename=self.dirname+"/"+self.filename)
		except:
			self.filename = old_filename
			self.dirname = old_dirname
			dlg = wx.MessageDialog(self, "Unable to load file, or file does not exist. Try again.")
			dlg.ShowWindowModal()
			return

		old_stream_pos = self.stream_pos
		temp_stream_pos = stream.find(bytearray.fromhex("0000000005000000000000000000000000000000000000000000000000000000"))
		#print(hex(temp_stream_pos[0] // 8))
		#input()

		if len(temp_stream_pos) == 0: # if empty tuple
			dlg = wx.MessageDialog(self, "Unable to find field unit tables. Make sure you chose a Kero Blaster Windows executable file.", "ERROR: Table not found", wx.OK)
			dlg.ShowModal()
			dlg.Destroy()

			self.stream_pos = old_stream_pos
			self.filename = old_filename
			self.dirname = old_dirname

			print("Task failed successfully")
			return

		self.stream_pos = temp_stream_pos[0]
		stream.pos = self.stream_pos
		self.menuSave.Enable()

		for y in range(len(dictionaries.FieldUnitType)):
			dictionaries.unitTables[y].clear()
			for x in range(dictionaries.maxUnits[y]):
				dictionaries.unitTables[y].append(UnitTable(stream))
				if y == dictionaries.FieldUnitType.PARTICLE:
					if x == 0:
						self.default_particle_function = dictionaries.unitTables[y][x].npcFunc
						print("Founnt it")
						input()
			self.nb.GetPage(y).InitTable()

		print(hex(self.default_particle_function))
		print(self.stream_pos // 8)

	def OnSave(self, e):
		print(self.dirname+"/"+self.filename)
		fileDialog = wx.FileDialog(self, "Choose a Kero Blaster executable file.", self.dirname, self.filename, style=wx.FD_SAVE)
		if (fileDialog.ShowModal() == wx.ID_CANCEL):
			self.Destroy()
			return
		
		print(self.dirname+"/"+self.filename)
		
		with open(self.dirname+"/"+self.filename, "rb+") as f:
			f.seek(self.stream_pos // 8, os.SEEK_SET)
			#f.seek(64, os.SEEK_CUR)
			#print(int.from_bytes(f.read(4), "little"))
			#f.seek(self.stream_pos // 8, os.SEEK_SET)
			for y in range(len(dictionaries.FieldUnitType)):
				for x in range(dictionaries.maxUnits[y]):
					temptable = dictionaries.unitTables[y][x]
					f.write(temptable.npcFunc.to_bytes(4, "little", signed=False))
					f.write(temptable.surfaceNo.to_bytes(2, "little", signed=False))
					f.write(temptable.spriteX.to_bytes(2, "little", signed=False))
					f.write(temptable.spriteY.to_bytes(2, "little", signed=False))
					f.write(temptable.spriteW.to_bytes(2, "little", signed=False))
					f.write(temptable.spriteH.to_bytes(2, "little", signed=False))
					f.write(temptable.style.to_bytes(1))
					f.write(temptable.priority.to_bytes(1))
					f.write(temptable.unitCollW.to_bytes(1))
					f.write(temptable.unitCollH.to_bytes(1))
					f.write(temptable.mapCollW.to_bytes(1))
					f.write(temptable.mapCollH.to_bytes(1))
					f.write(temptable.health.to_bytes(2, "little", signed=False))
					f.write(temptable.coins.to_bytes(2, "little", signed=True))
					f.write(temptable.bonusChance.to_bytes(4, "little", signed=False))
					f.write(temptable.name.to_bytes(4, "little", signed=False))



class EditorPanel(wx.Panel):
	def __init__(self, parent, type: dictionaries.FieldUnitType):
		wx.Panel.__init__(self, parent)
		self.fieldUnitType: dictionaries.FieldUnitType = type
		self.Show()
		self.megalist = []
		self.controlBoxes = []

		image = wx.Image("images/under_construction.png", wx.BITMAP_TYPE_PNG)
		imageBitmap = wx.StaticBitmap(self, wx.ID_ANY, wx.Bitmap(image))

		self.InitBoxes()
		self.UpdateLabels()
		self.BindControls()

		gridSizer = wx.GridSizer(3, 3, 0, 5)
		self.codeOffsetBox.AddToSizer(gridSizer, 2, wx.EXPAND)
		self.stringOffsetBox.AddToSizer(gridSizer, 2, wx.EXPAND)
		gridSizer.AddSpacer(1)
		self.coinBox.AddToSizer(gridSizer, 2, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.EXPAND)
		self.hpBox.AddToSizer(gridSizer, 1, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.EXPAND)
		self.bonusBox.AddToSizer(gridSizer, 2, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.EXPAND)
		self.internalNameBox.AddToSizer(gridSizer, 2, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.EXPAND)
		self.styleBox.AddToSizer(gridSizer, 2, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.EXPAND)
		self.lkFUBox.AddToSizer(gridSizer, 2, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.EXPAND)

		mainSizerTopBox = wx.StaticBoxSizer(wx.StaticBox(self, label=dictionaries.fieldUnitLabels[self.fieldUnitType]+" Attributes"), wx.VERTICAL)
		mainSizerTopBox.Add(gridSizer, 1, wx.ALL)
		mainSizerTopBox.AddSpacer(10)

		mainSizerTop = wx.BoxSizer(wx.VERTICAL)
		mainSizerTop.Add(self.searchBox, 1, flag=wx.ALIGN_CENTER)
		mainSizerTop.AddSpacer(10)
		mainSizerTop.Add(mainSizerTopBox, 9, flag=wx.EXPAND)

		gridSizer2 = wx.BoxSizer(wx.VERTICAL)
		self.unitWidthBox.AddToSizer(gridSizer2)
		self.unitHeightBox.AddToSizer(gridSizer2)
		self.mapWidthBox.AddToSizer(gridSizer2)
		self.mapHeightBox.AddToSizer(gridSizer2)

		mainSizerBottomLeft = wx.StaticBoxSizer(wx.StaticBox(self, label="Collision Data"), wx.HORIZONTAL)
		mainSizerBottomLeft.Add(imageBitmap, 4, wx.EXPAND, 5)
		mainSizerBottomLeft.Add(gridSizer2, 1, wx.EXPAND, 5)

		gridSizer3 = wx.GridSizer(2, 2, 16, 24)
		self.spriteXBox.AddToSizer(gridSizer3, wx.ALIGN_CENTER)
		self.spriteYBox.AddToSizer(gridSizer3, wx.ALIGN_CENTER)
		self.spriteWidthBox.AddToSizer(gridSizer3, wx.ALIGN_CENTER)
		self.spriteHeightBox.AddToSizer(gridSizer3, wx.ALIGN_CENTER)

		mainSizerBottomRight = wx.StaticBoxSizer(wx.StaticBox(self, label="Image Data"), wx.VERTICAL)
		mainSizerBottomRight.Add(gridSizer3, 5)
		self.surfaceNumberBox.AddToSizer(mainSizerBottomRight, 2)
		mainSizerBottomRight.Add(self.visualEditorButton, 1)

		mainSizerBottom = wx.BoxSizer(wx.HORIZONTAL)
		mainSizerBottom.Add(mainSizerBottomLeft, 1, wx.EXPAND)
		mainSizerBottom.Add(mainSizerBottomRight, 1, wx.EXPAND)


		self.mainSizer = wx.BoxSizer(wx.VERTICAL)
		self.mainSizer.Add(mainSizerTop, 50, wx.EXPAND, border=5)
		self.mainSizer.Add(mainSizerBottom, 50, wx.EXPAND, border=5)

		self.SetSizer(self.mainSizer)
		self.SetAutoLayout(True)


	def OnClear(self, e):
		return
	
	def Test(self, event: wx.CommandEvent):
		print(event.GetString())
		#event.EventObject.Disable()

	def InitBoxes(self):
		# Top half
		self.searchBox = wx.ComboBox(self, wx.ID_ANY, "", pos=(0, 0), size=(200, 16))
		self.controlBoxes.append(self.searchBox)

		self.codeOffsetBox = LabeledControl(self, wx.TextCtrl(self, value="", style=wx.TE_READONLY),
								wx.StaticText(self, label="Code Offset:"), 1, wx.EXPAND)
		self.stringOffsetBox = LabeledControl(self, wx.TextCtrl(self, value="", style=wx.TE_READONLY),
								wx.StaticText(self, label="String Offset:"), 1, wx.EXPAND)
		
		#print(self.fieldUnitType)
		#tempstr = input()
		if self.fieldUnitType != dictionaries.FieldUnitType.NPC:
			self.coinBox = LabeledControl(self, wx.SpinCtrl(self, min=-32768, max=32767, style=wx.CB_DROPDOWN, name="Coins"),
								wx.StaticText(self, label="Var1: "), 1, wx.EXPAND)
		else:
			self.coinBox = LabeledControl(self, wx.ComboBox(self, choices=dictionaries.coinLabelList, style=wx.CB_DROPDOWN|wx.TE_PROCESS_ENTER, name="Coins"),
								wx.StaticText(self, label="Var1: "), 1, wx.EXPAND)
			
		self.hpBox = LabeledControl(self, wx.SpinCtrl(self, min=0, max=65535, style=wx.ALIGN_LEFT),
								wx.StaticText(self, label="Var2: "), 1, wx.EXPAND)
		self.bonusBox = LabeledControl(self, wx.ComboBox(self, choices=dictionaries.bonusDict, style=wx.CB_DROPDOWN|wx.CB_READONLY, name="Coins"),
								wx.StaticText(self, label="Drop chance: "), 1, wx.EXPAND)
		self.internalNameBox = LabeledControl(self, wx.TextCtrl(self, value=""),
								wx.StaticText(self, label="Internal name: "), 1, wx.EXPAND)
		
		if self.fieldUnitType == dictionaries.FieldUnitType.BULLET:
			stylechoices = dictionaries.bulletStyleDict
		else:
			stylechoices = dictionaries.styleDict

		self.styleBox = LabeledControl(self, wx.ComboBox(self, choices=stylechoices, style=wx.CB_DROPDOWN|wx.CB_READONLY, name="Style"),
								wx.StaticText(self, label="Style: "), 1, wx.EXPAND)
		self.lkFUBox = LabeledControl(self, wx.SpinCtrl(self, min=0, max=255, style=wx.ALIGN_LEFT),
								wx.StaticText(self, label="lkFU Priority"), 1, wx.EXPAND)
		
		# Bottom left
		self.unitWidthBox = LabeledControl(self, wx.SpinCtrl(self, min=0, max=255, style=wx.ALIGN_LEFT),
								wx.StaticText(self, label="Unit W:"), 1, wx.EXPAND)
		self.unitHeightBox = LabeledControl(self, wx.SpinCtrl(self, min=0, max=255, style=wx.ALIGN_LEFT),
								wx.StaticText(self, label="Unit H:"), 1, wx.EXPAND)
		self.mapWidthBox = LabeledControl(self, wx.SpinCtrl(self, min=0, max=255, style=wx.ALIGN_LEFT),
								wx.StaticText(self, label="Map W:"), 1, wx.EXPAND)
		self.mapHeightBox = LabeledControl(self, wx.SpinCtrl(self, min=0, max=255, style=wx.ALIGN_LEFT),
								wx.StaticText(self, label="Map H:"), 1, wx.EXPAND)
		
		# Bottom right

		self.spriteXBox = LabeledControl(self, wx.SpinCtrl(self, min=0, max=65535),
								wx.StaticText(self, label="Sprite Rect X:"), 1, wx.ALIGN_CENTER_VERTICAL)
		self.spriteYBox = LabeledControl(self, wx.SpinCtrl(self, min=0, max=65535),
								wx.StaticText(self, label="Sprite Rect Y:"), 1, wx.ALIGN_CENTER_VERTICAL)
		self.spriteWidthBox = LabeledControl(self, wx.SpinCtrl(self, min=0, max=65535),
								wx.StaticText(self, label="Sprite Rect Width:"), 1, wx.ALIGN_CENTER_VERTICAL)
		self.spriteHeightBox = LabeledControl(self, wx.SpinCtrl(self, min=0, max=65535),
								wx.StaticText(self, label="Sprite Rect Height:"), 1, wx.ALIGN_CENTER_VERTICAL)
		
		self.surfaceNumberBox = LabeledControl(self, wx.ComboBox(self, choices=dictionaries.spriteSurfaceDict, style=wx.CB_DROPDOWN|wx.CB_READONLY),
								wx.StaticText(self, label="Sprite Surface: "), 1, wx.EXPAND)
		
		self.visualEditorButton = wx.Button(self, label="Open Visual Editor")

		self.coinBox.label.SetToolTip("Test")
		
		DisableLabeledControls(self.controlBoxes)

	def BindControls(self):
		self.Bind(wx.EVT_COMBOBOX, self.UsedSearchBox, self.searchBox)
		#self.Bind(wx.EVT_COMBOBOX, self.Test, self.coinBox.control)
		#self.Bind(wx.EVT_SPINCTRL, self.UpdateTableValue_HP, self.hpBox.control)
		self.Bind(wx.EVT_SIZE, self.OnSize, self)
		self.coinBox.BindControl(wx.EVT_COMBOBOX, self.UpdateTableValue_Coins)
		self.coinBox.BindControl(wx.EVT_TEXT_ENTER, self.UpdateTableValue_CoinsTextEdit)
		self.coinBox.BindControl(wx.EVT_SPINCTRL, self.UpdateTableValue_CoinsSpinCtrl)

		self.hpBox.BindControl(wx.EVT_SPINCTRL, self.UpdateTableValue_HP)
		self.bonusBox.BindControl(wx.EVT_COMBOBOX, self.UpdateTableValue_BonusChance)
		self.styleBox.BindControl(wx.EVT_COMBOBOX, self.UpdateTableValue_Style)
		self.lkFUBox.BindControl(wx.EVT_COMBOBOX, self.UpdateTableValue_Priority)

		self.unitWidthBox.BindControl(wx.EVT_SPINCTRL, self.UpdateTableValue_UnitCollW)
		self.unitHeightBox.BindControl(wx.EVT_SPINCTRL, self.UpdateTableValue_UnitCollH)
		self.mapWidthBox.BindControl(wx.EVT_SPINCTRL, self.UpdateTableValue_MapCollW)
		self.mapHeightBox.BindControl(wx.EVT_SPINCTRL, self.UpdateTableValue_MapCollH)

		self.spriteXBox.BindControl(wx.EVT_SPINCTRL, self.UpdateTableValue_SpriteX)
		self.spriteYBox.BindControl(wx.EVT_SPINCTRL, self.UpdateTableValue_SpriteY)
		self.spriteWidthBox.BindControl(wx.EVT_SPINCTRL, self.UpdateTableValue_SpriteW)
		self.spriteHeightBox.BindControl(wx.EVT_SPINCTRL, self.UpdateTableValue_SpriteH)

		self.surfaceNumberBox.BindControl(wx.EVT_COMBOBOX, self.UpdateTableValue_SurfaceNumber)

		self.Bind(wx.EVT_BUTTON, self.NotImplementedDialog, self.visualEditorButton)

	def OnSize(self, e):
		if self.GetAutoLayout():
			self.Layout()

	def InitTable(self):
		self.megalist.clear()
		for x in range(dictionaries.maxUnits[self.fieldUnitType]):
			print (x)
			self.megalist.append(dictionaries.fieldUnitLabels[self.fieldUnitType]+" #"+str("%03d" % (x)))
		self.searchBox.Clear()
		self.searchBox.AppendItems(self.megalist)
		self.searchBox.SetSelection(0)
		#EnableLabeledControls(self.controlBoxes)

		self.UpdateVisualTable()

	def UsedSearchBox(self, e):
		self.UpdateVisualTable()

	def UpdateVisualTable(self):
		temptable = dictionaries.unitTables[self.fieldUnitType][self.searchBox.GetSelection()]
		self.codeOffsetBox.SetValue(hex(temptable.npcFunc))

		if temptable.name != 0:
			self.stringOffsetBox.SetValue(hex(temptable.name))
		else:
			self.stringOffsetBox.SetValue("N/A")
		
		if temptable.coins in dictionaries.coinDict.keys() and self.fieldUnitType == dictionaries.FieldUnitType.NPC:
			self.coinBox.SetValue(dictionaries.coinLabelList[dictionaries.coinDict[temptable.coins]])
		else:
			self.coinBox.SetValue(str(temptable.coins))
		
		self.hpBox.SetValue(str(temptable.health))
		self.bonusBox.SetValue(dictionaries.bonusDict[temptable.bonusChance])
		self.internalNameBox.SetValue(temptable.nameString)

		if temptable.npcFunc == self.GetGrandParent().default_particle_function:
			self.hpBox.SetLabel("# of animation frames: ")
			self.coinBox.SetLabel("Animation speed: ")
		else:
			print(hex(self.GetGrandParent().default_particle_function))
			self.UpdateLabels()

		if self.fieldUnitType == dictionaries.FieldUnitType.BULLET:
			self.styleBox.SetValue(dictionaries.bulletStyleDict[temptable.style])
		else:
			self.styleBox.SetValue(dictionaries.styleDict[temptable.style])

		self.lkFUBox.SetValue(temptable.priority)

		self.unitWidthBox.SetValue(temptable.unitCollW)
		self.unitHeightBox.SetValue(temptable.unitCollH)
		self.mapWidthBox.SetValue(temptable.mapCollW)
		self.mapHeightBox.SetValue(temptable.mapCollH)
		self.spriteXBox.SetValue(temptable.spriteX)
		self.spriteYBox.SetValue(temptable.spriteY)
		self.spriteWidthBox.SetValue(temptable.spriteW)
		self.spriteHeightBox.SetValue(temptable.spriteH)

		self.surfaceNumberBox.SetValue(dictionaries.spriteSurfaceDict[temptable.surfaceNo])

		if self.searchBox.GetSelection() == 0 and self.fieldUnitType == dictionaries.FieldUnitType.NPC:
			DisableLabeledControls(self.controlBoxes)
			self.searchBox.Enable()
		else:
			EnableLabeledControls(self.controlBoxes)

	
	def UpdateLabels(self):
		if self.fieldUnitType == dictionaries.FieldUnitType.BULLET:
			self.hpBox.SetLabel("# of hits: ")
			self.coinBox.SetLabel("Damage: ")
		elif self.fieldUnitType == dictionaries.FieldUnitType.BONUS:
			self.hpBox.SetLabel("Var2: ")
			self.coinBox.SetLabel("Value: ")
		elif self.fieldUnitType == dictionaries.FieldUnitType.NPC:
			self.hpBox.SetLabel("HP: ")
			self.coinBox.SetLabel("Coins: ")
		else:
			self.coinBox.SetLabel("Var1: ")
			self.hpBox.SetLabel("Var2: ")

	def NotImplementedDialog(self, e):
		dlg = wx.MessageDialog(self, "Sorry, this isn't implemented! Come back in a later update (if there ever is one) :)", "Visual Editor Not Implemented")
		dlg.ShowWindowModal()

# UPDATING VALUES IN THE TABLE (there's probably a better way to do this...)

	def UpdateTableValue_Coins(self, e):
		tempindex = self.searchBox.GetSelection()
		temptable = dictionaries.unitTables[self.fieldUnitType][tempindex]
		tempvalue = e.GetInt()

		if tempvalue in dictionaries.coinDict.values():
			temptable.coins = list(dictionaries.coinDict.keys())[tempvalue]
			dictionaries.unitTables[self.fieldUnitType][tempindex] = temptable
		PrintUnitTableEntry(temptable, tempindex)

	def UpdateTableValue_CoinsTextEdit(self, e):
		string = e.GetString()
		tempindex = self.searchBox.GetSelection()
		temptable = dictionaries.unitTables[self.fieldUnitType][tempindex]

		try:
			print(string)
			tempvalue = int(string)		
		except:
			tempvalue = 0
			e.EventObject.SetSelection(0)

		temptable.coins = tempvalue
		PrintUnitTableEntry(temptable, tempindex)
		dictionaries.unitTables[self.fieldUnitType][tempindex] = temptable
		self.UpdateVisualTable()

	def UpdateTableValue_CoinsSpinCtrl(self, e):
		tempindex = self.searchBox.GetSelection()
		temptable = dictionaries.unitTables[self.fieldUnitType][tempindex]
		temptable.coins = e.GetInt()
		PrintUnitTableEntry(temptable, tempindex)
		dictionaries.unitTables[self.fieldUnitType][tempindex] = temptable

	def UpdateTableValue_HP(self, e):
		tempindex = self.searchBox.GetSelection()
		temptable = dictionaries.unitTables[self.fieldUnitType][tempindex]
		temptable.health = e.GetInt()
		PrintUnitTableEntry(temptable, tempindex)
		dictionaries.unitTables[self.fieldUnitType][tempindex] = temptable

	def UpdateTableValue_Style(self, e):
		tempindex = self.searchBox.GetSelection()
		temptable = dictionaries.unitTables[self.fieldUnitType][tempindex]
		temptable.style = e.GetInt()
		PrintUnitTableEntry(temptable, tempindex)
		dictionaries.unitTables[self.fieldUnitType][tempindex] = temptable

	def UpdateTableValue_BonusChance(self, e):
		tempindex = self.searchBox.GetSelection()
		temptable = dictionaries.unitTables[self.fieldUnitType][tempindex]
		temptable.bonusChance = e.GetInt()
		PrintUnitTableEntry(temptable, tempindex)
		dictionaries.unitTables[self.fieldUnitType][tempindex] = temptable

	def UpdateTableValue_Priority(self, e):
		tempindex = self.searchBox.GetSelection()
		temptable = dictionaries.unitTables[self.fieldUnitType][tempindex]
		temptable.priority = e.GetInt()
		PrintUnitTableEntry(temptable, tempindex)
		dictionaries.unitTables[self.fieldUnitType][tempindex] = temptable

	def UpdateTableValue_SurfaceNumber(self, e):
		tempindex = self.searchBox.GetSelection()
		temptable = dictionaries.unitTables[self.fieldUnitType][tempindex]
		temptable.surfaceNo = e.GetInt()
		PrintUnitTableEntry(temptable, tempindex)
		dictionaries.unitTables[self.fieldUnitType][tempindex] = temptable

	def UpdateTableValue_UnitCollW(self, e):
		tempindex = self.searchBox.GetSelection()
		temptable = dictionaries.unitTables[self.fieldUnitType][tempindex]
		temptable.unitCollW = e.GetInt()
		PrintUnitTableEntry(temptable, tempindex)
		dictionaries.unitTables[self.fieldUnitType][tempindex] = temptable

	def UpdateTableValue_UnitCollH(self, e):
		tempindex = self.searchBox.GetSelection()
		temptable = dictionaries.unitTables[self.fieldUnitType][tempindex]
		temptable.unitCollH = e.GetInt()
		PrintUnitTableEntry(temptable, tempindex)
		dictionaries.unitTables[self.fieldUnitType][tempindex] = temptable

	def UpdateTableValue_MapCollW(self, e):
		tempindex = self.searchBox.GetSelection()
		temptable = dictionaries.unitTables[self.fieldUnitType][tempindex]
		temptable.mapCollW = e.GetInt()
		PrintUnitTableEntry(temptable, tempindex)
		dictionaries.unitTables[self.fieldUnitType][tempindex] = temptable

	def UpdateTableValue_MapCollH(self, e):
		tempindex = self.searchBox.GetSelection()
		temptable = dictionaries.unitTables[self.fieldUnitType][tempindex]
		temptable.mapCollH = e.GetInt()
		PrintUnitTableEntry(temptable, tempindex)
		dictionaries.unitTables[self.fieldUnitType][tempindex] = temptable

	def UpdateTableValue_SpriteX(self, e):
		tempindex = self.searchBox.GetSelection()
		temptable = dictionaries.unitTables[self.fieldUnitType][tempindex]
		temptable.spriteX = e.GetInt()
		PrintUnitTableEntry(temptable, tempindex)
		dictionaries.unitTables[self.fieldUnitType][tempindex] = temptable

	def UpdateTableValue_SpriteY(self, e):
		tempindex = self.searchBox.GetSelection()
		temptable = dictionaries.unitTables[self.fieldUnitType][tempindex]
		temptable.spriteY = e.GetInt()
		PrintUnitTableEntry(temptable, tempindex)
		dictionaries.unitTables[self.fieldUnitType][tempindex] = temptable

	def UpdateTableValue_SpriteW(self, e):
		tempindex = self.searchBox.GetSelection()
		temptable = dictionaries.unitTables[self.fieldUnitType][tempindex]
		temptable.spriteW = e.GetInt()
		PrintUnitTableEntry(temptable, tempindex)
		dictionaries.unitTables[self.fieldUnitType][tempindex] = temptable

	def UpdateTableValue_SpriteH(self, e):
		tempindex = self.searchBox.GetSelection()
		temptable = dictionaries.unitTables[self.fieldUnitType][tempindex]
		temptable.spriteH = e.GetInt()
		PrintUnitTableEntry(temptable, tempindex)
		dictionaries.unitTables[self.fieldUnitType][tempindex] = temptable


app = wx.App(False)
frame = MainFrame(None)


app.MainLoop()
