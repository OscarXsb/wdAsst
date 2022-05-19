# coding:utf-8
import os
import random
import re
import sqlite3
import sys
import time

import xlwt
from PyQt5.QtCore import Qt, QUrl, QTimer
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QTableWidgetItem, QTableWidget, QFileDialog, \
    QCompleter

import ChildChangeStandardLexicon
import ChildConfirmAddWord
import ChildManageGroupRename
import ChildPronExisted
import queryWords
import readConfig
import wdAsst
from OperateDatabase import OperateDatabase


class MainWindow(QMainWindow, OperateDatabase):
    def __init__(self):
        super().__init__()
        # 使用ui文件导入定义界面类
        self.ui = wdAsst.Ui_WdAsst()
        # 读取配置文件
        self.current_config = readConfig.ReadConfig("config.ini")
        # 连接数据库
        db_path = self.current_config.get_config(
            "database", "file_path")  # 读取配置并获得数据库路径
        self.conn = sqlite3.connect(db_path)  # 连接数据库
        self.set_connection(self.conn)
        self.group_names = self.query_database_without_limits(
            "group").fetchall()  # 获取所有单词组别（初始化成员变量）
        # 初始化界面
        self.ui.setupUi(self)
        self.add_word_init()  # 初始化单词添加界面
        self.manage_word_init()  # 初始化单词管理页面
        self.init_pron_keyboard()  # 初始化音标输入页面屏幕键盘
        # 子窗口
        self.child_change_standard_lexicon = ChildChangeStandardLexicon.ChildChangeStandardLexicon()
        self.child_confirm_add_word = ChildConfirmAddWord.ChildConfirmAddWord()  # 添加单词确认子窗口
        self.child_pron_existed = ChildPronExisted.ChildPronExisted()  # 发音已存在操作子窗口
        self.child_manage_group_rename = ChildManageGroupRename.ChildManageGroupRename()  # 词库重命名子窗口
        # 绑定信号
        self.ui.search_btn.clicked.connect(self.search_word)  # 搜索页面搜索按钮
        self.ui.search_box.returnPressed.connect(
            self.search_word)  # 搜索页面搜索框 Return 键盘事件
        self.ui.reset_search.clicked.connect(self.reset_search)  # 搜索页面重置按钮
        self.ui.manage_word_btn.clicked.connect(
            self.manage_word_display)  # 管理单词查询单词按钮
        self.ui.manage_word_check_group.currentIndexChanged.connect(
            self.manage_word_display)  # 管理单词下拉菜单重新选择
        # 添加单词页面信号
        self.ui.add_btn.clicked.connect(self.add_word)  # 添加单词页面添加按钮
        self.ui.reset_add.clicked.connect(self.reset_add_word)  # 添加单词页面重置按钮
        # 添加读音
        self.editing_pron = 1  # 设置添加读音页面正在编辑的输入框为英式音标（初始化成员变量）
        self.ui.pron_keyboard.cellClicked.connect(
            self.pron_keyboard_click)  # 设置添加读音页面屏幕键盘点击事件
        self.ui.add_pron_ame.cursorPositionChanged.connect(
            self.set_pron_ame)  # 设置在美式发音输入框内的指针移动后设置正在编辑的输入框为美式音标
        self.ui.add_pron_bre.cursorPositionChanged.connect(
            self.set_pron_bre)  # 设置在英式发音输入框内的指针移动后设置正在编辑的输入框为英式音标
        self.ui.add_pron_submit.clicked.connect(
            self.submit_pron)  # 添加读音页面提交按钮点击事件
        self.ui.add_pron_ame.setDragEnabled(True)  # 添加读音页面美式发音输入框允许拖拽
        self.ui.add_pron_ame.setAcceptDrops(True)  # 添加读音页面美式发音输入框允许接受拖拽
        self.ui.add_pron_bre.setDragEnabled(True)  # 添加读音页面英式发音输入框允许拖拽
        self.ui.add_pron_bre.setAcceptDrops(True)  # 添加读音页面英式发音输入框允许接受拖拽
        self.ui.add_pron_reset.clicked.connect(self.reset_pron)
        # 测试单词
        self.test_word_init()
        self.ui.test_word_group_checked_button.clicked.connect(
            self.start_test_word)
        self.testing_word_list = []
        self.ui.submit_test.clicked.connect(self.verify_testing_word)
        self.ui.test_input_eng.returnPressed.connect(self.verify_testing_word)
        self.ui.stop_test.clicked.connect(self.stop_test)
        self.ui.test_word_clear_table.clicked.connect(self.clear_test_table)
        self.ui.test_word_save_table.clicked.connect(self.save_test_table)
        # 管理词库
        self.group_get = self.get_group_name_list_detail()
        self.completer = QCompleter(self.group_get)
        self.init_group_manage(self.group_get)
        self.ui.manage_groups_check_group_box.currentTextChanged.connect(
            self.manage_group_check_group_update)
        self.ui.manage_group_add.clicked.connect(self.manage_group_add)
        self.ui.manage_group_info.clicked.connect(self.manage_group_info)
        self.ui.manage_group_rename.clicked.connect(self.manage_group_rename)
        self.ui.manage_group_remove.clicked.connect(
            self.manage_group_remove)  # 删除词库

        # 根据单词选择正确释义
        self.ui.test_translation_start.clicked.connect(
            self.test_translation_start)
        self.standard_lexicon_name = ""
        self.testing_standard_answer = ""
        self.testing_standard_option = []  # 现有的正确答案组
        self.ui.test_translation_read.setStyleSheet(
            "QPushButton{border-image: url(./img/speak.svg)}")
        self.standard_words_reference = self.get_standard_words_from_config()
        # print(self.standard_words_reference)
        self.testing_standard = self.standard_words_reference.copy()
        self.ui.test_translation_read.clicked.connect(
            self.test_translation_read_word)
        self.ui.test_translation_option_group.buttonClicked.connect(
            self.test_translation_option_clicked)
        self.ui.test_translation_reset_record.clicked.connect(
            self.test_trans_record_reset)
        # 倒计时
        self.test_translation_timer = QTimer(self)
        self.test_translation_timer.timeout.connect(
            self.test_trans_update_time)
        self.test_translation_count = 10
        self.test_translation_flag = False
        # 下一次测试
        self.test_next_timer = QTimer(self)
        self.test_next_timer.timeout.connect(
            self.test_translation_publish_word)
        # 停止选择释义测试
        self.ui.test_translation_stop.clicked.connect(self.test_translation_stop_ask)

        # 菜单操作
        self.ui.change_standard_group.triggered.connect(self.change_standard_group)

        self.ui.statusbar.showMessage(
            'WdAsst(Word Assistant) Developed by Oscar Xia')  # 程序底部信息栏显示作者信息

        self.media_player = QMediaPlayer(self)
        self.media_player.stateChanged.connect(self.media_state_changed)

    def standard_lexicon_name_list(self):
        sql = "SELECT lexicon_name FROM standard_index"
        c = self.conn.cursor()
        c.execute(sql)
        return c.fetchall()

    def change_standard_group(self):
        # 弹出子窗口选择标准词库，通过子窗口更改 config 文件
        standard_lexicon_name_list = self.standard_lexicon_name_list()
        sql = f"SELECT lexicon_name FROM standard_index WHERE standard_table = '{self.current_config.get_config('standard_word', 'table_name')}'"
        c = self.conn.cursor()
        c.execute(sql)
        lexicon_name_current = c.fetchall()[0][0]
        self.child_change_standard_lexicon.load_contents(
            standard_lexicon_name_list, lexicon_name_current)
        self.child_change_standard_lexicon.exec()
        if self.child_change_standard_lexicon.status == self.child_change_standard_lexicon.yes:
            current_lexicon_name = self.child_change_standard_lexicon.chosen_lexicon_name
            sql = f"SELECT * FROM standard_index WHERE lexicon_name = '{current_lexicon_name}'"
            c = self.conn.cursor()
            c.execute(sql)
            current_lexicon = c.fetchall()[0][1]
            self.current_config.update_config(
                "standard_word", "table_name", current_lexicon)
            self.alert_message("information", "更改标准词库成功", f"成功更改标准词库为 “{current_lexicon_name}”！")

    def test_trans_stop_without_asking(self):
        # 清空定时器
        self.test_next_timer.stop()
        self.test_translation_timer.stop()
        self.test_translation_count = 10
        self.ui.test_translation_time.display(self.test_translation_count)
        self.test_translation_flag = False
        # 显示开始按钮
        self.ui.test_translation_start.setEnabled(True)
        self.ui.test_translation_start.show()
        # 清除测试记录
        self.ui.test_trans_tested_count.setText("0")
        self.ui.test_trans_right_count.setText("0")
        self.ui.test_trans_percent.setText("0%")
        # 清除前一个单词记录
        self.ui.test_translation_last_word.setText("单词记录")

    def test_translation_stop_ask(self):
        reply = QMessageBox.question(
            self, "停止测试", f"确定要停止测试吗？（记录将被清除且不可回到当前状态）", QMessageBox.Yes | QMessageBox.No)
        if reply != QMessageBox.Yes:
            return
        self.test_trans_stop_without_asking()

    def test_trans_record_reset(self):
        reply = QMessageBox.question(
            self, "清除记录", f"确定要清除记录吗？（该操作不可逆）", QMessageBox.Yes | QMessageBox.No)
        if reply != QMessageBox.Yes:
            return
        self.ui.test_trans_tested_count.setText("0")
        self.ui.test_trans_right_count.setText("0")
        self.ui.test_trans_percent.setText("0%")

    def test_trans_update_time(self):
        self.test_translation_count -= 1
        if self.test_translation_count <= 0:
            self.test_translation_flag = False
        if self.test_translation_flag:
            self.ui.test_translation_time.display(self.test_translation_count)
        else:
            self.test_translation_count = 10
            self.ui.test_translation_time.display(self.test_translation_count)
            self.test_translation_timer.stop()
            self.test_translation_timeout_wrong()

    def test_translation_timeout_wrong(self):
        self.test_trans_display_right_answer()
        self.test_trans_set_options_disabled(True)
        self.test_translation_flag = False
        self.test_translation_update_database_record(2)
        self.publish_statistic_number(False)
        self.ui.test_translation_last_word.setText(
            f"{self.ui.test_translation_show_word.text()} {self.testing_standard_answer}")
        self.test_next_timer.start(2000)

    def test_translation_publish_option(self, right_trans):
        """
        发布以参数 right_trans 为正确选项的选项组
        :param right_trans: 正确选项
        :return: 正确选项
        """
        option_list = [right_trans]
        while len(option_list) < 4:
            t = self.standard_words_reference[random.randint(
                0, len(self.standard_words_reference) - 1)][2]
            if t not in option_list:
                option_list.append(t)
        random.shuffle(option_list)
        self.testing_standard_option = option_list
        self.ui.test_translation_option_1.setText(option_list[0])
        self.ui.test_translation_option_2.setText(option_list[1])
        self.ui.test_translation_option_3.setText(option_list[2])
        self.ui.test_translation_option_4.setText(option_list[3])
        self.test_trans_set_options_disabled(False)
        self.ui.test_translation_option_1.setStyleSheet(
            "QToolButton{background-color: auto;}")
        self.ui.test_translation_option_2.setStyleSheet(
            "QToolButton{background-color: auto;}")
        self.ui.test_translation_option_3.setStyleSheet(
            "QToolButton{background-color: auto;}")
        self.ui.test_translation_option_4.setStyleSheet(
            "QToolButton{background-color: auto;}")
        return right_trans

    def test_trans_display_right_answer(self):
        for i in range(len(self.testing_standard_option)):
            if self.testing_standard_option[i] == self.testing_standard_answer:
                if i == 0:
                    self.ui.test_translation_option_1.setStyleSheet(
                        "QToolButton{background-color: rgb(0, 255, 0);}")
                elif i == 1:
                    self.ui.test_translation_option_2.setStyleSheet(
                        "QToolButton{background-color: rgb(0, 255, 0);}")
                elif i == 2:
                    self.ui.test_translation_option_3.setStyleSheet(
                        "QToolButton{background-color: rgb(0, 255, 0);}")
                elif i == 3:
                    self.ui.test_translation_option_4.setStyleSheet(
                        "QToolButton{background-color: rgb(0, 255, 0);}")
                break

    def test_trans_set_options_disabled(self, a):
        self.ui.test_translation_option_1.setDisabled(a)
        self.ui.test_translation_option_2.setDisabled(a)
        self.ui.test_translation_option_3.setDisabled(a)
        self.ui.test_translation_option_4.setDisabled(a)

    def publish_statistic_number(self, right):
        self.ui.test_trans_tested_count.setText(
            str(int(self.ui.test_trans_tested_count.text()) + 1))
        if right:
            self.ui.test_trans_right_count.setText(
                str(int(self.ui.test_trans_right_count.text()) + 1))
        self.ui.test_trans_percent.setText('{:.2%}'.format(int(
            self.ui.test_trans_right_count.text()) / int(self.ui.test_trans_tested_count.text())))
        # print(int(self.ui.test_trans_tested_count.text())+1)
        # print(self.ui.test_trans_right_count.text())

    def test_translation_update_database_record(self, mode):
        """
        mode: 1-单词正确 2-单词错误
        """
        if mode == 1:
            print(self.ui.test_translation_show_word.text())
            word_item = self.query_database("word", self.ui.test_translation_show_word.text(),
                                            self.current_config.get_config('standard_word', 'table_name')).fetchall()
            print(word_item)
            tested_times = int(word_item[0][4])
            right_times = int(word_item[0][5])
            self.update_database(self.current_config.get_config('standard_word', 'table_name'),
                                 f"tested_times = {tested_times + 1}, right_times = {right_times + 1}",
                                 f"word = '{self.ui.test_translation_show_word.text()}'")
        else:
            word_item = self.query_database("word", self.ui.test_translation_show_word.text(),
                                            self.current_config.get_config('standard_word', 'table_name')).fetchall()
            tested_times = int(word_item[0][4])
            self.update_database(self.current_config.get_config('standard_word', 'table_name'),
                                 f"tested_times = {tested_times + 1}",
                                 f"word = '{self.ui.test_translation_show_word.text()}'")

    def test_translation_option_clicked(self, e):
        input_ans = e.text()
        if input_ans == self.testing_standard_answer:
            # 选择的单词正确
            # print("Right")
            e.setStyleSheet("QToolButton{background-color: rgb(0, 255, 0);}")
            self.ui.test_translation_last_word.setText(
                f"{self.ui.test_translation_show_word.text()} {self.testing_standard_answer}")
            self.test_translation_update_database_record(1)
            self.publish_statistic_number(True)
            self.test_next_timer.start(1000)
        else:
            e.setStyleSheet("QToolButton{background-color: rgb(255, 0, 0);}")
            self.ui.test_translation_last_word.setText(
                f"{self.ui.test_translation_show_word.text()} {self.testing_standard_answer}")
            self.publish_statistic_number(False)
            self.test_translation_update_database_record(2)
            self.test_next_timer.start(2000)
            self.test_trans_display_right_answer()
        self.test_trans_set_options_disabled(True)
        self.test_translation_count = 10
        self.ui.test_translation_time.display(self.test_translation_count)
        self.test_translation_timer.stop()
        self.test_translation_flag = False

    def test_translation_read_word(self):
        word = self.ui.test_translation_show_word.text()
        self.play_media(f"./pronunciation/{word}.mp3")

    def media_state_changed(self, state):
        if state == QMediaPlayer.PlayingState:
            # print('player is playing')
            pass
        if state == QMediaPlayer.PausedState:
            # print('player is pausing')
            pass
        if state == QMediaPlayer.StoppedState:
            # print('player is stopped')
            self.media_player.setMedia(QMediaContent())

    def play_media(self, filename):
        pro_dir = os.path.split(os.path.realpath(__file__))[0]
        abs_path = os.path.join(pro_dir, filename)
        url = QUrl.fromLocalFile(abs_path)
        c = QMediaContent(url)
        self.media_player.setMedia(c)
        self.media_player.play()

    def get_standard_words_from_config(self):
        table_name = self.current_config.get_config(
            "standard_word", "table_name")
        # 获取单词表
        sql = f"SELECT * FROM {table_name} ORDER BY tested_times ASC"
        # print(sql)
        c = self.conn.cursor()
        c.execute(sql)
        self.standard_words_reference = c.fetchall()
        # 获取测试词库信息
        sql = f"SELECT * FROM standard_index WHERE standard_table = '{table_name}'"
        c = self.conn.cursor()
        c.execute(sql)
        self.standard_lexicon_name = c.fetchall()[0][2]
        # print(self.standard_lexicon_name)
        random.shuffle(self.standard_words_reference)
        self.standard_words_reference = sorted(
            self.standard_words_reference, key=(lambda x: x[4]), reverse=False)
        self.testing_standard = self.standard_words_reference.copy()
        return self.standard_words_reference

    def test_translation_start(self):
        self.get_standard_words_from_config()
        self.test_translation_publish_word()
        self.ui.test_translation_start.setEnabled(False)
        self.ui.test_translation_start.hide()
        self.ui.test_translation_group.setText(self.standard_lexicon_name)

    def test_translation_publish_word(self):
        self.test_next_timer.stop()
        print(self.testing_standard)
        print(self.standard_words_reference)
        if len(self.testing_standard) <= 0:
            self.alert_message("information", "词库测试完成", "{} 词库中的所有单词测试完成！".format(
                self.standard_lexicon_name))
            self.test_trans_stop_without_asking()
            return
        self.ui.test_translation_show_word.setText(
            self.testing_standard[0][1])  # 显示正在测试列表首个单词
        self.test_translation_publish_option(
            self.testing_standard[0][2])  # 设置选项
        self.testing_standard_answer = self.testing_standard[0][2]  # 记录正确答案
        self.test_translation_flag = True  # 测试计时开始
        self.test_translation_timer.start(1000)
        self.testing_standard.pop(0)

    def manage_group_remove(self):
        operate_name = self.ui.manage_groups_check_group_box.currentText().strip()
        if operate_name == "":
            self.alert_message("warning", "词库名为空", "操作的词库名为空")
        # 确认删除单词信息
        reply = QMessageBox.question(
            self, "删除词库", f"确定要删除词库 '{operate_name}' 吗？（词库中的所有单词将被全部删除）", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.No:
            self.alert_message("information", "取消删除词库",
                               f"未删除词库 '{operate_name}'")
            return
        self.ui.manage_groups_log.append(f'[{time.ctime(time.time())}]')
        self.ui.manage_groups_log.append(f"开始删除词库 '{operate_name}' ")
        # 打印逐条单词记录删除的日志
        display_content = self.query_database(
            "group_name", operate_name, "word").fetchall()
        for i in display_content:
            self.ui.manage_groups_log.append(f"删除单词 {i[3]} ")
        self.ui.manage_groups_log.append(f"共删除了 {len(display_content)} 条单词记录")
        # 从单词表删除
        self.delete_database(f"group_name ='{operate_name}'", "word")
        # 从词库表删除
        self.delete_database(f"group_name ='{operate_name}'", "group")
        self.ui.manage_groups_log.append(f"删除词库 '{operate_name}' 完成")
        self.ui.manage_groups_log.moveCursor(
            self.ui.manage_groups_log.textCursor().End)
        self.alert_message("information", "删除词库成功",
                           f"删除词库 '{operate_name}' 成功！")
        # 更新下拉菜单
        self.update_group_menu()
        self.ui.manage_groups_check_group_box.setCurrentIndex(-1)

    def update_group_menu(self):
        self.group_get = self.get_group_name_list_detail()
        self.manage_group_check_group_update()
        self.add_word_init()
        self.manage_word_init()
        self.test_word_init()
        self.ui.manage_groups_check_group_box.clear()
        self.ui.manage_groups_check_group_box.addItems(
            self.get_group_name_list_detail())

    def manage_group_rename(self):
        origin_name = self.ui.manage_groups_check_group_box.currentText()
        if origin_name == "":
            return
        existed_group = self.get_group_name_list_detail()
        self.child_manage_group_rename.set_content(origin_name, existed_group)
        self.child_manage_group_rename.exec()
        child_result = self.child_manage_group_rename.return_current_text()
        if child_result is not None:

            self.update_database(
                "word", f"group_name='{child_result}'", f"group_name='{origin_name}'")

            display_content = self.query_database(
                "group_name", child_result, "word").fetchall()
            self.ui.manage_groups_log.append(f'[{time.ctime(time.time())}]')
            self.ui.manage_groups_log.append(
                f'开始重命名：{origin_name} --> {child_result}')
            for i in display_content:
                self.ui.manage_groups_log.append(
                    f'单词 {i[3]} 所属词库重命名为 ”{child_result}“')

            self.update_database(
                "group", f"group_name='{child_result}'", f"group_name='{origin_name}'")
            self.ui.manage_groups_log.append(
                f'共有 {len(display_content)} 条记录移动到词库 ”{child_result}“')
            self.ui.manage_groups_log.append(f'重命名词库为 {child_result} 成功')
            self.ui.manage_groups_log.moveCursor(
                self.ui.manage_groups_log.textCursor().End)
            self.alert_message("information", "重命名成功",
                               f'重命名词库为 {child_result} 成功')
            self.update_group_menu()
            self.ui.manage_groups_check_group_box.setCurrentText(child_result)
        else:
            self.alert_message("information", "词库重命名失败", "词库重命名失败！")

    def manage_group_info(self):
        info_name = self.ui.manage_groups_check_group_box.currentText().strip()
        info_create_time = ""
        self.group_names_get()
        groups = self.group_names
        for i in groups:
            if i[1] == info_name:
                info_create_time = i[2]
                break
        time_str = time.strftime(
            "%Y-%m-%d %H:%M", time.localtime(float(info_create_time)))
        # print(time_str)
        display_content = self.query_database(
            "group_name", info_name, "word").fetchall()
        # print(len(display_content))
        self.alert_message("information", "词库 {} 的详细信息".format(info_name),
                           f"词库名称：{info_name}\n创建时间：{time_str}\n词汇数量：{len(display_content)}")
        self.ui.manage_groups_log.append(
            f'[{time.ctime(time.time())}]\n查询词库 ”{info_name}“ 的详细信息：\n    词库名称：{info_name}\n    创建时间：{time_str}\n    词汇数量：{len(display_content)}')
        self.ui.manage_groups_log.moveCursor(
            self.ui.manage_groups_log.textCursor().End)

    def manage_group_add(self):
        add_name = self.ui.manage_groups_check_group_box.currentText().strip()
        # 数据检查与判断
        if add_name == "":
            self.alert_message("warning", "输入的词库名为空", "请输入正确的词库名！")

        insert_str = f"NULL, '{add_name}', '{time.time()}'"
        # print(insert_str)
        self.insert_values_to_database(insert_str, "group")
        self.group_get = self.get_group_name_list_detail()
        self.manage_group_check_group_update()
        self.add_word_init()
        self.manage_word_init()
        self.test_word_init()
        self.ui.manage_groups_check_group_box.clear()
        self.ui.manage_groups_check_group_box.addItems(
            self.get_group_name_list_detail())
        # 弹出框提示
        self.alert_message("information", "添加成功", f"添加词库 “{add_name}” 成功")

        self.ui.manage_groups_log.append(
            f'[{time.ctime(time.time())}] \n添加词库 “{add_name}” 成功')
        self.ui.manage_groups_log.moveCursor(
            self.ui.manage_groups_log.textCursor().End)

    def manage_group_check_group_update(self):
        current_text = self.ui.manage_groups_check_group_box.currentText().strip()
        if current_text in self.group_get:
            self.ui.manage_group_add.setEnabled(False)
            self.ui.manage_group_remove.setEnabled(True)
            self.ui.manage_group_rename.setEnabled(True)
            self.ui.manage_group_info.setEnabled(True)
        elif current_text == "":
            self.ui.manage_group_add.setEnabled(False)
            self.ui.manage_group_remove.setEnabled(False)
            self.ui.manage_group_rename.setEnabled(False)
            self.ui.manage_group_info.setEnabled(False)
        else:
            self.ui.manage_group_add.setEnabled(True)
            self.ui.manage_group_remove.setEnabled(False)
            self.ui.manage_group_rename.setEnabled(False)
            self.ui.manage_group_info.setEnabled(False)

    def get_group_name_list_detail(self):
        self.group_names_get()
        res = []
        for i in self.group_names:
            res.append(str(i[1]))
        return res

    def init_group_manage(self, group_get):
        for i in range(len(group_get)):
            self.ui.manage_groups_check_group_box.addItem(group_get[i])
        self.ui.manage_groups_check_group_box.setCurrentIndex(-1)

        self.completer.setFilterMode(Qt.MatchContains)
        self.completer.setCompletionMode(QCompleter.PopupCompletion)
        self.ui.manage_groups_check_group_box.setCompleter(self.completer)

        self.ui.manage_group_add.setEnabled(False)
        self.ui.manage_group_remove.setEnabled(False)
        self.ui.manage_group_rename.setEnabled(False)
        self.ui.manage_group_info.setEnabled(False)

    @staticmethod
    def set_sheet_style(name='Microsoft YaHei'):
        style = xlwt.XFStyle()
        font = xlwt.Font()
        font.name = name
        font.bold = False
        font.underline = False
        font.italic = False
        style.font = font
        return style

    def save_test_table(self):
        xl = xlwt.Workbook(encoding='utf-8')
        sheet = xl.add_sheet('已测试单词', cell_overwrite_ok=True)
        t_row = self.ui.tested_word_table.rowCount()
        t_col = self.ui.tested_word_table.columnCount()
        title = ["序号", "单词", "词性", "释义", "输入答案", "正确答案", "批改"]
        for i in range(len(title)):
            sheet.write(0, i, title[i], self.set_sheet_style())
        for i in range(t_row):
            sheet.write(i + 1, 0, i + 1, self.set_sheet_style())
            for j in range(t_col):
                # i -> row | j -> column | self.ui.tested_word_table.item(i, j).text()-> content | style -> style
                sheet.write(i + 1, j + 1, self.ui.tested_word_table.item(i,
                                                                         j).text(), self.set_sheet_style())

        filepath, _ = QFileDialog.getSaveFileName(
            self, '保存单词测试记录表格', '/已测试单词.xls', 'xls(*.xls)')
        if filepath != "":
            xl.save(filepath)
            self.alert_message("information", "文件已保存",
                               "单词测试记录表格文件保存在 {}".format(filepath))
        else:
            self.alert_message("warning", "文件保存失败", "未选择文件保存路径！")
        return

    def clear_test_table(self):
        reply = QMessageBox.question(
            self, "清空表格", "确定要清空表格吗？（该操作不可逆）", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.ui.tested_word_table.setRowCount(0)
        elif reply == QMessageBox.No:
            return
        return

    def stop_test(self):
        reply = QMessageBox.question(
            self, "停止测试", "确定要停止测试吗？（确定后无法返回到该测试状态）", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.ui.test_show_chi.clear()
            self.ui.test_show_chi.setEnabled(False)
            self.ui.test_input_eng.setEnabled(False)
            self.ui.submit_test.setEnabled(False)
            self.ui.stop_test.setEnabled(False)
            self.ui.test_group_box.setEnabled(True)
            self.ui.test_word_group_checked_button.setEnabled(True)
        elif reply == QMessageBox.No:
            return
        return

    @staticmethod
    def generate_table_item(color, string):
        if color == "green":
            t = QTableWidgetItem(str(string))
            t.setForeground(Qt.green)
            return t
        elif color == "darkGreen":
            t = QTableWidgetItem(str(string))
            t.setForeground(Qt.darkGreen)
            return t
        elif color == "red":
            t = QTableWidgetItem(str(string))
            t.setForeground(Qt.red)
            return t

    def verify_testing_word(self):
        test_answer = self.ui.test_input_eng.text().strip()
        if not re.match(r'[a-zA-Z]+', test_answer):
            self.alert_message("warning", "输入单词格式有误", "请输入正确的英语单词")
            return
        right_answer = self.testing_word_list[0][3]
        if test_answer == right_answer:
            rowcount = self.ui.tested_word_table.rowCount()
            self.ui.tested_word_table.insertRow(rowcount)
            self.ui.tested_word_table.setItem(rowcount, 0,
                                              self.generate_table_item("darkGreen", self.testing_word_list[0][3]))
            self.ui.tested_word_table.setItem(rowcount, 1,
                                              self.generate_table_item("darkGreen", self.testing_word_list[0][4]))
            self.ui.tested_word_table.setItem(rowcount, 2,
                                              self.generate_table_item("darkGreen", self.testing_word_list[0][5]))
            self.ui.tested_word_table.setItem(
                rowcount, 3, self.generate_table_item("darkGreen", test_answer))
            self.ui.tested_word_table.setItem(
                rowcount, 4, self.generate_table_item("darkGreen", right_answer))
            self.ui.tested_word_table.setItem(
                rowcount, 5, self.generate_table_item("darkGreen", "正确"))
        else:
            rowcount = self.ui.tested_word_table.rowCount()
            self.ui.tested_word_table.insertRow(rowcount)
            self.ui.tested_word_table.setItem(rowcount, 0,
                                              self.generate_table_item("red", self.testing_word_list[0][3]))
            self.ui.tested_word_table.setItem(rowcount, 1,
                                              self.generate_table_item("red", self.testing_word_list[0][4]))
            self.ui.tested_word_table.setItem(rowcount, 2,
                                              self.generate_table_item("red", self.testing_word_list[0][5]))
            self.ui.tested_word_table.setItem(
                rowcount, 3, self.generate_table_item("red", test_answer))
            self.ui.tested_word_table.setItem(
                rowcount, 4, self.generate_table_item("red", right_answer))
            self.ui.tested_word_table.setItem(
                rowcount, 5, self.generate_table_item("red", "错误"))
        self.ui.tested_word_table.scrollToBottom()
        self.ui.test_input_eng.clear()
        if len(self.testing_word_list) > 1:
            self.testing_word_list.pop(0)
            self.publish_test_word()
        else:
            # 单词全部测试完毕
            self.alert_message("information", "单词测试完成", "该词库所有单词测试完毕！")
            self.ui.test_show_chi.clear()
            self.ui.test_show_chi.setEnabled(False)
            self.ui.test_input_eng.setEnabled(False)
            self.ui.submit_test.setEnabled(False)
            self.ui.stop_test.setEnabled(False)
            self.ui.test_group_box.setEnabled(True)
            self.ui.test_word_group_checked_button.setEnabled(True)
        return

    def publish_test_word(self):
        if len(self.testing_word_list) > 0:
            self.ui.test_show_chi.setText(
                f"{self.testing_word_list[0][4]} {self.testing_word_list[0][5]}")
        else:
            self.alert_message("warning", "单词测试完成", "该词库没有单词！")
            self.ui.test_show_chi.clear()
            self.ui.test_show_chi.setEnabled(False)
            self.ui.test_input_eng.setEnabled(False)
            self.ui.submit_test.setEnabled(False)
            self.ui.stop_test.setEnabled(False)
            self.ui.test_group_box.setEnabled(True)
            self.ui.test_word_group_checked_button.setEnabled(True)
        return

    def start_test_word(self):
        test_group = self.ui.test_group_box.currentText()
        self.ui.test_group_box.setEnabled(False)
        self.ui.test_word_group_checked_button.setEnabled(False)
        self.testing_word_list = self.query_database(
            "group_name", test_group, "word").fetchall()
        random.shuffle(self.testing_word_list)
        # print(self.testing_word_list)
        self.ui.test_show_chi.setEnabled(True)
        self.ui.test_input_eng.setEnabled(True)
        self.ui.submit_test.setEnabled(True)
        self.ui.stop_test.setEnabled(True)
        self.publish_test_word()
        return None

    def test_word_init(self):
        self.ui.test_group_box.clear()
        self.group_names_get()
        for i in self.group_names:
            self.ui.test_group_box.addItems([i[1]])
        self.ui.test_show_chi.setEnabled(False)
        self.ui.test_input_eng.setEnabled(False)
        self.ui.submit_test.setEnabled(False)
        self.ui.stop_test.setEnabled(False)
        return

    def reset_pron(self):
        """
        重置添加读音页面输入框
        :return: None
        """
        self.ui.add_pron_word.clear()
        self.ui.add_pron_ame.clear()
        self.ui.add_pron_bre.clear()
        return None

    def submit_pron(self):
        """
        提交输入的发音
        :return: None
        """
        # 获取信息
        set_word = self.ui.add_pron_word.text().strip()
        ame_pron = self.ui.add_pron_ame.text().strip()
        bre_pron = self.ui.add_pron_bre.text().strip()
        # 数据校验
        # 单词不能为空
        if set_word == "":
            self.alert_message("warning", "请输入单词", "请输入英语单词")
            return
        # 单词是否为英语
        if not re.match(r'[a-zA-Z]+', set_word):
            self.alert_message("warning", "请输入单词", "请输入正确的英语单词")
            return
        # 音标不能都为空
        if ame_pron == "" and bre_pron == "":
            self.alert_message("warning", "请输入音标", "音标不能全部为空")
            return
        # 音标格式是否为 /或[+音标部分(没有数字和汉字)+/或]
        if ame_pron != "" and not re.match(r'^[/\[][^\u4E00-\u9FFF\d]+[/\]]$', ame_pron):
            self.alert_message("warning", "音标格式不正确", "美式发音音标不正确")
            return
        if bre_pron != "" and not re.match(r'^[/\[][^\u4E00-\u9FFF\d]+[/\]]$', bre_pron):
            self.alert_message("warning", "音标格式不正确", "英式发音音标不正确")
            return
        # 数据库查重
        q = self.query_database("word", set_word, "pronounce").fetchall()
        if q:
            self.child_pron_existed.set_dialog_value(word=set_word, old_bre=q[0][2], old_ame=q[0][3], new_bre=bre_pron,
                                                     new_ame=ame_pron)
            self.child_pron_existed.exec()
            # 获取用户选择并处理
            s = self.child_pron_existed.get_clicked_status()
            if s == 1:
                # 更新全部
                self.update_database("pronounce", f"pronounce_bre='{bre_pron}',pronounce_ame='{ame_pron}'",
                                     f"word='{set_word}'")
                current_q = self.query_database(
                    "word", set_word, "pronounce").fetchall()
                # 反馈信息
                self.alert_message("information", "更新全部发音", "英式发音：{}\n美式发音：{}".format(
                    current_q[0][2], current_q[0][3]))
            elif s == 2:
                # 更新英式发音
                self.update_database("pronounce", f"pronounce_bre='{bre_pron}'",
                                     f"word='{set_word}'")
                current_q = self.query_database(
                    "word", set_word, "pronounce").fetchall()
                # 反馈信息
                self.alert_message("information", "更新英式发音", "英式发音：{}\n美式发音：{}".format(
                    current_q[0][2], current_q[0][3]))
            elif s == 3:
                # 更新美式发音
                self.update_database("pronounce", f"pronounce_ame='{ame_pron}'",
                                     f"word='{set_word}'")
                current_q = self.query_database(
                    "word", set_word, "pronounce").fetchall()
                # 反馈信息
                self.alert_message("information", "更新美式发音", "英式发音：{}\n美式发音：{}".format(
                    current_q[0][2], current_q[0][3]))
            elif s == 4:
                # 不更新
                current_q = self.query_database(
                    "word", set_word, "pronounce").fetchall()
                # 反馈信息
                self.alert_message("warning", "未更新现有发音", "英式发音：{}\n美式发音：{}".format(
                    current_q[0][2], current_q[0][3]))
                return
        else:
            insert_info = f"NULL,'{set_word}','{bre_pron}','{ame_pron}'"
            self.insert_values_to_database(insert_info, "pronounce")
            current_q = self.query_database(
                "word", set_word, "pronounce").fetchall()
            # 反馈信息
            self.alert_message("information", f"添加单词 {set_word} 的发音",
                               "英式发音：{}\n美式发音：{}".format(current_q[0][2], current_q[0][3]))
        self.reset_pron()

    def set_pron_ame(self):
        """
        设置输入框指针改变时离开美式发音输入框
        :return: None
        """
        self.editing_pron = 2

    def set_pron_bre(self):
        """
        设置输入框指针改变时离开英式发音输入框
        :return: None
        """
        self.editing_pron = 1

    def pron_keyboard_click(self, row, col):
        """
        音标键盘点击事件
        :param row: 点击的单元格行
        :param col: 点击的单元格列
        :return:
        """
        # print(self.ui.add_pron_ame.isModified())
        # 点击键盘前选中的是美式发音
        if self.editing_pron == 2:
            self.ui.add_pron_ame.insert(
                self.ui.pron_keyboard.item(row, col).text())
            self.ui.add_pron_ame.setFocus()
        # 选中英式发音
        else:
            self.ui.add_pron_bre.insert(
                self.ui.pron_keyboard.item(row, col).text())
            self.ui.add_pron_bre.setFocus()

    def init_pron_keyboard(self):
        """
        初始化添加读音页面的屏幕键盘，主要通过列表控件实现，包括设定键盘单元格宽高，居中单元格元素，设置选中时的模式
        :return: None
        """
        # 设置屏幕键盘宽度
        col = self.ui.pron_keyboard.columnCount()
        for index in range(col):
            self.ui.pron_keyboard.setColumnWidth(index, 35)
        # 设置屏幕键盘高度
        row = self.ui.pron_keyboard.rowCount()
        for index in range(row):
            self.ui.pron_keyboard.setRowHeight(index, 35)
        for i in range(row):
            for j in range(col):
                item = self.ui.pron_keyboard.item(i, j)
                item.setTextAlignment(Qt.AlignCenter)
        # 只允许选中单元格
        self.ui.pron_keyboard.setSelectionBehavior(QTableWidget.SelectItems)
        # 只允许选中单个单元格
        self.ui.pron_keyboard.setSelectionMode(QTableWidget.SingleSelection)

    def group_names_get(self):
        """
        为了解决遍历时group_names总是为空的问题，通过此函数重新获取group_names
        :return: None
        """
        self.group_names = self.query_database_without_limits(
            "group").fetchall()
        return

    def add_word_init(self):
        """
        添加单词页面初始化，主要包括为下拉菜单填充内容
        :return: None
        """
        self.ui.group_box.clear()
        self.group_names_get()
        for i in self.group_names:
            self.ui.group_box.addItems([i[1]])
        return

    def manage_word_init(self):
        """
        管理单词页面初始化，主要包括为下拉菜单填充内容
        :return: None
        """
        self.ui.manage_word_check_group.clear()
        self.ui.manage_word_check_group.addItem("无限制")
        self.group_names_get()
        for i in self.group_names:
            # print(i)
            self.ui.manage_word_check_group.addItems([i[1]])
        return

    def search_word(self):
        """
        点击按钮后查询单词
        :return: None
        """
        search_word = self.ui.search_box.text()
        checked_mode = self.ui.search_mode.checkedButton().text()
        # 匹配单词格式是否正确
        m = re.match(r'[A-Za-z]+', search_word)
        result = []
        if m:
            if checked_mode == '联网查询':
                result = queryWords.QueryWords().query_words(search_word, self)
                if result == -1:
                    return None
                self.activateWindow()

            elif checked_mode == '本地查询':
                self.append_word_and_pronunciation_to_result(
                    result, search_word)
        else:
            result = search_word
        # result列表是否为空或格式是否正确
        if result and isinstance(result, list):
            self.ui.result_search_box.clear()
            self.ui.result_search_box.addItems(result)
        elif not result:
            self.alert_message("warning", '查询错误', '未查询到该单词！')
        else:
            self.alert_message("critical", '查询错误', '请输入正确的英语单词！')

    def reset_search(self):
        """
        重置查询单词tab页的显示内容
        :return: None
        """
        self.ui.search_box.clear()
        self.ui.result_search_box.clear()
        self.ui.search_web.setChecked(True)

    def manage_word_box_display(self, display_content):
        for i in display_content:
            rowcount = self.ui.manage_word_show_box.rowCount()
            # print(rowcount)
            self.ui.manage_word_show_box.insertRow(rowcount)
            self.ui.manage_word_show_box.setItem(
                rowcount, 0, QTableWidgetItem(str(i[2])))
            self.ui.manage_word_show_box.setItem(
                rowcount, 1, QTableWidgetItem(str(i[3])))
            self.ui.manage_word_show_box.setItem(
                rowcount, 2, QTableWidgetItem(str(i[4])))
            self.ui.manage_word_show_box.setItem(
                rowcount, 3, QTableWidgetItem(str(i[5])))

    def manage_word_display(self):
        """
        点击按钮后显示指定词库内的单词
        :return: None
        """
        mode = self.ui.manage_word_check_group.currentText()
        self.ui.manage_word_show_box.setRowCount(0)
        if mode == "无限制":
            display_content = self.query_database_without_limits(
                "word").fetchall()
            # print(f"display_content:{display_content}")
            self.manage_word_box_display(display_content)
        else:
            display_content = self.query_database(
                "group_name", mode, "word").fetchall()
            self.manage_word_box_display(display_content)

    def add_word(self):
        """
        获取并添加单词
        :return: None
        """
        add_word_group = self.ui.group_box.currentText()
        english_spelling = self.ui.eng_input.text().strip()
        chinese_spelling = self.ui.chi_input.text().strip()
        add_word_part = re.sub(
            "[\u4e00-\u9fa5]", "", self.ui.part_box.currentText()).replace(" ", "")
        # 数据的校验与筛查
        m = re.match(r'[A-Za-z]+', english_spelling)
        if not m:
            self.alert_message("warning", '添加单词失败', '请输入正确的英语单词')
            return None
        if len(chinese_spelling) == 0:
            self.alert_message("warning", '添加单词失败', '请输入正确的中文翻译')
            return None

        # self.c.show_dialog()
        # 子窗口确认添加的单词信息
        self.child_confirm_add_word.set_words(
            english_spelling, add_word_group, add_word_part, chinese_spelling)
        self.child_confirm_add_word.exec()

        # 获取弹出子窗口案件的返回值
        if self.child_confirm_add_word.get_status():
            # 子窗口返回成功
            self.group_names_get()
            add_word_group_id = 0
            for i in self.group_names:
                if i[1] == add_word_group:
                    add_word_group_id = i[0]
                    break
            insert_str = f"NULL, {add_word_group_id}, '{add_word_group}', '{english_spelling}', '{add_word_part}', '{chinese_spelling}'"
            self.insert_values_to_database(insert_str, "word")
            self.alert_message(
                "information", f'添加单词 {english_spelling} 成功', f'单词 {english_spelling} 添加成功')
            # 成功则重置添加单词输入框
            self.reset_add_word()
        else:
            # 子窗口返回失败
            self.alert_message(
                "warning", f'添加单词 {english_spelling} 失败', f'单词 {english_spelling} 添加失败')

        # 在右侧窗口中显示单词
        result = []
        self.append_word_and_pronunciation_to_result(result, english_spelling)

        self.ui.word_add_show_box.setText(english_spelling)

        if result and isinstance(result, list):
            self.ui.chi_box.clear()
            self.ui.chi_box.addItems(result)
        elif not result:
            self.ui.chi_box.addItems([f'没有关于 {english_spelling} 的记录'])

    def append_word_and_pronunciation_to_result(self, result, english_spelling):
        origin_res = self.query_database(
            "word", english_spelling, "word").fetchall()
        pronounce_res = self.query_database(
            "word", english_spelling, "pronounce").fetchall()
        pro_str = ""
        if pronounce_res:
            for i in pronounce_res:
                if i[2]:
                    pro_str += "英 {} ".format(i[2])
                if i[3]:
                    pro_str += "美 {} ".format(i[3])
            if pro_str:
                result.append(pro_str)
        for i in origin_res:
            # result 列表添加字符串 词性 + 空格 + 中文翻译
            result.append(f'({i[2]}) {i[4]} {i[5]}')

    def closeEvent(self, event):
        # 窗口关闭时提交并关闭数据库
        self.close_database()

    def alert_message(self, mode, title, content):
        """
        弹出指定内容、形式的提示框
        :param mode: 提示框模式
        :param title: 提示框标题
        :param content: 提示框内容
        :return: None
        """
        if mode == "warning":
            QMessageBox.warning(
                self,
                title,
                content)
        elif mode == "critical":
            QMessageBox.critical(
                self,
                title,
                content)
        elif mode == "information":
            QMessageBox.information(
                self,
                title,
                content)
        else:
            raise Exception("alert_message mode error")

    def reset_add_word(self):
        """
        重置添加单词的输入框页面
        :return: None
        """
        self.ui.eng_input.clear()
        self.ui.chi_input.clear()


if __name__ == '__main__':
    wdAsstApp = QApplication(sys.argv)
    wdAsstWindow = MainWindow()
    wdAsstWindow.show()
    sys.exit(wdAsstApp.exec_())
