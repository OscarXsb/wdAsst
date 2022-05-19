from PyQt5 import QtCore
from PyQt5.QtWidgets import QDialog, QApplication

import sys

import ChangeStandardLexicon


class ChildChangeStandardLexicon(QDialog):
    def __init__(self):
        super().__init__()
        # self.dialog_s = QDialog()
        self.status = False
        self.ui = ChangeStandardLexicon.Ui_change_standard_lexicon()
        self.ui.setupUi(self)
        self.ui.ok_btn.clicked.connect(self.ok_btn_clicked)
        self.ui.cancel_btn.clicked.connect(self.cancel_btn_clicked)
        self.setWindowFlags(QtCore.Qt.WindowTitleHint)
        self.cancelled = "cancelled"
        self.yes = "yes"
        self.status = self.cancelled
        self.chosen_lexicon_name = ""

    def load_contents(self, content_list, current_text):
        self.ui.choose_lexicon.clear()
        for i in content_list:
            self.ui.choose_lexicon.addItem(i[0])
        print(current_text)
        self.ui.choose_lexicon.setCurrentText(current_text)
        self.status = self.cancelled

    def ok_btn_clicked(self):
        self.chosen_lexicon_name = self.ui.choose_lexicon.currentText()
        print(self.chosen_lexicon_name)
        self.status = self.yes
        self.close()

    def cancel_btn_clicked(self):
        self.status = self.cancelled
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    dialog = ChildChangeStandardLexicon()
    dialog.show()
    sys.exit(app.exec_())
