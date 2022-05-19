from PyQt5 import QtCore
from PyQt5.QtWidgets import QDialog, QMessageBox

import ManageGroupRename


class ChildManageGroupRename(QDialog):
    def __init__(self):
        super().__init__()
        # self.dialog_s = QDialog()
        self.ui = ManageGroupRename.Ui_ManageGroupRename()
        self.ui.setupUi(self)
        self.setWindowFlags(QtCore.Qt.WindowTitleHint)
        self.existed_group = []
        self.status = 1  # 0 - 选择确定，1 - 选择取消
        self.ui.renameButton.clicked.connect(self.rename_button_clicked)
        self.ui.cancelButton.clicked.connect(self.cancel_button_clicked)

    def rename_button_clicked(self):
        self.status = 0
        if self.ui.newName.text().strip() == "":
            QMessageBox.warning(
                self,
                "词库新命名为空",
                "词库新命名为空，请重新输入！")
        elif self.ui.newName.text().strip() in self.existed_group:
            QMessageBox.warning(
                self,
                "该词库名称已存在",
                "该词库名称已存在，请重新输入！")
        else:
            self.close()

    def cancel_button_clicked(self):
        self.status = 1
        self.close()

    def set_content(self, origin_name, existed_group):
        self.ui.originName.clear()
        self.ui.newName.clear()
        self.ui.originName.setText(origin_name)
        self.existed_group = existed_group
        self.status = 1

    def return_current_text(self):
        if self.status == 0:
            return self.ui.newName.text()
        else:
            return None
