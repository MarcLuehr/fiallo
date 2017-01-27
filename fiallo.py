import sys
from PyQt5.QtWidgets import QApplication, QDialog, QFileDialog, QListWidgetItem
from fialloui import Ui_Fiallo
from tftpy import tftpy
import os
import re
import json
from os.path import expanduser

class UIHandler():
	def __init__(self, ui):
		self.updatefile = ''
		self.ui = ui
		self.filesize = 0
		self.updateprogress = 0
		self.Command = ""
		self.commands = [['{"device":{"identity":{"version":<#>}}}', ['null']]]
		
		_json = expanduser("~/.fiallo/.json")
		try:
			with open(_json, 'r') as infile:
				self.commands.append(json.load(infile))
		except:
			pass
		
	def handleBrowse(self):
		(self.updatefile, extensionFilter) = QFileDialog.getOpenFileName(caption='Select Update', filter='*.bin')
		self.ui.lineUpdateFile.setText(self.updatefile)
		try:
			with open(self.updatefile, 'rb') as infile:
				infile.seek(int('0x0E', 16))
				(main, major, minor) = infile.read(3)
			with open(self.updatefile, 'rb') as infile:
				infile.seek(int('0x11', 16))
				other = infile.read(3).decode("utf-8")
				self.ui.label.setText("Found valid image\nR_%d_%d_%d-%s" % (main, major, minor, other))
				self.ui.pushUpdate.setEnabled(True)
		except:
			self.ui.label.setText("Image not valid")
			self.ui.pushUpdate.setEnabled(False)
			pass

	def handleAddCommand(self):
		command_text = self.ui.lineCommand.text()
		if "" != command_text:
			newItem = QListWidgetItem(command_text);
			self.ui.listCommands.addItem(newItem)
			self.ui.listCommands.setCurrentItem(newItem)
			self.ui.lineCommand.setText("")

	def handleDelCommand(self):
		for item in self.ui.listCommands.selectedItems():
			self.ui.listCommands.takeItem(self.ui.listCommands.row(item))
		
	def handleUpdate(self):
		self.ui.progressUpdate.setProperty("value", 0)
		self.updateprogress = 0
		try:
			self.filesize = os.path.getsize(self.updatefile)
			with open(self.updatefile, 'rb') as infile:
				client = tftpy.TftpClient('::1', 69)
				client.upload("update2.bin", infile, packethook=self.tftp_hook)
			self.ui.progressUpdate.setEnabled(True)
		except:
			raise
	def tftp_hook(self, dat):
		searchObj = re.search( r'.*data: (.*?) bytes.*?', str(dat), re.M|re.I)

		if searchObj:
			self.updateprogress += int(searchObj.group(1))
			self.ui.progressUpdate.setProperty("value", self.updateprogress * 100 / self.filesize )
		
	def handleAddParameter(self):
		parameter_text = self.ui.lineParameter.text()
		if "" != parameter_text:
			newItem = QListWidgetItem(parameter_text);
			self.ui.listParameter.addItem(newItem)
			self.ui.listParameter.setCurrentItem(newItem)
			self.ui.lineParameter.setText("")
			
	def handleDelParameter(self):
		for item in self.ui.listParameter.selectedItems():
			self.ui.listParameter.takeItem(self.ui.listParameter.row(item))

	def handleCommandSelectionChanged(self):
		self.Command = ""
		items = self.ui.listCommands.selectedItems()
		if 1 == len(items):
			self.Command = items[0].text()

		items = self.ui.listParameter.selectedItems()
		if 1 == len(items):
			self.Command = self.Command.replace("<#>", items[0].text())
		
		self.ui.labelCommand.setText(self.Command)

	def handleParameterSelectionChanged(self):
		self.Command = ""
		items = self.ui.listCommands.selectedItems()
		if 1 == len(items):
			self.Command = items[0].text()

		items = self.ui.listParameter.selectedItems()
		if 1 == len(items):
			self.Command = self.Command.replace("<#>", items[0].text())
		
		self.ui.labelCommand.setText(self.Command)

	def handleExecute(self):
		for item in self.ui.listServices.selectedItems():
			print("send %r to %r" % (self.Command, item.text()))

app = QApplication(sys.argv)
window = QDialog()
ui = Ui_Fiallo()
ui.setupUi(window)

uih = UIHandler(ui)

ui.listServices.addItem("test")

ui.listCommands.addItem('{"device":{"identity":{"version":<#>}}}')

ui.pushBrowse.clicked.connect(uih.handleBrowse)
ui.pushUpdate.clicked.connect(uih.handleUpdate)

ui.pushAddCommand.clicked.connect(uih.handleAddCommand)
ui.pushDelCommand.clicked.connect(uih.handleDelCommand)
ui.pushAddParameter.clicked.connect(uih.handleAddParameter)
ui.pushDelParameter.clicked.connect(uih.handleDelParameter)
ui.pushExecute.clicked.connect(uih.handleExecute)

ui.listCommands.itemSelectionChanged.connect(uih.handleCommandSelectionChanged)
ui.listParameter.itemSelectionChanged.connect(uih.handleParameterSelectionChanged)

window.show()
sys.exit(app.exec_())
