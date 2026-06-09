"""
AcroUIMatrix - Dynamic grid layout extension for TouchDesigner.

Manages a resizable matrix of widget containers with draggable splits
for adjusting row and column sizes.
"""
import math

# Node layout constants for network editor positioning
NODE_SPACING_X = 300
NODE_SPACING_Y = 250
NODE_OFFSET_H = 150
NODE_OFFSET_V = 100


class AcroUIMatrix:
	"""
	Manages a dynamic grid layout with resizable rows and columns.

	The matrix consists of:
	- Items: Widget containers arranged in a grid (tagged 'item')
	- H splits: Horizontal dividers between rows (tagged 'h_split')
	- V splits: Vertical dividers between columns (tagged 'v_split')

	Split positions are stored as normalized values (0-1) and used to
	calculate item sizes via parameter expressions.
	"""

	def __init__(self, ownerComp):
		self.ownerComp = ownerComp
		self.items = []
		self.h_splits = []
		self.v_splits = []
		self.m_size1 = 0
		self.m_size2 = 0
		self.n_items = 0
		self.UpdateMatrixParameters()

	def onStart(self):
		return
	
	def onCreate(self):
		if '/AcroWidgets/widgets/ui' not in self.ownerComp.path :
			self.UpdateMatrix()

	def UpdateMatrix(self):
		"""Main orchestrator - syncs matrix layout with current parameters."""
		debug('Updating matrix layout...')
		self.UpdateMatrixParameters()

		if len(self.h_splits) != self.m_size1 and len(self.h_splits) > 1:
			self.ScaleSplits()
		if len(self.v_splits) != self.m_size2 and len(self.v_splits) > 1:
			self.ScaleSplits()

		self.DeleteExtraItems()
		self.UpdateMatrixParameters()
		self.CreateMissingItems()
		self.UpdateMatrixParameters()
		self.UpdateNetworkNodes()
		self.ResizeMatrix()

	def UpdateMatrixParameters(self):
		"""Refresh internal state from component parameters and children."""
		self.m_size1 = self.ownerComp.par.Matrixsize1
		self.m_size2 = self.ownerComp.par.Matrixsize2
		self.n_items = self.m_size1 * self.m_size2

		self.items = self.ownerComp.findChildren(tags=['item'], depth=1)
		self.h_splits = self.ownerComp.findChildren(tags=['h_split'], depth=1)
		self.v_splits = self.ownerComp.findChildren(tags=['v_split'], depth=1)

		self.ownerComp.store('h_splits', len(self.h_splits) - 1)
		self.ownerComp.store('v_splits', len(self.v_splits) - 1)

	def UpdateAllParameters(self):
		"""
		Update all position/size expressions on items, splits, and network nodes.

		Call this to refresh all parameter expressions without creating or
		deleting any operators. Useful when expressions need to be reapplied.
		"""
		self.UpdateMatrixParameters()
		self._updateSplitExpressions()
		self._updateItemExpressions()
		self.UpdateNetworkNodes()

	def UpdateNetworkNodes(self):
		"""Position operators in the network editor for visual organization."""
		debug('Updating network node positions...')
		for item in self.items:
			inverted = self.n_items - item.digits
			item.nodeX = ((item.digits - 1) % self.m_size2) * NODE_SPACING_X
			item.nodeY = math.floor(inverted / self.m_size2) * NODE_SPACING_Y

		for h in self.h_splits[:-1]:
			h.nodeX = (self.m_size2 * NODE_SPACING_X) / 2 - NODE_OFFSET_H
			h.nodeY = (self.m_size1 - h.digits - 1) * NODE_SPACING_Y + NODE_OFFSET_H

		for v in self.v_splits[:-1]:
			v.nodeX = (v.digits * NODE_SPACING_X) - NODE_OFFSET_V
			v.nodeY = (self.m_size1 * NODE_SPACING_Y) / 2 - NODE_OFFSET_H

	def DeleteExtraItems(self):
		"""Remove items and splits that exceed current matrix dimensions."""
		for item in self.items:
			if item.digits > self.n_items:
				item.destroy()

		if len(self.h_splits) > 1:
			for h in self.h_splits[:-1]:
				if h.digits >= self.m_size1:
					self.ownerComp.unstore(h.name)
					h.destroy()

		if len(self.v_splits) > 1:
			for v in self.v_splits[:-1]:
				if v.digits >= self.m_size2:
					self.ownerComp.unstore(v.name)
					v.destroy()

	def CreateMissingItems(self):
		"""Create items and splits needed to fill current matrix dimensions."""
		item_names = [i.name for i in self.items]
		h_split_names = [h.name for h in self.h_splits]
		v_split_names = [v.name for v in self.v_splits]

		# Create missing horizontal splits
		new_split_index = 0
		for h in range(1, self.m_size1):
			split_name = f'h_split{h}'
			if split_name not in h_split_names:
				split_value = self._calculateNewSplitValue('h', new_split_index)
				self._createSplit('h', h, split_value)
				new_split_index += 1

		# Create missing vertical splits
		new_split_index = 0
		for v in range(1, self.m_size2):
			split_name = f'v_split{v}'
			if split_name not in v_split_names:
				split_value = self._calculateNewSplitValue('v', new_split_index)
				self._createSplit('v', v, split_value)
				new_split_index += 1

		# Create missing matrix items
		for j in range(1, self.n_items + 1):
			item_name = f'item{j}'
			if item_name not in item_names:
				self._createItem(item_name, j)

	def ResizeMatrix(self):
		"""Apply size/position expressions to all items based on split positions."""
		self._updateItemExpressions()

	def ResetSplits(self):
		"""Reset all splits to equal divisions."""
		for h in self.h_splits[:-1]:
			split_value = h.digits / len(self.h_splits)
			self.ownerComp.store(h.name, split_value)

		for v in self.v_splits[:-1]:
			split_value = v.digits / len(self.v_splits)
			self.ownerComp.store(v.name, split_value)

	def ScaleSplits(self):
		"""Rescale existing split positions when matrix dimensions change."""
		m_size1 = self.ownerComp.par.Matrixsize1
		m_size2 = self.ownerComp.par.Matrixsize2

		# Horizontal splits added
		if len(self.h_splits) < m_size1 and len(self.h_splits) > 1:
			self._scaleSplitsForAxis('h', m_size1, adding=True)
		# Vertical splits added
		elif len(self.v_splits) < m_size2 and len(self.v_splits) > 1:
			self._scaleSplitsForAxis('v', m_size2, adding=True)
		# Horizontal splits removed
		elif len(self.h_splits) > m_size1 and len(self.h_splits) > 1:
			self._scaleSplitsForAxis('h', m_size1, adding=False)
		# Vertical splits removed
		elif len(self.v_splits) > m_size2 and len(self.v_splits) > 1:
			self._scaleSplitsForAxis('v', m_size2, adding=False)

	# -------------------------------------------------------------------------
	# Private Helpers
	# -------------------------------------------------------------------------

	def _createSplit(self, axis, index, split_value):
		"""
		Create a split operator for the given axis.

		Args:
			axis: 'h' for horizontal, 'v' for vertical
			index: Split number (1-based)
			split_value: Normalized position (0-1)
		"""
		split_name = f'{axis}_split{index}'
		master_name = f'{axis}_split_master'

		split = self.ownerComp.copy(op(master_name), name=split_name)
		split.par.clone = master_name
		split.cloneImmune = True

		self.ownerComp.store(split_name, split_value)

		if axis == 'h':
			split.par.y.expr = '(1 - parent().fetch(me.name)) * parent().height - parent().par.Splitsize / 2'
		else:
			split.par.x.expr = 'parent().fetch(me.name) * parent().width - parent().par.Splitsize / 2'

		split.par.display.expr = 'parent().par.Splitsactive'

	def _createItem(self, name, index):
		"""Create a widget container item at the given index."""
		item = self.ownerComp.copy(op.AW.op('widgetContainer'), name=name)
		item.cloneImmune = True
		item.tags = ['widgetcontainer', 'item']
		item.par.hmode = 0
		item.par.vmode = 0
		item.par.alignallow = 1
		item.par.display = 1
		item.par.alignorder = index * 2
		item.par.clone.expr = "op.AW.op('widgetContainer')"

	def _calculateNewSplitValue(self, axis, new_index):
		"""
		Calculate the value for a newly created split.

		Args:
			axis: 'h' or 'v'
			new_index: 0-based index among new splits being created

		Returns:
			Normalized split position (0-1)
		"""
		splits = self.h_splits if axis == 'h' else self.v_splits
		target_size = self.m_size1 if axis == 'h' else self.m_size2

		# Guard against division by zero
		if target_size <= 0:
			return 0.5

		# No existing splits - create with standard equal spacing
		if len(splits) == 1:
			return (new_index + 1) / target_size

		# Existing splits - place new ones at the end
		diff = target_size - len(splits)
		new_region = diff / target_size
		split_scalar = 1.0 - new_region
		delta_split = new_region / diff
		return split_scalar + (new_index * delta_split)

	def _scaleSplitsForAxis(self, axis, new_size, adding):
		"""
		Rescale split positions when rows/columns are added or removed.

		Args:
			axis: 'h' or 'v'
			new_size: New matrix dimension for this axis
			adding: True if splits are being added, False if removed
		"""
		splits = self.h_splits if axis == 'h' else self.v_splits

		# Guard against invalid sizes
		if new_size <= 0 or len(splits) <= 1:
			return

		if adding:
			# Scale down existing splits to make room for new ones
			diff = new_size - len(splits)
			new_region = diff / new_size
			split_scalar = 1.0 - new_region

			for split in splits[:-1]:
				value = self.ownerComp.fetch(split.name)
				self.ownerComp.store(split.name, value * split_scalar)
		else:
			# Scale up remaining splits after removal
			diff = len(splits) - new_size
			last_index = -diff - 1
			last_split_val = self.ownerComp.fetch(splits[last_index].name)

			for split in splits[:-1]:
				value = self.ownerComp.fetch(split.name)
				self.ownerComp.store(split.name, value / last_split_val)

	def _updateSplitExpressions(self):
		"""Set position and display expressions on all split operators."""
		for h in self.h_splits[:-1]:
			h.par.y.expr = '(1 - parent().fetch(me.name)) * parent().height - parent().par.Splitsize / 2'
			h.par.display.expr = 'parent().par.Splitsactive'

		for v in self.v_splits[:-1]:
			v.par.x.expr = 'parent().fetch(me.name) * parent().width - parent().par.Splitsize / 2'
			v.par.display.expr = 'parent().par.Splitsactive'

	def _updateItemExpressions(self):
		"""Set position and size expressions on all item operators."""
		for item in self.items:
			row = math.floor((item.digits - 1) / self.m_size2) + 1
			col = (item.digits - 1) % self.m_size2 + 1

			# Calculate height expression components
			h_expr = self._buildHeightExpr(row)
			item.par.h.expr = h_expr['size']
			item.par.y.expr = h_expr['pos']

			# Calculate width expression components
			w_expr = self._buildWidthExpr(col)
			item.par.w.expr = w_expr['size']
			item.par.x.expr = w_expr['pos']

	def _buildHeightExpr(self, row):
		"""
		Build height and y-position expressions for an item in the given row.

		Returns:
			dict with 'size' and 'pos' expression strings
		"""
		# Single row - no splits, fill parent height
		if self.m_size1 == 1:
			return {'size': 'parent().height', 'pos': '0'}

		if row == self.m_size1:  # Last row
			upper = f"parent().fetch('h_split{row - 1}', 0))"
			lower = '(1'
			splitsize = 'parent().par.Splitsize/2'
			pos = '0'
		elif row == 1:  # First row
			upper = '0)'
			lower = "(parent().fetch('h_split1')"
			splitsize = 'parent().par.Splitsize/2'
			pos = 'parent().height - me.height'
		else:  # Middle rows
			upper = f"parent().fetch('h_split{row - 1}', 0))"
			lower = f"(parent().fetch('h_split{row}')"
			splitsize = 'parent().par.Splitsize'
			pos = f"(1-parent().fetch('h_split{row}', 0)) * parent().height + parent().par.Splitsize/2"

		size_ratio = f'{lower}-{upper}'
		return {
			'size': f'parent().height * {size_ratio}-{splitsize}',
			'pos': pos
		}

	def _buildWidthExpr(self, col):
		"""
		Build width and x-position expressions for an item in the given column.

		Returns:
			dict with 'size' and 'pos' expression strings
		"""
		# Single column - no splits, fill parent width
		if self.m_size2 == 1:
			return {'size': 'parent().width', 'pos': '0'}

		if col == self.m_size2:  # Last column
			left = f"parent().fetch('v_split{col - 1}', 0))"
			right = '(1'
			splitsize = 'parent().par.Splitsize/2'
			pos = f"parent().fetch('v_split{col - 1}', 0) * parent().width + parent().par.Splitsize/2"
		elif col == 1:  # First column
			left = '0)'
			right = "(parent().fetch('v_split1')"
			splitsize = 'parent().par.Splitsize/2'
			pos = '0'
		else:  # Middle columns
			left = f"parent().fetch('v_split{col - 1}', 0))"
			right = f"(parent().fetch('v_split{col}')"
			splitsize = 'parent().par.Splitsize'
			pos = f"parent().fetch('v_split{col - 1}', 0) * parent().width + parent().par.Splitsize/2"

		size_ratio = f'{right}-{left}'
		return {
			'size': f'parent().width * {size_ratio}-{splitsize}',
			'pos': pos
		}
