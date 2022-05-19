from PyQt5 import QtCore
from PyQt5.QtWidgets import QDialog

import ConfirmAddWord


class ChildConfirmAddWord(QDialog):
    def __init__(self):
        super().__init__()
        # self.dialog_s = QDialog()
        self.status = False
        self.ui = ConfirmAddWord.Ui_ConfirmAddWord()
        self.ui.setupUi(self)
        self.ui.ok_btn.clicked.connect(self.set_sta_true)
        self.ui.cancel_btn.clicked.connect(self.set_sta_false)
        self.setWindowFlags(QtCore.Qt.WindowTitleHint)

    def set_words(self, word, group, pos, chinese_translation):
        self.set_sta_false()
        self.ui.eng_label.setText(word)
        self.ui.trans_box.clear()
        self.ui.trans_box.addItems([group, pos, chinese_translation])

    def set_sta_true(self):
        self.status = True
        self.close()

    def set_sta_false(self):
        self.status = False
        self.close()

    def get_status(self):
        return self.status

    # def show_dialog(self):
    #     d = ConfirmAddWord.Ui_ConfirmAddWord()
    #     d.setupUi(self.dialog_s)
    #     self.dialog_s.show()
