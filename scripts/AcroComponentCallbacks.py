from TDStoreTools import StorageManager
TDF = op.TDModules.mod.TDFunctions

class AcroComponentCallbacks:
	"""
	AcroComponentCallbacks description
	"""
	def __init__(self, ownerComp):
		# The component to which this extension is attached
		self.ownerComp = ownerComp

	def generateScript(self):
		selected_comp = self.ownerComp.par.Selected.eval()
		c = selected_comp.copy(self.ownerComp.op('defaultCallbacks'))
		c.name = 'callbacks'
		selected_comp.copy(self.ownerComp.op('CallbacksExt'))

		if not hasattr(selected_comp.par, 'Callbackdat'):
			a = ui.messageBox(
				'Add parameters',
				'Add callback parameters?',
				buttons=['Yes', 'No']
			)
			if a == 0:
				p = selected_comp.appendCustomPage('Callbacks')
				p.appendDAT('Callbackdat', label='Callback DAT')
				p.appendPulse('Editcallbackdat', label='Edit Callback DAT')
				p.appendToggle('Printcallbacks', label='Print Callbacks')

				selected_comp.par.Callbackdat = './callbacks'
				selected_comp.op('callbacks').par.edit.expr = 'parent().par.Editcallbackdat'

		a = ui.messageBox(
			'Copy Example',
			'Copy callbacks extension example?',
			buttons=['Yes', 'No']
			)
		if a == 0:
			selected_comp.copy(self.ownerComp.op('ExampleCallbacksExtension'))


	def editScript(self):
		selected_comp = self.ownerComp.par.Selected.eval()
		if selected_comp.op('callbacks'):
				selected_comp.op('callbacks').par.edit.pulse()

	def saveScript(self):
		selected_comp = self.ownerComp.par.Selected.eval()
		if selected_comp.op('callbacks'):
			print('saved')