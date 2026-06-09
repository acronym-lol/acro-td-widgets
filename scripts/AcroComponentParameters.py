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

class AcroComponentParameters:

	def __init__(self, ownerComp):
		# The component to which this extension is attached
		self.ownerComp = ownerComp

	# do something in the future
	def _futureFrames(self, attrib, args, group_name, delayFrames):
		self.ownerComp.op('future').run(attrib, args, group=group_name, delayFrames=delayFrames)

	def UpdateComponents(self):
		self._futureFrames('updateComponents', (), str(self.ownerComp.id), 1)

	def updateComponents(self):
		l = []
		for comp in op.AW.Components:
			l.append(comp)
		self.ownerComp.par.Component.menuNames = l
		self.ownerComp.par.Component.menuLabels = l
		pass

	def onCreate(self):	
		self.UpdateComponents()
		
	def onStart(self):
		self.UpdateComponents()


	def par_Refreshcomponentslist(self):
		self.UpdateComponents()
		pass