from json import loads, dumps
import traceback

from CallbacksExt import CallbacksExt
from TDStoreTools import StorageManager
TDF = op.TDModules.mod.TDFunctions

class AcroPopWin(CallbacksExt):
    """ A component used to open a window at the mouse location """

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

        

        self.windowComp = ownerComp.op('window')

        # the component to which data is stored
        self.dataComp = ownerComp.op('data')

        # stored items (persistent across saves and re-initialization):
        storedItems = [
            # Only 'name' is required...
            {'name': 'Data', 'default': None, 'readOnly': False,
                                     'property': True, 'dependable': True},
        ]
        self.stored = StorageManager(self, self.dataComp, storedItems)

    def Open(self, comp, horiz='right', vert='bottom', offsetx=0, offsety=0):
        # if open, close
        if self.windowComp.isOpen:
            self.windowComp.par.winclose.pulse()

        self.windowComp.par.winop = comp.path

        h_offset = offsetx
        v_offset = offsety
        if horiz == 'right':
            h_offset += comp.width/2
        elif horiz == 'left':
            h_offset -= comp.width/2

        if vert == 'top':
            v_offset += comp.height/2
        elif vert == 'bottom':
            v_offset -= comp.height/2

        self.windowComp.par.winoffsetx = h_offset
        self.windowComp.par.winoffsety = v_offset
        self.windowComp.par.winopen.pulse()
        return
    
    def onLoseFocus(self):
        self.windowComp.par.winclose.pulse()
        return
    
    def open(self):
        return

    # pulse parameter to open extension
    def pulse_Editextension(self):
        self.ownerComp.op('AcroPopWin').par.edit.pulse()
