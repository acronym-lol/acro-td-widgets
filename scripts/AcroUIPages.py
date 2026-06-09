"""
Help: search "Extensions" in wiki
"""

from TdStoreTools import StorageManager

class AcroUIPages:
	"""
	AcroUIPages description
	"""
	def __init__(self, ownerComp):
		self.ownerComp = ownerComp

		storedItems = [
			{'name':'Selected','default':1}
		]
		self.stored = StorageManager(self, self.ownerComp, storedItems)

	def SelectPage(self, page):
		self.stored['Selected'] = page
		
	def UpdatePageNum(self):

		n_pages = self.ownerComp.par.Pages
		pages = self.ownerComp.findChildren(tags=['page'], depth=1)
		for p in pages:
			if p.digits > n_pages:
				p.destroy()
		
		tabs = self.ownerComp.op('tabs').findChildren(tags=['tab'], depth=1)	
		for t in tabs:
			if t.digits > n_pages:
				t.destroy()
		
		page_names = [p.name for p in pages]
		tab_names = [t.name for t in tabs]
			
		for i in range(1, n_pages+1):
			page = 'page' + str(i)

			if page not in page_names:
				p = self.ownerComp.copy(op.AW.op('widgetContainer'), name=page)
				p.cloneImmune = True

				#p.tags.add('page')
				p.tags = ['widgetcontainer', 'page']

				p.par.display.expr = 'ext.AcroUIPages.Selected == me.digits'
				p.par.alignorder = 1
				p.par.alignallow = 0
				p.par.vmode = 1

				#p.par.display = 1
				# p.par.layer.expr = 0 #'ext.AcroUIPages.Selected == me.digits'
				# p.par.alignallow = 1
				# p.par.vmode = 0
				# p.par.h.expr = 'parent().height - parent().par.Tabssize'

				#p.par.clone.expr = 'op.AW.op(\'widgetContainer\')'
				p.par.hmode = 1
				
				p.nodeX = (i-1) * 200

				pcore = p.op('core')
				pcore.par.Bgcolorr.expr = 'parent(2).par.Acttabcolorr'
				pcore.par.Bgcolorg.expr = 'parent(2).par.Acttabcolorg'
				pcore.par.Bgcolorb.expr = 'parent(2).par.Acttabcolorb'
				pcore.par.Bgcolora.expr = 'parent(2).par.Acttabcolora'
				pcore.par.Headercolorr.expr = 'parent(2).par.Acttabcolorr'
				pcore.par.Headercolorg.expr = 'parent(2).par.Acttabcolorg'
				pcore.par.Headercolorb.expr = 'parent(2).par.Acttabcolorb'
				pcore.par.Headercolora.expr = 'parent(2).par.Acttabcolora'

				
			tab = 'tab' + str(i)		
			if tab not in tab_names:
				t = self.ownerComp.op('tabs').copy(op.AW.op('widgets/ui/tab'), name=tab)
				t.cloneImmune = True
				t.par.clone.expr = 'op.AW.op("widgets/ui/tab") if hasattr(op, "AW") else ""'
				t.par.enablecloning = True
				t.tags = ['widget', 'ui', 'tab']
				t.par.hmode.expr = 'parent(2).par.Tabsautosize'
				t.par.vmode = 1
				t.par.w = 120
				# t.par.Bottomborder = 0
				t.par.State.expr = 'ext.AcroUIPages.Selected == me.digits'
				t.par.Script = 'ext.AcroUIPages.SelectPage(me.digits)'
				t.par.alignorder.expr = 'me.digits'
				t.par.Text = tab
				t.par.Fontsize = 10
				t.par.display = 1
				#t.par.clone.expr = 'op.AW.WidgetsComp.op(\'_ui_tab\')'

				t.par.Buttoncolorr.expr = 'parent(2).par.Tabcolorr'
				t.par.Buttoncolorg.expr = 'parent(2).par.Tabcolorg'
				t.par.Buttoncolorb.expr = 'parent(2).par.Tabcolorb'
				t.par.Buttoncolora.expr = 'parent(2).par.Tabcolora'
				
				t.par.Overbuttoncolorr.expr = 'parent(2).par.Ovrtabcolorr'
				t.par.Overbuttoncolorg.expr = 'parent(2).par.Ovrtabcolorg'
				t.par.Overbuttoncolorb.expr = 'parent(2).par.Ovrtabcolorb'
				t.par.Overbuttoncolora.expr = 'parent(2).par.Ovrtabcolora'

				t.par.Activebuttoncolorr.expr = 'parent(2).par.Acttabcolorr'
				t.par.Activebuttoncolorg.expr = 'parent(2).par.Acttabcolorg'
				t.par.Activebuttoncolorb.expr = 'parent(2).par.Acttabcolorb'
				t.par.Activebuttoncolora.expr = 'parent(2).par.Acttabcolora'
				
				t.par.Overactivebuttoncolorr.expr = 'parent(2).par.Ovracttabcolorr'
				t.par.Overactivebuttoncolorg.expr = 'parent(2).par.Ovracttabcolorg'
				t.par.Overactivebuttoncolorb.expr = 'parent(2).par.Ovracttabcolorb'
				t.par.Overactivebuttoncolora.expr = 'parent(2).par.Ovracttabcolora'
				
				t.par.Fontcolorr.expr = 'parent(2).par.Fontcolorr'
				t.par.Fontcolorg.expr = 'parent(2).par.Fontcolorg'
				t.par.Fontcolorb.expr = 'parent(2).par.Fontcolorb'
				t.par.Fontcolora.expr = 'parent(2).par.Fontcolora'
				
				t.par.Overfontcolorr.expr = 'parent(2).par.Ovrfontcolorr'
				t.par.Overfontcolorg.expr = 'parent(2).par.Ovrfontcolorg'
				t.par.Overfontcolorb.expr = 'parent(2).par.Ovrfontcolorb'
				t.par.Overfontcolora.expr = 'parent(2).par.Ovrfontcolora'

				t.par.Activefontcolorr.expr = 'parent(2).par.Actfontcolorr'
				t.par.Activefontcolorg.expr = 'parent(2).par.Actfontcolorg'
				t.par.Activefontcolorb.expr = 'parent(2).par.Actfontcolorb'
				t.par.Activefontcolora.expr = 'parent(2).par.Actfontcolora'
				
				t.par.Overactivefontcolorr.expr = 'parent(2).par.Ovractfontcolorr'
				t.par.Overactivefontcolorg.expr = 'parent(2).par.Ovractfontcolorg'
				t.par.Overactivefontcolorb.expr = 'parent(2).par.Ovractfontcolorb'
				t.par.Overactivefontcolora.expr = 'parent(2).par.Ovractfontcolora'
				
				t.par.Bordercolorr.expr = 'parent(2).par.Bordercolorr'
				t.par.Bordercolorg.expr = 'parent(2).par.Bordercolorg'
				t.par.Bordercolorb.expr = 'parent(2).par.Bordercolorb'
				t.par.Bordercolora.expr = 'parent(2).par.Bordercolora'
				p.nodeX = i * 150