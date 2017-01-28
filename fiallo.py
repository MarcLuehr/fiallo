import sys
from PyQt5.QtWidgets import QApplication, QDialog, QFileDialog, QListWidgetItem
from fialloui import Ui_Fiallo
import os
import re
import json
from os.path import expanduser
from zeroconf import ServiceBrowser, Zeroconf, ServiceInfo, ip_kind
import socket
import tftpy

class UIHandler():
	def __init__(self, ui):
		self.updatefile = ''
		self.ui = ui
		self.filesize = 0
		self.updateprogress = 0
		self.Command = ""
		self.commands_json = expanduser(".fiallo/commands.json")
		self.commands = {}
		try:
			with open(self.commands_json, 'r') as infile:
				self.commands = json.load(infile)
		except:
			pass
		
		self.updateCommands()
		
		self.ui.listParameter.setCurrentRow(0)
		self.ui.listCommands.setCurrentRow(0)
		
		self.handleCommandSelectionChanged()
		
	def updateCommands(self):
		ui.listCommands.clear()
		for command in self.commands.keys():
			ui.listCommands.addItem(command)
		self.reloadParameter(self.ui.listCommands.selectedItems())
	
	def saveCommands(self):
		os.makedirs(os.path.dirname(self.commands_json), exist_ok=True)
		with open(self.commands_json, 'w') as outfile:
			outfile.write(json.dumps(self.commands))
	
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
			self.commands[command_text] = ['null']
			self.updateCommands()
			self.ui.lineCommand.setText("")
			self.saveCommands()

	def handleDelCommand(self):
		items = self.ui.listCommands.selectedItems()
		if 1 == len(items):
			del self.commands[items[0].text()]
			self.updateCommands()
			self.saveCommands()
		
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
	
	def reloadParameter(self, commands):
		self.ui.listParameter.clear()
		if 1 == len(commands):
			for parameter in self.commands[commands[0].text()]:
				self.ui.listParameter.addItem(parameter)		
		
	
	def handleAddParameter(self):
		parameter_text = self.ui.lineParameter.text()
		command_items = self.ui.listCommands.selectedItems()
		if "" != parameter_text and 1 == len(command_items):
			items = self.ui.listCommands.selectedItems()
			self.commands[command_items[0].text()].append(parameter_text)
			newItem = QListWidgetItem(parameter_text)
			self.ui.listParameter.addItem(newItem)
			self.ui.listParameter.setCurrentItem(newItem)
			self.ui.lineParameter.setText("")
			self.saveCommands()
			
	def handleDelParameter(self):
		items = self.ui.listParameter.selectedItems()
		if 1 == len(items):
			command_items = self.ui.listCommands.selectedItems()
			del self.commands[command_items[0].text()][self.ui.listParameter.row(items[0])]
			self.ui.listParameter.takeItem(self.ui.listParameter.row(items[0]))
			self.saveCommands()
		

	def handleCommandSelectionChanged(self):
		self.Command = ""
		items = self.ui.listCommands.selectedItems()
		
		self.reloadParameter(items)
		
		if 1 == len(items):

			self.ui.listParameter.setCurrentRow(0)
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

class telnet():
	def __init__(self):
		pass
		
	def open_connection(ip6address, interface):
		s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)

		res = socket.getaddrinfo(ip6address + '%' + interface, 45, socket.AF_INET6, socket.SOCK_STREAM)
		family, socktype, proto, canonname, sockaddr = res[0]
		print(sockaddr)
		s.connect(sockaddr)
		
		print ("client opened socket connection:", s.getsockname())
		
		return s

	def send_command(socket, command):
		data = command + '\r\n'
		print ('Client is sending:', repr(data))
		socket.send(data.encode())
		data = socket.recv(1024).decode()
		print ('Client received response:', repr(data))

class MyListener(object):

    def remove_service(self, zeroconf, type, name):
        print("Service %s removed" % (name,))

    def add_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        print("Service %s added, service info: %s" % (name, info))
        if None != info:
            if 4 == ip_kind(info.address):
                print("Address %s" % socket.inet_ntop(socket.AF_INET, info.address))
            elif 6 == ip_kind(info.address):
                print("Address %s" % socket.inet_ntop(socket.AF_INET6, info.address))
            print("Interface %s" % info.interface)


zeroconf = Zeroconf()
listener = MyListener()
serviceName = "_telnet"
browser = ServiceBrowser(zeroconf, serviceName + "._tcp.local.", listener)

app = QApplication(sys.argv)
window = QDialog()
ui = Ui_Fiallo()
ui.setupUi(window)

uih = UIHandler(ui)

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
