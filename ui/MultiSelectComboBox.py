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
        
        self.initControl()
    
    def initControl(self):
        # 初始化控件
        self.list_widget_ = QListWidget()
        self.line_edit_ = QLineEdit()
        self.line_edit_.setObjectName("camera_list")
        self.search_bar_ = QLineEdit()

        # 设置搜索框
        current_item = QListWidgetItem(self.list_widget_)
        self.search_bar_.setObjectName("search")
        self.search_bar_.setPlaceholderText("Search.........")
        self.search_bar_.setClearButtonEnabled(True)
        self.list_widget_.addItem(current_item)
        self.list_widget_.setItemWidget(current_item, self.search_bar_)

        # 添加"全选"复选框
        self.checkAll = QCheckBox("全选")
        self.checkAll.setStyleSheet("""
            QCheckBox {
                spacing: 18px;
                font-size: 24px;
                color: #2C3E50;
                height: 38px;
            }
        """)
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
        self.checkAll.stateChanged.connect(self.toggle_all_items)
        self.activated.connect(self.itemClicked)
    
    def toggle_all_items(self, state):
        """全选复选框的槽函数（批量设置时屏蔽单项信号）"""
        checked = (state == Qt.Checked)
        # 批量设置每个子复选框，屏蔽单项信号以避免重复/重入
        for i in range(2, self.list_widget_.count()):  # 从索引2开始，跳过搜索框和全选复选框
            item = self.list_widget_.item(i)
            if item:
                check_box = self.list_widget_.itemWidget(item)
                if isinstance(check_box, QCheckBox):
                    check_box.blockSignals(True)
                    check_box.setChecked(checked)
                    check_box.blockSignals(False)
        
        # 批量完成后统一刷新显示与全选态（update_check_all_state 内部屏蔽了 self.checkAll 的信号）
        self.update_text_display()
        self.update_check_all_state()

    def update_check_all_state(self):
        """更新全选复选框的状态（修改 self.checkAll 时屏蔽其信号，避免回路）"""
        total_count = 0
        checked_count = 0
        
        for i in range(2, self.list_widget_.count()):
            item = self.list_widget_.item(i)
            if item:
                check_box = self.list_widget_.itemWidget(item)
                if isinstance(check_box, QCheckBox):
                    total_count += 1
                    if check_box.isChecked():
                        checked_count += 1
        
        # 在设置 self.checkAll 状态时屏蔽它的信号，防止再次触发 toggle_all_items
        self.checkAll.blockSignals(True)
        if total_count == 0:
            self.checkAll.setCheckState(Qt.Unchecked)
        elif checked_count == total_count:
            self.checkAll.setCheckState(Qt.Checked)
        else:
            self.checkAll.setCheckState(Qt.PartiallyChecked)
        self.checkAll.blockSignals(False)

    # def hidePopup(self):
    #     """隐藏下拉框"""
    #     self.show_flag_ = False
    #     width = self.width()
    #     height = self.height()
    #     x = QCursor.pos().x() - self.mapToGlobal(self.geometry().topLeft()).x() + self.geometry().x()
    #     y = QCursor.pos().y() - self.mapToGlobal(self.geometry().topLeft()).y() + self.geometry().y()
    #     if x < 0 or x > width or y < self.height() or y > height + self.height():
    #         super().hidePopup()

    def hidePopup(self):
        cursor_pos = QCursor.pos()
        rect = self.view().geometry()
        rect.moveTo(self.view().mapToGlobal(rect.topLeft()))
        if rect.contains(cursor_pos):
            return
        super().hidePopup()

    def addItem(self, _text, _variant=None):
        """添加一条选项"""
        item = QListWidgetItem(self.list_widget_)
        checkbox = QCheckBox(self)
        checkbox.setText(_text)
        checkbox.setStyleSheet("""
            QCheckBox {
                spacing: 18px;
                font-size: 24px;
                color: #2C3E50;
                height: 38px;
            }
        """)
        self.list_widget_.addItem(item)
        self.list_widget_.setItemWidget(item, checkbox)
        # 初始设置时屏蔽信号，避免触发多次更新
        checkbox.blockSignals(True)
        checkbox.setChecked(True)
        checkbox.blockSignals(False)
        # 连接信号（后续状态变化才会触发）
        checkbox.stateChanged.connect(self.update_text_display)
        checkbox.stateChanged.connect(self.update_check_all_state)
        
        # 更新全选状态与文本显示（统一调用一次）
        self.update_check_all_state()
        self.update_text_display()

    def addItems(self, _text_list):
        """添加多条选项"""
        for text in _text_list:
            self.addItem(text)

    def currentText(self):
        """返回当前选中选项"""
        text_list = []
        if self.line_edit_.text():
            text_list = self.line_edit_.text().split(';')
        return text_list

    def count(self):
        """返回当前选项条数"""
        count = self.list_widget_.count() - 2  # 减去搜索框和全选复选框
        return max(count, 0)

    def SetSearchBarPlaceHolderText(self, _text):
        """设置搜索框默认文字"""
        self.search_bar_.setPlaceholderText(_text)

    def SetPlaceHolderText(self, _text):
        """设置文本框默认文字"""
        self.line_edit_.setPlaceholderText(_text)

    def ResetSelection(self):
        """下拉框状态恢复默认（批量修改时屏蔽单项信号）"""
        for i in range(2, self.list_widget_.count()):  # 从索引2开始，跳过搜索框和全选复选框
            widget = self.list_widget_.itemWidget(self.list_widget_.item(i))
            if isinstance(widget, QCheckBox):
                widget.blockSignals(True)
                widget.setChecked(False)
                widget.blockSignals(False)
        
        # 更新全选状态与文本显示
        self.update_check_all_state()
        self.update_text_display()

    def clear(self):
        """清空所有内容"""
        # 保留搜索框和全选复选框，只删除其他项目
        for i in range(self.list_widget_.count() - 1, 1, -1):  # 从最后一项开始删除，保留前两项
            self.list_widget_.takeItem(i)
        
        # 更新文本框显示
        self.update_text_display()

    def TextClear(self):
        """文本框内容清空"""
        self.line_edit_.clear()
        self.ResetSelection()

    def setCurrentText(self, _text):
        """设置选中文本--单（批量屏蔽信号再更新）"""
        for i in range(2, self.list_widget_.count()):
            widget = self.list_widget_.itemWidget(self.list_widget_.item(i))
            if isinstance(widget, QCheckBox) and widget.text() == _text:
                widget.blockSignals(True)
                widget.setChecked(True)
                widget.blockSignals(False)
                break
        
        # 更新全选状态
        self.update_check_all_state()
        # 更新文本框显示
        self.update_text_display()

    def setCurrentTextList(self, _text_list):
        """设置选中文本--多（批量屏蔽信号再更新）"""
        for i in range(2, self.list_widget_.count()):
            widget = self.list_widget_.itemWidget(self.list_widget_.item(i))
            if isinstance(widget, QCheckBox):
                widget.blockSignals(True)
                widget.setChecked(widget.text() in _text_list)
                widget.blockSignals(False)
        
        # 更新全选状态
        self.update_check_all_state()
        # 更新文本框显示
        self.update_text_display()

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

    def update_text_display(self):
        """更新文本框显示，不包含'全选'字样"""
        selected_data = ""
        # 从索引2开始，跳过搜索框和全选复选框
        for i in range(2, self.list_widget_.count()):
            widget = self.list_widget_.itemWidget(self.list_widget_.item(i))
            if isinstance(widget, QCheckBox) and widget.isChecked():
                selected_data += widget.text() + ";"
        
        selected_data = selected_data.rstrip(';')
        if selected_data:
            self.line_edit_.setText(selected_data)
        else:
            self.line_edit_.clear()
        
        self.selected_items = []
        it_match = re.finditer(r"\[(\d+)\]", selected_data) 
        for mt in it_match:
            self.selected_items.append(int(mt.group(1)))

        self.line_edit_.setToolTip(selected_data)
        self.selectionChange.emit(selected_data)

    # 保留stateChange方法作为update_text_display的别名，以兼容旧代码
    def stateChange(self, _row=None):
        """兼容旧代码的方法别名"""
        self.update_text_display()

    def onSearch(self, _text):
        """搜索框文本变化"""
        # 搜索时保持搜索框可见
        self.list_widget_.item(0).setHidden(False)  # 搜索框

        # 根据搜索文本决定是否显示全选复选框
        if _text.strip():  # 搜索框有内容时隐藏全选
            self.list_widget_.item(1).setHidden(True)
        else:  # 搜索框为空时显示全选
            self.list_widget_.item(1).setHidden(False)
        
        # 过滤其他项目
        for i in range(2, self.list_widget_.count()):
            checkbox = self.list_widget_.itemWidget(self.list_widget_.item(i))
            if isinstance(checkbox, QCheckBox):
                if _text.lower() in checkbox.text().lower():
                    self.list_widget_.item(i).setHidden(False)
                else:
                    self.list_widget_.item(i).setHidden(True)
        
        # 更新全选状态（基于所有项目，不限于可见项目）
        self.update_check_all_state()


    def itemClicked(self, _index):
        """点击下拉框选项"""
        if _index == 1:  # 全选复选框行
            # 如果当前全选是部分选中或未选中，则点击后变为全选
            new_state = Qt.Checked if self.checkAll.checkState() != Qt.Checked else Qt.Unchecked
            self.checkAll.setCheckState(new_state)
            # 直接调用 toggle_all_items 更新所有子项和文本框
            self.toggle_all_items(new_state)
            return
        elif _index >= 2:  # 普通选项
            checkbox = self.list_widget_.itemWidget(self.list_widget_.item(_index))
            if isinstance(checkbox, QCheckBox):
                checkbox.blockSignals(True)
                checkbox.setChecked(not checkbox.isChecked())
                checkbox.blockSignals(False)
                
                self.update_check_all_state()
                self.update_text_display()


