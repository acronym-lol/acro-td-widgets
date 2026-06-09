import inspect
import re
import traceback
from ntpath import basename

from CallbacksExt import CallbacksExt
from TDStoreTools import StorageManager
from AcroVersionExt import AcroVersionExt


class AcroWidgets(CallbacksExt, AcroVersionExt):
    """
    AcroWidgets - Widget management system for TouchDesigner.

    Provides widget discovery, component inspection, and clipboard operations
    for building custom UIs.
    """

    # Sentinel: settings comps default to this when no widget is selected,
    # so their parameter expressions always resolve to a real op.
    EMPTY_WIDGET_PATH = '/AcroWidgets/widgets/ui/empty'

    def __init__(self, ownerComp):
        self.ownerComp = ownerComp
        self.dataComp = ownerComp.op('data')
        self.widgetsComp = ownerComp.op('widgets')

        # ---------------------------------------------------------------------
        # Initialize CallbacksExt
        # ---------------------------------------------------------------------
        self.callbackDat = self.ownerComp.par.Callbackdat.eval()
        try:
            CallbacksExt.__init__(self, ownerComp)
        except:
            self.ownerComp.addScriptError(traceback.format_exc() +
                    "Error in CallbacksExt __init__. See textport.")
            print()
            print("Error initializing callbacks - " + self.ownerComp.path)
            print(traceback.format_exc())

        # Run onInit callback
        try:
            self.DoCallback('onInit', {'ownerComp': self.ownerComp})
        except:
            self.ownerComp.addScriptError(traceback.format_exc() +
                    "Error in custom onInit callback. See textport.")
            print(traceback.format_exc())

        # ---------------------------------------------------------------------
        # Initialize AcroVersionExt (creates Version parameter page)
        # ---------------------------------------------------------------------
        AcroVersionExt.__init__(self, ownerComp)

        # ---------------------------------------------------------------------
        # Storage setup
        # ---------------------------------------------------------------------
        storedItems = [
            {'name': 'Widgets', 'default': {}, 'dependable': True},
            {'name': 'Modifiers', 'default': {
                'ctrl': False,
                'alt': False,
                'shift': False,
            }, 'dependable': True},
            {'name': 'Components', 'default': [], 'dependable': True},
            {'name': 'ComponentsPath', 'default': '', 'dependable': False},
            {'name': 'SelectedComponent', 'default': {
                'index': 0,
                'name': '',
                'path': '',
                'parameters': [],
                'classes': [],
                # 4 empty slots so ext0..ext3 lookups never IndexError
                'extPaths': ['', '', '', ''],
            }, 'dependable': True},
            {'name': 'ComponentExts', 'default': [], 'dependable': True},
            {'name': 'ComponentParams', 'default': [], 'dependable': True},
            {'name': 'Copy', 'default': {
                'path': None,
                'isCut': False,
            }, 'dependable': True},
            {'name': 'SelectedWidgetContainer', 'default': None},
        ]
        self.stored = StorageManager(self, self.dataComp, storedItems)

        # Initialize components path from parameter
        self._initComponentsPath()

        # Update widget registry
        self.UpdateWidgets()

        # Reset stale Widget pars + SelectedComponent so dependent expressions
        # never see None / empty lists at startup
        self.EnsureValidSelections()

    # -------------------------------------------------------------------------
    # Public methods (Uppercase = promoted via ext0promote)
    # -------------------------------------------------------------------------

    def EnsureValidSelections(self):
        """Guarantee a safe initial state for downstream parameter expressions.

        - op.AWWS.par.Widget (widgetSettings) and op.AWWCS.par.Widget
          (widgetContainerSettings) get reset to EMPTY_WIDGET_PATH whenever
          the saved value doesn't resolve to a real op.
        - SelectedComponent['extPaths'] is padded so opviewer/extPaths[i]
          lookups can't IndexError.

        Safe to call any time. Wire to a parameterexecute DAT on the Widget
        pars to self-heal whenever a value is set to an invalid path.
        """
        for shortcut in ('AWWS', 'AWWCS'):
            comp = getattr(op, shortcut, None)
            if comp is None or not hasattr(comp.par, 'Widget'):
                continue
            current = comp.par.Widget.eval()
            if not current or op(current) is None:
                comp.par.Widget = self.EMPTY_WIDGET_PATH

        try:
            sel = self.stored['SelectedComponent']
            # DependDict supports dict-like access; copy via getRaw if available
            raw = sel.getRaw() if hasattr(sel, 'getRaw') else dict(sel)
            ext_paths = raw.get('extPaths') or []
            if len(ext_paths) < 4:
                raw['extPaths'] = list(ext_paths) + [''] * (4 - len(ext_paths))
                self.stored['SelectedComponent'] = raw
        except Exception as e:
            print('AcroWidgets._ensureValidSelections: SelectedComponent guard failed:', e)

    def _initComponentsPath(self):
        """Initialize components path from parameter if set."""
        comp_par = self.ownerComp.par.Components.eval()
        if comp_par:
            comp_op = op(comp_par)
            if comp_op:
                self.stored['ComponentsPath'] = comp_op.path

    def _getDefaultArg(self, args, defaults, arg_index):
        """Helper function for getting method argument defaults."""
        if not defaults:
            return None
        args_with_no_defaults = len(args) - len(defaults)
        if arg_index < args_with_no_defaults:
            return None
        else:
            value = defaults[arg_index - args_with_no_defaults]
            if isinstance(value, str):
                value = f'"{value}"'
            return value

    # -------------------------------------------------------------------------
    # Widgets
    # -------------------------------------------------------------------------

    def UpdateWidgets(self):
        """Discover and register all widgets in the scene.

        Searches for components tagged with 'widgetFolder' and catalogs
        their child widgets (tagged 'widget' or 'TDBasicWidget').

        Returns:
            dict: Widget data organized by folder.
        """
        widgets_data = {}

        widget_folders = op('/').findChildren(tags=['widgetFolder'])

        for f in widget_folders:
            widgets_data[f.name] = {
                'path': f.path
            }

            widgets_list = {}
            widgets = f.findChildren(tags=['widget', 'TDBasicWidget'], depth=1)

            for w in widgets:
                widget_data = {
                    'folder': f.name,
                    'tags': [t for t in w.tags],
                    'path': w.path
                }
                widgets_list[w.name] = widget_data

            widgets_data[f.name]['widgets'] = widgets_list

        # Refresh widget menu
        settings_comp = self.ownerComp.op('widgetContainerSettings')
        if settings_comp:
            menu_op = settings_comp.op('scriptWidgetsMenu')
            if menu_op:
                menu_op.par.Recreate.pulse()

        self.stored['Widgets'] = widgets_data
        return widgets_data

    def SearchWidgetsByTag(self, key, items):
        """Search widgets by tag.

        Args:
            key: Tag to search for.
            items: List of widget dicts to search.

        Returns:
            list: Widgets matching the tag.
        """
        return [element for element in items if key in element.get('name', '')]

    # -------------------------------------------------------------------------
    # Components
    # -------------------------------------------------------------------------

    def UpdateComponentsPath(self):
        """Update the stored components path from the parameter."""
        comp_par = self.ownerComp.par.Components.eval()
        if comp_par:
            comp_op = op(comp_par)
            if comp_op:
                self.stored['ComponentsPath'] = comp_op.path

    def UpdateComponents(self):
        """Update the list of available components."""
        comps = self.GetComponents()
        self.stored['Components'] = comps

    def GetComponents(self):
        """Get the list of available components."""
        components_path = self.stored['ComponentsPath']
        if not components_path:
            return

        parent_op = op(components_path)
        if not parent_op:
            return

        components = parent_op.findChildren(tags=['component'])
        comps = []
        for i in components:
            comps.append(i.path.replace('/components/', ''))

        comps = sorted(comps, key=lambda s: s.casefold())

        return comps

    def SelectComponent(self, component):
        """Select a component by index.

        Args:
            component: Index of the component to select.
        """
        components = self.stored['Components']
        if not components:
            return

        if component >= len(components):
            component = len(components) - 1

        self.stored['SelectedComponent']['index'] = component
        self.stored['SelectedComponent']['name'] = components[component]

        components_path = self.stored['ComponentsPath']
        if components_path:
            comp_op = op(components_path).op(components[component])
            if comp_op:
                self.stored['SelectedComponent']['path'] = comp_op.path

        self.UpdateComponent()

        # Fire callback
        self.DoCallback('onComponentSelect', {
            'ownerComp': self.ownerComp,
            'component': self.stored['SelectedComponent']
        })

    def OpenComponentsNetwork(self):
        """Open a floating network editor for the components folder."""
        components_path = self.stored['ComponentsPath']
        if components_path:
            pane = ui.panes.createFloating(type=PaneType.NETWORKEDITOR, name='Components')
            pane.owner = op(components_path)

    def OpenComponentNetwork(self):
        """Open a floating network editor for the selected component."""
        components_path = self.stored['ComponentsPath']
        selected = self.stored['SelectedComponent']
        components = self.stored['Components']

        if components_path and components:
            comp_op = op(components_path).op(components[selected['index']])
            if comp_op:
                pane = ui.panes.createFloating(type=PaneType.NETWORKEDITOR, name='Components')
                pane.owner = comp_op

    def ExportComponent(self):
        """Export the selected component to a .tox file."""
        selected = self.stored['SelectedComponent']
        if not selected['path']:
            return

        f = ui.chooseFile(load=False, start=None, fileTypes=['.tox'], title=None, asExpression=False)
        if f:
            comp_op = op(selected['path'])
            if comp_op:
                comp_op.save(f)

    def ImportComponent(self):
        """Import a component from a .tox file."""
        components_path = self.stored['ComponentsPath']
        if not components_path:
            return

        f = ui.chooseFile(load=True, start=None, fileTypes=['.tox'], title=None, asExpression=False)
        if f:
            parent_op = op(components_path)
            if parent_op:
                parent_op.loadTox(f, unwired=True)

    def UpdateComponent(self):
        """Update extension and parameter info for the selected component."""
        selected_path = self.stored['SelectedComponent']['path']
        if not selected_path:
            return

        component = op(selected_path)
        if not component:
            return

        # Get custom parameters
        pars = {}
        for p in component.customPars:
            pars[p.name] = {
                'name': p.name,
                'val': p.val,
                'label': p.label,
                'style': p.style
            }
        self.stored['SelectedComponent']['parameters'] = pars

        # Get extension paths
        self.stored['SelectedComponent']['extPaths'] = ['', '', '', '']
        for i in range(4):
            ext_par = component.par[f'ext{i}object'].eval()
            pattern = r"(?<=op\('\./)([^']+)"
            match = re.search(pattern, ext_par)
            if match:
                ext_path = selected_path + '/' + match.group(0)
                self.stored['SelectedComponent']['extPaths'][i] = ext_path

        # Get extension classes, methods, and attributes
        ext = component.extensions
        classes = []

        # Get inherited methods and attributes from CallbacksExt
        inherited_methods = dir(CallbacksExt)
        inherited_attributes = set(CallbacksExt.__dict__.keys())

        for c in ext:
            if c:
                myc = {
                    'name': c.__class__.__name__,
                    'methods': {},
                    'attributes': {}
                }

                # Get all public methods except __init__
                m = [method for method in dir(c) if inspect.ismethod(getattr(c, method, None))]

                for method_name in m:
                    if method_name != '__init__' and method_name[0].isupper() and method_name not in inherited_methods:
                        method_obj = getattr(c, method_name, None)
                        if method_obj:
                            fullargspec = inspect.getfullargspec(method_obj)
                            variables = list(fullargspec.args[1:])  # Exclude self

                            for idx in range(len(variables)):
                                default_arg = self._getDefaultArg(variables, fullargspec.defaults, idx)
                                if default_arg is not None:
                                    variables[idx] += f'={default_arg}'

                            strvars = ', '.join(map(str, variables))
                            funct = f'{method_name}({strvars})' if variables else f'{method_name}()'

                            myc['methods'][method_name] = {
                                'funct': funct,
                                'variables': variables
                            }

                # Get all public attributes that are NOT inherited
                attributes = c.__dict__
                mya = {}

                for attr_name, attr_value in attributes.items():
                    if attr_name[0].isupper() and attr_name not in inherited_attributes:
                        mya[attr_name] = {'val': str(attr_value)}

                myc['attributes'] = mya
                classes.append(myc)

        self.stored['SelectedComponent']['classes'] = classes

    # -------------------------------------------------------------------------
    # Widget Container
    # -------------------------------------------------------------------------

    def CreateWC(self, path, x, y):
        """Create a widget container at the specified position.

        Args:
            path: Path to create the container in.
            x: X position.
            y: Y position.
        """
        parent_op = op(path)
        if parent_op:
            wc = parent_op.copy(self.ownerComp.op('widgetContainer'))
            wc.nodeCenterX = x
            wc.nodeCenterY = y

    def CreateWCInCurrentPane(self):
        """Create a widget container at the current pane position."""
        cur_pane = ui.panes.current

        if cur_pane.type == PaneType.NETWORKEDITOR:
            path = cur_pane.owner
            x = cur_pane.x
            y = cur_pane.y
            self.CreateWC(path, x, y)

    # -------------------------------------------------------------------------
    # PopMenu
    # -------------------------------------------------------------------------

    def onPopMenuClose(self):
        """Called by CHOP Execute DAT when the PopMenu window closes."""
        path = self.stored['SelectedWidgetContainer']
        if path and op(path) and hasattr(op(path), 'Selected'):
            op(path).Selected = False
        self.stored['SelectedWidgetContainer'] = None

    # -------------------------------------------------------------------------
    # Pulse handlers
    # -------------------------------------------------------------------------

    def pulse_Editextension(self):
        """Edit extension pulse handler."""
        ext_dat = self.ownerComp.op('AcroWidgets')
        if ext_dat:
            ext_dat.par.edit.pulse()

    def pulse_Editcallbackdat(self):
        """Edit callbacks DAT pulse handler."""
        dat = self.ownerComp.par.Callbackdat.eval()
        if dat:
            dat.par.edit.pulse()
