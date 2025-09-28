from PyQt5.QtCore import Qt, pyqtSignal, QEvent
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QComboBox, QListWidget, QLineEdit, QListWidgetItem, QCheckBox
import re

class MultiSelectComboBox(QComboBox):
    # 自定义信号
    selectionChange = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.hidden_flag_ = True
        self.show_flag_ = False
        # self.selected_items = []
        
        self.initControl()
        
    def initControl(self):
        # 初始化控件
        self.list_widget_ = QListWidget()
        self.line_edit_ = QLineEdit()
        self.search_bar_ = QLineEdit()

        # 设置搜索框
        current_item = QListWidgetItem(self.list_widget_)
        self.search_bar_.setPlaceholderText("Search.........")
        self.search_bar_.setClearButtonEnabled(True)
        self.list_widget_.addItem(current_item)
        self.list_widget_.setItemWidget(current_item, self.search_bar_)

        # 添加“全选”复选框
        self.checkAll = QCheckBox("全选")
        self.checkAll.setChecked(True)
        current_item = QListWidgetItem(self.list_widget_)
        self.list_widget_.addItem(current_item)
        self.list_widget_.setItemWidget(current_item, self.checkAll)

        # 设置文本框
        self.line_edit_.setReadOnly(True)
        self.line_edit_.installEventFilter(self)
        self.line_edit_.setStyleSheet("QLineEdit:disabled{background:rgb(233,233,233);}")

        # 设置 QComboBox 的视图和模型
        self.setModel(self.list_widget_.model())
        self.setView(self.list_widget_)
        self.setLineEdit(self.line_edit_)

        # 信号槽连接
        self.search_bar_.textChanged.connect(self.onSearch)
        # 全选信号与槽
        self.checkAll.released.connect(self.toggle_all_items)
        self.activated.connect(self.itemClicked)
    
    def toggle_all_items(self):
        """全选复选框的槽函数"""
        is_checked = self.checkAll.isChecked()
        for i in range(self.list_widget_.count()):
            check_box = self.list_widget_.itemWidget(self.list_widget_.item(i))
            if isinstance(check_box, QCheckBox):  # 确保是 QCheckBox
                check_box.setChecked(is_checked)

    def check_all_state(self, state):
        """单项与全选状态的更新逻辑"""
        if state == Qt.Unchecked:
            self.checkAll.setChecked(False)
        elif state == Qt.Checked:
            is_all_checked = True
            for i in range(2, self.list_widget_.count()):
                check_box = self.list_widget_.itemWidget(self.list_widget_.item(i))
                if isinstance(check_box, QCheckBox) and not check_box.isChecked():
                    is_all_checked = False
                    break
            self.checkAll.setChecked(is_all_checked)
    
    def hidePopup(self):
        """隐藏下拉框"""
        self.show_flag_ = False
        width = self.width()
        height = self.height()
        x = QCursor.pos().x() - self.mapToGlobal(self.geometry().topLeft()).x() + self.geometry().x()
        y = QCursor.pos().y() - self.mapToGlobal(self.geometry().topLeft()).y() + self.geometry().y()
        if x < 0 or x > width or y < self.height() or y > height + self.height():
            super().hidePopup()

    def addItem(self, _text, _variant=None):
        """添加一条选项"""
        item = QListWidgetItem(self.list_widget_)
        checkbox = QCheckBox(self)
        checkbox.setText(_text)
        self.list_widget_.addItem(item)
        self.list_widget_.setItemWidget(item, checkbox)
        checkbox.setChecked(True)
        checkbox.stateChanged.connect(self.stateChange)
        # 连接单项复选框与状态更新的信号与槽
        checkbox.stateChanged.connect(self.check_all_state)

    def addItems(self, _text_list):
        """添加多条选项"""
        for text in _text_list:
            self.addItem(text)

    def currentText(self):
        """返回当前选中选项"""
        text_list = []
        if self.line_edit_.text():
            text_list = self.line_edit_.text().split(':')
        return text_list

    def count(self):
        """返回当前选项条数"""
        count = self.list_widget_.count() - 1
        return max(count, 0)

    def SetSearchBarPlaceHolderText(self, _text):
        """设置搜索框默认文字"""
        self.search_bar_.setPlaceholderText(_text)

    def SetPlaceHolderText(self, _text):
        """设置文本框默认文字"""
        self.line_edit_.setPlaceholderText(_text)

    def ResetSelection(self):
        """下拉框状态恢复默认"""
        count = self.list_widget_.count()
        for i in range(1, count):
            widget = self.list_widget_.itemWidget(self.list_widget_.item(i))
            if isinstance(widget, QCheckBox):
                widget.setChecked(False)

    def delete_all_slot(self):
        counter = self.list_widget_.count()
        print("count is", counter)

        # 从后向前删除项
        for index in range(counter - 1, -1, -1):  # 从最后一个项开始删除
            item = self.list_widget_.takeItem(index)  # 获取并删除指定索引的项
            if item is not None:
                del item  # 删除项
            print("index is", index)


    def clear(self):
        """清空所有内容"""
        # self.line_edit_.clear()
        # self.list_widget_.clear()
        # current_item = QListWidgetItem(self.list_widget_)
        # self.search_bar_.setPlaceholderText("Search.........")
        # self.search_bar_.setClearButtonEnabled(True)
        # self.list_widget_.addItem(current_item)
        # self.list_widget_.setItemWidget(current_item, self.search_bar_)
        # self.SetSearchBarHidden(self.hidden_flag_)
        # self.search_bar_.textChanged.connect(self.onSearch)

        self.initControl()
        

    def TextClear(self):
        """文本框内容清空"""
        self.line_edit_.clear()
        self.ResetSelection()

    def setCurrentText(self, _text):
        """设置选中文本--单"""
        count = self.list_widget_.count()
        for i in range(1, count):
            widget = self.list_widget_.itemWidget(self.list_widget_.item(i))
            if isinstance(widget, QCheckBox) and widget.text() == _text:
                widget.setChecked(True)

    def setCurrentTextList(self, _text_list):
        """设置选中文本--多"""
        count = self.list_widget_.count()
        for i in range(1, count):
            widget = self.list_widget_.itemWidget(self.list_widget_.item(i))
            if isinstance(widget, QCheckBox) and widget.text() in _text_list:
                widget.setChecked(True)

    def SetSearchBarHidden(self, _flag):
        """设置搜索框是否禁用"""
        self.hidden_flag_ = _flag
        self.list_widget_.item(0).setHidden(self.hidden_flag_)

    def eventFilter(self, watched, event):
        """事件过滤器"""
        if watched == self.line_edit_ and event.type() == QEvent.MouseButtonRelease and self.isEnabled():
            self.showPopup()
            return True
        return False

    def wheelEvent(self, event):
        """滚轮事件"""
        event.ignore()

    def keyPressEvent(self, event):
        """按键事件"""
        super().keyPressEvent(event)

    def stateChange(self, _row):
        """文本框文本变化"""
        selected_data = ""
        count = self.list_widget_.count()
        for i in range(1, count):
            widget = self.list_widget_.itemWidget(self.list_widget_.item(i))
            if isinstance(widget, QCheckBox) and widget.isChecked():
                selected_data += widget.text() + ";"
        selected_data = selected_data.rstrip(';')
        if selected_data:
            self.line_edit_.setText(selected_data)
        else:
            self.line_edit_.clear()
        
        self.selected_items = []
        it_match = re.finditer(r"\[(\d+)\]",selected_data) 
        for mt in it_match:
            self.selected_items.append(int(mt.group(1)))

        self.line_edit_.setToolTip(selected_data)
        self.selectionChange.emit(selected_data)

    def onSearch(self, _text):
        """搜索框文本变化"""
        for i in range(1, self.list_widget_.count()):
            checkbox = self.list_widget_.itemWidget(self.list_widget_.item(i))
            if isinstance(checkbox, QCheckBox):
                if _text.lower() in checkbox.text().lower():
                    self.list_widget_.item(i).setHidden(False)
                else:
                    self.list_widget_.item(i).setHidden(True)

    def itemClicked(self, _index):
        """点击下拉框选项"""
        if _index != 0:
            checkbox = self.list_widget_.itemWidget(self.list_widget_.item(_index))
            if isinstance(checkbox, QCheckBox):
                checkbox.setChecked(not checkbox.isChecked())
