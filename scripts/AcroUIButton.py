from json import loads, dumps
import traceback

from CallbacksExt import CallbacksExt
from TDStoreTools import StorageManager
TDF = op.TDModules.mod.TDFunctions

class AcroUIButton(CallbacksExt):
    """ McWidget UI Button """

    def __init__(self, ownerComp):
        # the component to which this extension is attached
        self.ownerComp = ownerComp

        # init callbacks
        self.callbackDat = self.ownerComp.par.Callbackdat.eval()
        try:
            CallbacksExt.__init__(self, ownerComp)
        except:
            self.ownerComp.addScriptError(traceback.format_exc() + \
                    "Error in CallbacksExt __init__. See textport.")
            print()
            print("Error initializing callbacks - " + self.ownerComp.path)
            print(traceback.format_exc())
        # run onInit callback
        try:
            self.DoCallback('onInit', {'ownerComp':self.ownerComp})
        except:
            self.ownerComp.addScriptError(traceback.format_exc() + \
                    "Error in custom onInit callback. See textport.")
            print(traceback.format_exc())



        # the component to which data is stored
        self.dataComp = ownerComp.op('data')

        # stored items (persistent across saves and re-initialization):
        storedItems = [
            # Only 'name' is required...
            {'name': 'State', 'default': False, 'readOnly': False,
                                     'property': True, 'dependable': True},
            {'name': 'Over', 'default': False, 'readOnly': False,
                                     'property': True, 'dependable': True},
        ]
        self.stored = StorageManager(self, self.dataComp, storedItems)


    def onClick(self, panelValue):
        button_type = self.ownerComp.par.Buttontype.eval()
        if panelValue.name == 'lselect':
            value = panelValue.val
            
            # momentary button
            if button_type == 'momentary':
                if value:
                    self.setState(True)
                    self.runScript()
                else:
                    self.setState(False)
            
            # toggle button
            elif button_type == 'toggle':
                if value:
                    self.runScript()
                    self.setState(not self.stored['State'])
            
            # pulse button
            elif button_type == 'pulse':
                if value:
                    self.runScript()
                    self.setState(True)
                    run(self.setState, False, delayMilliSeconds=100)
        
        elif panelValue.name == 'mselect':
            # open widget settings for this button
            op.AWWS.par.Widget = self.ownerComp.path
            op.AWWS.openViewer(borders=False)


        self.DoCallback(
            'onClick', 
            {
                'ownerComp':self.ownerComp,
                'panelValue':panelValue
            }
        )

    def setState(self, value):
        self.stored['State'] = value
        self.DoCallback('onState', {'ownerComp':self.ownerComp})

    def runScript(self):
        run(self.ownerComp.par.Script.eval(), fromOP=self.ownerComp, asParameter=True)
        

    def onOver(self, value):
        self.stored['Over'] = value
        self.DoCallback('onOver', {'ownerComp':self.ownerComp})
        

    def pulse_Iconsearch(self):
        ui.viewFile('https://pictogrammers.com/library/mdi/')
        return

    # pulse parameter to open extension
    def pulse_Editextension(self):
        self.ownerComp.op('AcroUIButton').par.edit.pulse()

    # def pulse_Editcallbackdat(self):
    #     self.ownerComp.op('Callbacks').par.edit.pulse()
