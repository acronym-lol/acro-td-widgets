from TdStoreTools import StorageManager

EMPTY_WIDGET = {'folder': 'ui', 'widget': 'empty'}


class AcroWidgetContainer:

    def __init__(self, ownerComp):
        self.ownerComp = ownerComp
        self.DataComp = ownerComp.op('data')
        self.WidgetsComp = op.AW.op('widgets')
        self.AcroWidgetContainerSettingsComp = op.AW.op('widgetContainerSettings')
        self.WidgetSettingsComp = op.AW.op('widgetSettings')
        self.popMenu = op.TDResources.PopMenu

        storedItems = [
            {'name':'SelectedWidget','default': EMPTY_WIDGET.copy()},
            {'name':'Selected','default':False},
            {'name':'Drag','default':False},
            {'name':'Drop','default':False}
        ]
        self.stored = StorageManager(self, self.DataComp, storedItems)

        self.UpdateSelectedWidget()

    # -------------------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------------------

    def _isEmptyWidget(self, comp):
        """Check if a widget container holds the empty widget."""
        return comp.SelectedWidget == EMPTY_WIDGET

    def _addUndoSelectCallback(self, comp):
        """Register an undo callback to restore comp's current SelectedWidget."""
        ui.undo.addCallback(
            self._undoSelectWidget,
            {'from_op': comp.path, 'selected': comp.SelectedWidget.copy()}
        )

    def _replaceWidget(self, source_op):
        """Replace this container's widget with source_op's widget. Registers undo."""
        source_widgets = source_op.findChildren(tags=['widget'], depth=1)
        if not source_widgets or self._isEmptyWidget(source_op):
            return False
        widgets = self.ownerComp.findChildren(tags=['widget'], depth=1)
        self.ownerComp.copy(source_widgets[0])
        for w in widgets:
            w.destroy()
        self._addUndoSelectCallback(self.ownerComp)
        self.stored['SelectedWidget'] = {
            'folder': source_op.SelectedWidget['folder'],
            'widget': source_op.SelectedWidget['widget']
        }
        return True

    def _clearSourceWidget(self, source_op):
        """Clear the source container's widget (for move/cut). Registers undo."""
        source_widgets = source_op.findChildren(tags=['widget'], depth=1)
        for w in source_widgets:
            w.destroy()
        self._addUndoSelectCallback(source_op)
        source_op.ext.AcroWidgetContainer._SelectWidget('ui', 'empty')

    def _swapWidgets(self, source_op):
        """Swap widgets between this container and source_op. Registers undo."""
        widgets = self.ownerComp.findChildren(tags=['widget'], depth=1)
        source_widgets = source_op.findChildren(tags=['widget'], depth=1)
        if not source_widgets or self._isEmptyWidget(source_op):
            return

        self.ownerComp.copy(source_widgets[0])
        source_op.copy(widgets[0])

        for w in source_widgets:
            w.destroy()
        for w in widgets:
            w.destroy()

        owner_sel = self.stored['SelectedWidget'].copy()
        source_sel = source_op.SelectedWidget.copy()

        self._addUndoSelectCallback(self.ownerComp)
        self.stored['SelectedWidget'] = {
            'folder': source_sel['folder'],
            'widget': source_sel['widget']
        }

        self._addUndoSelectCallback(source_op)
        source_op.SelectedWidget = {
            'folder': owner_sel['folder'],
            'widget': owner_sel['widget']
        }

    def _transferWidget(self, source_op, is_move):
        """Core logic shared by Paste and OnDrop.

        Caller must wrap in ui.undo.startBlock/endBlock.

        Args:
            source_op: The widget container to transfer from.
            is_move: If True, clears the source after transfer.
        """
        source_widgets = source_op.findChildren(tags=['widget'], depth=1)
        if not source_widgets:
            return

        widgets = self.ownerComp.findChildren(tags=['widget'], depth=1)
        if not widgets:
            return

        if self._isEmptyWidget(self.ownerComp):
            if self._replaceWidget(source_op) and is_move:
                self._clearSourceWidget(source_op)
        else:
            if self._isEmptyWidget(source_op):
                return

            can_swap = (self.ownerComp.path not in source_op.path
                        and not is_move)
            if can_swap:
                answer = ui.messageBox('Widget Conflict',
                    'Widget container occupied. Select verdict:',
                    buttons=['Replace', 'Swap', 'Cancel'])
            else:
                answer = ui.messageBox('Widget Conflict',
                    'Widget container occupied. Select verdict:',
                    buttons=['Replace', 'Cancel'])

            if answer == 0:
                if self._replaceWidget(source_op) and is_move:
                    self._clearSourceWidget(source_op)
            elif answer == 1 and can_swap:
                self._swapWidgets(source_op)

    def _pulseBasicWidgets(self):
        """Pulse enablecloning on any TDBasicWidget children."""
        widgets = self.ownerComp.findChildren(tags=['widget'], depth=1)
        for w in widgets:
            if 'TDBasicWidget' in w.tags:
                w.par.enablecloningpulse.pulse()

    # -------------------------------------------------------------------------
    # Widget selection
    # -------------------------------------------------------------------------

    def UpdateSelectedWidget(self):
        widgets = self.ownerComp.findChildren(tags=['widget'], depth=1)

        if len(widgets) > 0:
            master = widgets[0].par.clone.eval()
            if op(master) != None:
                folder = op(master).parent().name
                widget = op(master).name
                self.stored['SelectedWidget'] = {'folder': folder, 'widget': widget}

    def SelectWidget(self, folder, widget):
        ui.undo.startBlock('select widget')
        self._SelectWidget(folder, widget)
        selected_widget = self.stored['SelectedWidget'].copy()
        ui.undo.addCallback(self._undoSelectWidget, selected_widget)
        ui.undo.endBlock()

    def _SelectWidget(self, folder, widget):
        self.stored['SelectedWidget'] = {
            'folder': folder,
            'widget': widget
        }
        self._ReloadWidget()

    def _undoSelectWidget(self, isUndo, info):
        from_op = info['from_op']
        selected = info['selected']
        op(from_op).SelectedWidget = selected

    # -------------------------------------------------------------------------
    # Right-click menu callbacks
    # -------------------------------------------------------------------------

    def onSelectCallback(self, info):
        if info['item'] == 'Create Widget':
            widgetFolders = sorted(op.AW.Widgets.keys())
            info['menu'].OpenSubMenu(
                items=widgetFolders,
                callback=self.onFolderSelectCallback,
                callbackDetails={
                    'level': 'folder',
                    'container': self.ownerComp.path
                },
                subMenuItems=widgetFolders,
            )
            return

        cmds = [
            self.OpenAcroWidgetContainerSettings,
            self.Copy,
            self.Cut,
            self.Paste,
            self.Delete,
            self.Save,
            self.Load
        ]
        cmd_index = info['index'] - 1
        if 0 <= cmd_index < len(cmds):
            cmds[cmd_index]()

    def onFolderSelectCallback(self, info):
        """Handle folder selection - opens widget list submenu."""
        folder = info['item']
        widgets = list(op.AW.Widgets[folder]['widgets'].keys())

        info['menu'].OpenSubMenu(
            items=widgets,
            callback=self.onWidgetSelectCallback,
            callbackDetails={
                'folder': folder,
            },
        )

    def onWidgetSelectCallback(self, info):
        """Handle widget selection - creates the widget."""
        widget = info['item']
        # Look up which folder contains this widget
        folder = None
        for f, data in op.AW.Widgets.items():
            if widget in data['widgets']:
                folder = f
                break
        if folder is None:
            return

        if self.stored['SelectedWidget'] == EMPTY_WIDGET:
            self.SelectWidget(folder, widget)
        else:
            answer = ui.messageBox(
                'Widget Overwrite Warning',
                'Are you sure you want to overwrite the current widget?',
                buttons=['Yes', 'No']
            )
            if answer == 0:
                self.SelectWidget(folder, widget)

    def OpenRClickMenu(self):
        if op.AW.par.Enableedit:
            self.stored['Selected'] = True
            op.AW.SelectedWidgetContainer = self.ownerComp.path
            self.popMenu.Open(
                items=['Create Widget', 'Open Settings', 'Copy', 'Cut', 'Paste', 'Delete', 'Save', 'Load'],
                callback=self.onSelectCallback,
                callbackDetails=None,
                disabledItems=None,
                dividersAfterItems=['Create Widget'],
                checkedItems=None,
                subMenuItems=['Create Widget'],
                autoClose=None,
                rolloverCallback=None
            )

    # -------------------------------------------------------------------------
    # Clipboard operations
    # -------------------------------------------------------------------------

    def Copy(self):
        op.AW.Copy['path'] = self.ownerComp.path
        op.AW.Copy['isCut'] = False

    def _undoCopy(self, isUndo, info):
        op.AW.Copy = info

    def Cut(self):
        op.AW.Copy['path'] = self.ownerComp.path
        op.AW.Copy['isCut'] = True

    def Paste(self):
        if op.AW.Copy['path'] is None:
            return
        copy_op = op(op.AW.Copy['path'])

        if 'widgetcontainer' not in copy_op.tags:
            ui.messageBox('Widget Paste Warning',
                'Pasted item is not a widget container', buttons=['Ok'])
            return

        if copy_op.path in self.ownerComp.parent().path:
            ui.messageBox('Widget Paste Warning',
                "Can't paste widget inside itself.", buttons=['Ok'])
            return

        is_move = op.AW.Copy['isCut']
        ui.undo.startBlock('paste widget')
        self._transferWidget(copy_op, is_move)
        if is_move:
            ui.undo.addCallback(self._undoCopy, op.AW.Copy.getRaw())
            op.AW.Copy['path'] = self.ownerComp.path
            op.AW.Copy['isCut'] = False
        ui.undo.endBlock()

    def Delete(self):
        ui.undo.startBlock('delete widget')
        self._addUndoSelectCallback(self.ownerComp)
        self._SelectWidget('ui', 'empty')
        if op.AW.Copy['path'] == self.ownerComp.path:
            ui.undo.addCallback(self._undoCopy, op.AW.Copy.getRaw())
            op.AW.Copy['path'] = None
            op.AW.Copy['isCut'] = False
        ui.undo.endBlock()

    # -------------------------------------------------------------------------
    # Save / Load
    # -------------------------------------------------------------------------

    def Save(self):
        p = ui.chooseFile(load=False, fileTypes=['tox'])
        if p:
            self.stored['Selected'] = False
            self.ownerComp.save(p)

    def Load(self):
        p = ui.chooseFile(fileTypes=['tox'])
        if p:
            self.ownerComp.par.externaltox = p
            self.ownerComp.par.reinitnet.pulse()
            self.ownerComp.par.reloadtoxonstart = False

    # -------------------------------------------------------------------------
    # Settings panels
    # -------------------------------------------------------------------------

    def OpenAcroWidgetContainerSettings(self):
        if op(self.AcroWidgetContainerSettingsComp.par.Widget) is not None:
            if op(self.AcroWidgetContainerSettingsComp.par.Widget).path != self.ownerComp.path:
                if hasattr(op(self.AcroWidgetContainerSettingsComp.par.Widget), 'Selected'):
                    op(self.AcroWidgetContainerSettingsComp.par.Widget).Selected = False

        self.stored['Selected'] = True
        self.AcroWidgetContainerSettingsComp.par.Widget = self.ownerComp.path
        try:
            if self.AcroWidgetContainerSettingsComp.panel.winopen == 0:
                self.AcroWidgetContainerSettingsComp.openViewer(borders=False, unique=True)
        except:
            pass

    def OpenWidgetSettings(self):
        if op(self.WidgetSettingsComp.par.Widget) != self.ownerComp.path:
            op(self.WidgetSettingsComp.par.Widget).Selected = False
        self.stored['Selected'] = True
        self.WidgetSettingsComp.par.Widget = self.ownerComp.op(self.stored['SelectedWidget']['widget']).path
        self.WidgetSettingsComp.closeViewer()
        self.WidgetSettingsComp.openViewer(borders=False, unique=True)

    # -------------------------------------------------------------------------
    # Lifecycle
    # -------------------------------------------------------------------------

    def OnCreate(self):
        self.UpdateSelectedWidget()

        if self.stored['SelectedWidget'] == EMPTY_WIDGET:
            if op.AW.path not in self.ownerComp.path:
                self._ReloadWidget()

        self._pulseBasicWidgets()

    def OnStart(self):
        self.UpdateSelectedWidget()
        self._pulseBasicWidgets()

    def ReloadWidget(self):
        ui.undo.startBlock('reload widget')
        self._ReloadWidget()
        ui.undo.endBlock()

    def _ReloadWidget(self):
        widgets = self.ownerComp.findChildren(tags=['widget'], depth=1)
        for w in widgets:
            w.destroy()

        folder = self.stored['SelectedWidget']['folder']
        widget = self.stored['SelectedWidget']['widget']

        master_widget = op(op.AW.Widgets[folder]['path']).op(widget)

        try:
            widgetOp = self.ownerComp.copy(master_widget)

            widgetOp.tags.add('widget')

            widgetOp.par.hmode = 1
            widgetOp.par.vmode = 1
            widgetOp.par.alignorder = 1
            widgetOp.par.alignallow = 0

            widgetOp.par.enablecloning = True
            widgetOp.cloneImmune = True
            widgetOp.nodeX = 0
            widgetOp.nodeY = 0

        except Exception as e:
            debug('failed to load widget')
            debug(e)

    # -------------------------------------------------------------------------
    # Drag and drop
    # -------------------------------------------------------------------------

    def OnDrag(self, args):
        return

    def OnDrop(self, args):
        if args[5] != 'COMP':
            ui.messageBox('Widget Drop Warning',
                'Dropped item is not a COMP', buttons=['Ok'])
            return

        drag_op = op(args[6] + '/' + args[0]).parent()

        if 'widgetcontainer' not in drag_op.tags:
            ui.messageBox('Widget Drop Warning',
                'Dropped item is not a widget container', buttons=['Ok'])
            return

        if drag_op.path in self.ownerComp.parent().path:
            ui.messageBox('Widget Drop Warning',
                "Can't move widget inside itself.", buttons=['Ok'])
            return

        is_move = not op.AW.Modifiers['ctrl']
        ui.undo.startBlock('drop widget')
        self._transferWidget(drag_op, is_move)
        ui.undo.endBlock()
