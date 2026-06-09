"""
Open(items=None, callback=None, callbackDetails=None, disabledItems=None, dividersAfterItems=None, checkedItems=None, subMenuItems=None, autoClose=None, rolloverCallback=None)

Opens the menu. Usually, a call to this method and a callback (provided in argument here or defined in Callback DAT) is all that is needed to use popMenu. Arguments set to None will use the values set in the popMenu's parameters.
items - a list of item strings for the menu. If this is None or not provided, the default is to use the Items set up in parameters. If provided, these options will replace the ones in the Items parameter, and other Item parameters will be ignored (e.g. Disabled Items).
callback - a method that will be called when a selection is made.
callbackDetails - will be passed to callbacks in addition to item chosen.
disabledItems - list of strings for greyed out, unselectable items.
dividersAfterItems - list of strings for items with dividers below them.
checkedItems - list of strings for items with check marks next to them. Will show the 'check' graphic in configComp. Also accepts a dict of strings with 'item': bool. Will show the 'checkOn' or 'checkOff' graphic depending on bool. Also accepts a string which will be used as an EXPRESSION to continually evaluate.
subMenuItems - list of strings for items with indicator and will select on rollOver instead of click. Always use OpenSubMenu in handler function. Set SubMenu parameter to another popMenu comp. Default is []... no parameter available for submenus.
autoClose - will close after selection or click away.
rolloverCallback - will be called when a cell is rolledOver. A callback with cell -1 will be called when mouse leaves menu or menu closes. Uses same callbackDetails as selection callback.
OpenSubMenu(items=None, callback=None, callbackDetails=None, disabledItems=None, dividersAfterItems=None, checkedItems=None, subMenuItems=None, autoClose=None, rolloverCallback=None)

Opens the menu's sub-menu. All arguments are exactly as in the Open method above. For all sub-menu items, this method must be called from the selection callback.
SetPlacement(hAlign='Left', vAlign='Top', alignOffset=(0,0), buttonComp=None, hAttach='Left', vAttach='Bottom', matchWidth=False)

Set up placement parameters for the popMenu. This is a convenience function for reusing popMenu as a dropdown menu in multiple places
hAlign - set Horizontal Align.
vAlign - set Vertical Align.
alignOffset - set Align Offset.
buttonComp - set Button COMP.
hAttach - set Horizontal Attach.
vAttach - set Vertical Attach.
matchWidth - True = match width of menu to width of button Comp, False = optimal width, number = specific width.
Close()

Close the menu. The selection callback will not be called.
OnSelect(cell, doautoClose=True)

Simulates a click of the provided cell.
cell - the cell number to simulate a click on.
doautoClose - (Optional) if False, skip all auto close functionality.
"""

from TDStoreTools import StorageManager
TDF = op.TDModules.mod.TDFunctions
from pprint import pprint

class AcroDropList:
	"""
	AcroDropList description
	"""
	def __init__(self, ownerComp):
		# The component to which this extension is attached
		self.ownerComp = ownerComp
		self.popMenu = op.TDResources.PopMenu

	def onSelectCallback(self, info):
		#pprint(info)
		# 'getattr(parent.DLSLS.par.Op.eval(), parent.DLSLS.par.Key.eval())[parent.DLSLS.par.Item.eval()]'
		# + parent.DLSLS.par.Accessor.eval() + ' = args[0]'
		# index = info['index']
		# item = info['item']

		# cmd = 'getattr(self.ownerComp.par.Op.eval(), self.ownerComp.par.Key.eval())'
		# cmd += '[self.ownerComp.par.Item.eval()]'
		# cmd += self.ownerComp.par.Accessor.eval()
		# cmd += ' = \'' + item + '\''
		# print(cmd)

		# eval(cmd)

		#setattr(o, self.ownerComp.par.Accessor.eval(), item)

		self.ownerComp.op('updateValue').run(info['item'])


	def OpenList(self):
		#print(type(self.ownerComp.par.Listitems.eval()))
		self.popMenu.Open(
			items=self.ownerComp.par.Listitems.eval(),
			callback=self.onSelectCallback,
			callbackDetails=None,
			disabledItems=None,
			dividersAfterItems=None,
			checkedItems=None,
			subMenuItems=None,
			autoClose=None,
			rolloverCallback=None
		)
