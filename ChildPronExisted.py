from PyQt5 import QtCore
from PyQt5.QtWidgets import QDialog

import PronExistedDialog


class ChildPronExisted(QDialog):
    def __init__(self):
        super().__init__()
        # self.dialog_s = QDialog()
        self.status = False
        self.ui = PronExistedDialog.Ui_PronExistedDialog()
        self.ui.setupUi(self)
        self.setWindowFlags(QtCore.Qt.WindowTitleHint)

        self.clicked_status = 4
        # 绑定点击事件
        self.ui.update_all.clicked.connect(self.update_all)  # clicked_status = 1
        self.ui.update_bre.clicked.connect(self.update_bre)  # clicked_status = 2
        self.ui.update_ame.clicked.connect(self.update_ame)  # clicked_status = 3
        self.ui.update_none.clicked.connect(self.update_none)  # clicked_status = 4

    def set_dialog_value(self, word, old_bre="", old_ame="", new_bre="", new_ame=""):
        self.clicked_status = 4
        self.ui.operate_word.clear()
        self.ui.old_bre.clear()
        self.ui.old_ame.clear()
        self.ui.new_bre.clear()
        self.ui.new_ame.clear()
        self.ui.operate_word.setText(word)
        self.ui.old_bre.setText(old_bre)
        self.ui.old_ame.setText(old_ame)
        self.ui.new_bre.setText(new_bre)
        self.ui.new_ame.setText(new_ame)

    def update_all(self):
        self.clicked_status = 1
        self.close()

    def update_bre(self):
        self.clicked_status = 2
        self.close()

    def update_ame(self):
        self.clicked_status = 3
        self.close()

    def update_none(self):
        self.clicked_status = 4
        self.close()

    def get_clicked_status(self):
        return self.clicked_status

    # def show_dialog(self):
    #     d = PronExistedDialog.Ui_PronExistedDialog()
    #     d.setupUi(self.dialog_s)
    #     self.dialog_s.show()
