"""
Extension classes enhance TouchDesigner components with python. An
extension is accessed via ext.ExtensionClassName from any operator
within the extended component. If the extension is promoted via its
Promote Extension parameter, all its attributes with capitalized names
can be accessed externally, e.g. op('yourComp').PromotedFunction().

Help: search "Extensions" in wiki
"""

from TDStoreTools import StorageManager
TDF = op.TDModules.mod.TDFunctions

class AcroComponentSelectorRelative:
	"""
	AcroComponentSelectorRelative description
	"""
	def __init__(self, ownerComp):
		# The component to which this extension is attached
		self.ownerComp = ownerComp
		
		storedItems = [
			# Only 'name' is required...
			{'name': 'BindID', 'default': None, 'dependable': True},
		]
		# Uncomment the line below to store StoredProperty. To clear stored
		# 	items, use the Storage section of the Component Editor
		
		self.stored = StorageManager(self, ownerComp, storedItems)

	def BindSelected(self):
		target = self.ownerComp.par.selectpanel.eval()
		p = target.relativePath(self.ownerComp)
	
		target.par.w.mode = ParMode.EXPRESSION
		target.par.h.mode = ParMode.EXPRESSION
		target.par.w.expr = 'op(\'' + p + '\').width'
		target.par.h.expr = 'op(\'' + p + '\').height'

		self.stored['BindID'] = self.ownerComp.id
		pass

	# def UpdateComponents(self):
	# 	l = []
	# 	for comp in op.AW.Components:
	# 		if op.comps.op(comp).type != 'base':
	# 			l.append(comp)
	# 	self.ownerComp.par.Component.menuNames = l
	# 	self.ownerComp.par.Component.menuLabels = l
	# 	pass

	def onCreate(self):
		target = self.ownerComp.par.selectpanel.eval()

		#debug('onCreate')

		if self.stored['BindID'] is not None:
			if target.par.w.expr == 'op(' + str(self.stored['BindID']) + ').width':
				self.BindSelected()
				
		# self.UpdateComponents()
		
	def onStart(self):
		# self.UpdateComponents()
		pass


	def par_Bindselected(self):
		self.BindSelected()
		pass

	def par_Updatecomponents(self):
		self.UpdateComponents()
		pass