
import binascii
import struct

from PySide import QtUiTools
from PySide.QtCore import *
from PySide.QtGui import *

from Petter.guihelper import exception_handler

class DataTypes(QMainWindow):
	def __init__(self, main_window, company_name, software_name):
		QMainWindow.__init__(self)
		self.setWindowTitle("Data Types")
		self.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)

		self.main_window = main_window

		# Set up UI
		loader = QtUiTools.QUiLoader()
		self.ui = loader.load('data_Types.ui', None)
		self.setCentralWidget(self.ui)
		QMetaObject.connectSlotsByName(self)

		# Size constraints
		self.setMinimumSize(self.ui.minimumSize())
		self.setMaximumSize(self.ui.maximumSize())

		# Read settings
		self.settings = QSettings(company_name, software_name)
		self.restoreGeometry(self.settings.value("DataTypes/geometry"))
		self.view = None

	def set_view(self, view):
		self.view = view

	def get_integer_format_string(self):
		if self.ui.littleEndianCheckBox.isChecked():
			format_string = '<'
		else:
			format_string = '>'

		if self.ui.eightBitRadioButton.isChecked():
			format_string += 'b'
		elif self.ui.sixteenBitRadioButton.isChecked():
			format_string += 'h'
		elif self.ui.thirtyTwoBitRadioButton.isChecked():
			format_string += 'i'
		elif self.ui.sixtyFourBitRadioButton.isChecked():
			format_string += 'q'

		if not self.ui.signedCheckBox.isChecked():
			format_string = format_string.upper()

		return format_string

	def get_floating_point_format_string(self):
		if self.ui.littleEndianFloatingPointCheckBox.isChecked():
			format_string = '<'
		else:
			format_string = '>'

		if self.ui.singleRadioButton.isChecked():
			format_string += 'f'
		elif self.ui.doubleRadioButton.isChecked():
			format_string += 'd'
		else:
			raise ValueError("No floating point type selected.")

		return format_string

	def get_format_string(self):
		current_tab = self.ui.tabWidget.currentWidget()
		format_string = None
		if current_tab == self.ui.tab_integers:
			format_string = self.get_integer_format_string()
		elif current_tab == self.ui.tab_floating_point:
			format_string = self.get_floating_point_format_string()
		else:
			raise ValueError("No number tab selected.")
		return format_string

	def set_hexEdit_bytes(self, bytes):
		text = ''.join( [ "%02X " % ord( x ) for x in bytes ] ).strip()
		self.ui.hexEdit.setText(text)

	def set_bytes(self, bytes_or_view):
		current_tab = self.ui.tabWidget.currentWidget()

		if current_tab == self.ui.tab_integers or \
		   current_tab == self.ui.tab_floating_point:
			#Get the format string.
			format_string = self.get_format_string()
			# Compute how many bytes are needed.
			size_needed = struct.calcsize(format_string)
			# Extract the correct number of bytes if the
			# input is a memoryview.
			if isinstance(bytes_or_view, memoryview):
				bytes_or_view = bytes_or_view[:size_needed].tobytes()

		if current_tab == self.ui.tab_integers:
			# Try and parse an integer.
			self.ui.integerEdit.setEnabled(True)
			self.ui.signedCheckBox.setEnabled(True)
			self.ui.littleEndianCheckBox.setEnabled(True)

			number = None
			try:
				assert(size_needed == len(bytes_or_view))
				number = struct.unpack(format_string, bytes_or_view)[0]
			except:
				self.ui.integerEdit.setText("n/a")
				self.ui.integerEdit.setEnabled(False)
				self.ui.signedCheckBox.setEnabled(False)
				self.ui.littleEndianCheckBox.setEnabled(False)

			if number is not None:
				self.ui.integerEdit.setText("%d" % number)
				number_bytes = struct.pack(format_string, number)
				self.set_hexEdit_bytes(number_bytes)

		elif current_tab == self.ui.tab_floating_point:
			# Try and parse a floating point.
			self.ui.floatingPointEdit.setEnabled(True)
			self.ui.littleEndianFloatingPointCheckBox.setEnabled(True)

			number = None
			try:
				assert(size_needed == len(bytes_or_view))
				number = struct.unpack(format_string, bytes_or_view)[0]
			except:
				self.ui.floatingPointEdit.setText("n/a")
				self.ui.floatingPointEdit.setEnabled(False)
				self.ui.littleEndianFloatingPointCheckBox.setEnabled(False)

			if number is not None:
				self.ui.floatingPointEdit.setText("%e" % number)
				number_bytes = struct.pack(format_string, number)
				self.set_hexEdit_bytes(number_bytes)

		elif current_tab == self.ui.tab_dates:
			pass


	def update(self):
		if not self.view:
			return
		if not self.view.data_buffer:
			return
		data_view = self.view.data_at_position(self.view.get_cursor_position())
		self.set_bytes(data_view)

	def showEvent(self, event):
		QMainWindow.showEvent(self, event)

	def closeEvent(self, event):
		self.settings.setValue("DataTypes/geometry", self.saveGeometry())
		QMainWindow.closeEvent(self, event)

	@Slot()
	@exception_handler
	def on_hexEdit_textEdited(self):
		# Fires only when the text is edited by the user, not
		# by the program.
		try:
			hex_string = self.ui.hexEdit.text().encode('utf-8')
			hex_string = hex_string.replace(" ", "")
			bytes = binascii.unhexlify(hex_string)
		except:
			bytes = ''
		self.set_bytes(bytes)


	@Slot()
	@exception_handler
	def on_changeButton_clicked(self):
		pass



	@Slot()
	@exception_handler
	def on_tabWidget_currentChanged(self):
		self.update()

	@Slot()
	@exception_handler
	def on_eightBitRadioButton_clicked(self):
		self.update()

	@Slot()
	@exception_handler
	def on_sixteenBitRadioButton_clicked(self):
		self.update()

	@Slot()
	@exception_handler
	def on_thirtyTwoBitRadioButton_clicked(self):
		self.update()

	@Slot()
	@exception_handler
	def on_sixtyFourBitRadioButton_clicked(self):
		self.update()

	@Slot()
	@exception_handler
	def on_signedCheckBox_clicked(self):
		self.on_hexEdit_textEdited()

	@Slot()
	@exception_handler
	def on_littleEndianCheckBox_clicked(self):
		self.on_hexEdit_textEdited()

	@Slot()
	@exception_handler
	def on_singleRadioButton_clicked(self):
		self.update()

	@Slot()
	@exception_handler
	def on_doubleRadioButton_clicked(self):
		self.update()

	@Slot()
	@exception_handler
	def on_littleEndianFloatingPointCheckBox_clicked(self):
		self.on_hexEdit_textEdited()