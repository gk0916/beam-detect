# detect_main_ui.py
import os
import sys
import logging
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QStandardItemModel, QIcon  
from PyQt5.QtWidgets import QHeaderView
from PyQt5.QtCore import pyqtSignal, QObject

from .svg_icon import SvgIconProvider
from .MultiSelectComboBox import MultiSelectComboBox


# ========== 图标路径函数 ==========
def icon_path(name):
    """返回正确的图标路径（基于当前文件位置）"""
    ui_dir = os.path.dirname(os.path.abspath(__file__))  # 当前文件所在目录（ui/）
    return os.path.join(ui_dir, "icons", name + ".svg").replace("\\", "/")


# ==================== 日志 Handler ====================
class QtHandler(logging.Handler, QObject):
    log_signal = pyqtSignal(str, str)  # 日志消息 + 日志级别

    def __init__(self):
        logging.Handler.__init__(self)
        QObject.__init__(self)

    def emit(self, record):
        msg = self.format(record)
        level = record.levelname
        self.log_signal.emit(msg, level)


# ==================== 动态变色按钮封装 ====================
class StyledButton(QtWidgets.QPushButton):
    def __init__(self, text, icon_path, parent=None, default_color="black", hover_color="white", click_color="white"):
        super().__init__(text, parent)
        self.icon_path = icon_path
        self.default_color = default_color
        self.hover_color = hover_color
        self.click_color = click_color
        self.is_pressed = False

        self.setIcon(SvgIconProvider.get_icon(icon_path, default_color, 24))
        self.setIconSize(QtCore.QSize(24, 24))
        self.setMouseTracking(True)

        # 初始化图标颜色
        self.update_icon_color()

    def update_icon_color(self):
        """根据按钮启用状态更新图标颜色"""
        if self.isEnabled():
            self.set_icon("white")  # 可选时为白色
        else:
            self.set_icon("black")  # 不可选时为黑色

    def set_icon(self, color):
        icon = SvgIconProvider.get_icon(self.icon_path, color, 24)
        self.setIcon(icon)

    def setEnabled(self, enabled):
        """重写 setEnabled 方法，更新图标颜色"""
        super().setEnabled(enabled)
        self.update_icon_color()

    def enterEvent(self, event):
        if self.isEnabled():
            self.set_icon(self.hover_color)
        super().enterEvent(event)

    def leaveEvent(self, event):
        if not self.is_pressed:
            self.update_icon_color()  # 离开时根据启用状态更新颜色
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if self.isEnabled() and event.button() == QtCore.Qt.LeftButton:
            self.is_pressed = True
            self.set_icon(self.click_color)
            self.setIconSize(QtCore.QSize(22, 22))
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if self.isEnabled() and event.button() == QtCore.Qt.LeftButton:
            self.is_pressed = False
            self.setIconSize(QtCore.QSize(24, 24))
            local_pos = self.mapFromGlobal(event.globalPos())
            if self.rect().contains(local_pos):
                self.set_icon(self.hover_color)
            else:
                self.update_icon_color()
        super().mouseReleaseEvent(event)


    
# ==================== 主界面 UI ====================
class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1920, 1080)
        MainWindow.setWindowIcon(QIcon(icon_path('camera-ai-fill')))

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout_4.setObjectName("gridLayout_4")

        # ---------------- 左侧（相机 + 图像显示） ----------------
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        
        self.ComboDevices = MultiSelectComboBox(self.centralwidget)
        self.ComboDevices.setMinimumSize(QtCore.QSize(580, 32))
        self.ComboDevices.setObjectName("ComboDevices")
        self.verticalLayout_3.addWidget(self.ComboDevices)

        self.pictureView = QtWidgets.QLabel(self.centralwidget)
        self.pictureView.setMinimumSize(QtCore.QSize(580, 480))
        self.pictureView.setStyleSheet("background-color: black")
        self.pictureView.setScaledContents(True)
        self.verticalLayout_3.addWidget(self.pictureView)

        self.horizontalLayout_2.addLayout(self.verticalLayout_3)

        # ---------------- 右侧功能区 ----------------
        self.gridLayout_5 = QtWidgets.QGridLayout()

        # 相机控制
        self.groupCamera = QtWidgets.QGroupBox(self.centralwidget)
        self.groupCamera.setObjectName("groupCamera")
        self.hLayoutCamera = QtWidgets.QHBoxLayout(self.groupCamera)

        self.bnEnum = StyledButton(" 查找相机", icon_path("search"), self.groupCamera)
        self.bnOpen = StyledButton(" 打开相机", icon_path("camera-on"), self.groupCamera)
        self.bnClose = StyledButton(" 关闭相机", icon_path("camera-off"), self.groupCamera)
        
        for btn in [self.bnEnum, self.bnOpen, self.bnClose]:
            btn.setMinimumHeight(40)
            self.hLayoutCamera.addWidget(btn)

        self.gridLayout_5.addWidget(self.groupCamera, 0, 0, 1, 1)

        # 图像检测
        self.groupDetect = QtWidgets.QGroupBox(self.centralwidget)
        self.groupDetect.setObjectName("groupDetect")
        self.vLayoutDetect = QtWidgets.QVBoxLayout(self.groupDetect)

        # 第一行：Label + ComboBox
        self.hLayoutTop = QtWidgets.QHBoxLayout()
        self.modelLabel = QtWidgets.QLabel(self.centralwidget)
        self.modelLabel.setFixedWidth(110)
        self.ComboModels = QtWidgets.QComboBox(self.centralwidget)
        self.ComboModels.setObjectName("comModels")

        self.hLayoutTop.addWidget(self.modelLabel)
        self.hLayoutTop.addWidget(self.ComboModels, 1)

        # 第二行：Start + Stop
        self.hLayoutBottom = QtWidgets.QHBoxLayout()
        self.bnStart = StyledButton(" 开始检测", icon_path("start"), self.groupDetect)
        self.bnStop = StyledButton(" 停止检测", icon_path("stop"), self.groupDetect)

        for btn in [self.bnStart, self.bnStop]:
            btn.setMinimumHeight(40)
            self.hLayoutBottom.addWidget(btn)

        self.vLayoutDetect.addLayout(self.hLayoutTop)
        self.vLayoutDetect.addLayout(self.hLayoutBottom)
        self.gridLayout_5.addWidget(self.groupDetect, 1, 0, 1, 1)

        # 检测结果
        self.groupResult = QtWidgets.QGroupBox(self.centralwidget)
        self.groupResult.setObjectName("groupResult")
        self.vLayoutResult = QtWidgets.QVBoxLayout(self.groupResult)

        self.resultTable = QtWidgets.QTableView(self.groupResult)
        self.resultTable.setMinimumHeight(250)
        self.resultTable.setStyleSheet("font-size: 22px;")
        self.resultTable.verticalHeader().setVisible(False)

        self.resultModel = QStandardItemModel(0, 4)
        self.resultModel.setHorizontalHeaderLabels(['检测任务', '梁编号', '气泡数', '裂缝数'])
        self.resultTable.setModel(self.resultModel)

        self.resultTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.resultTable.horizontalHeader().setMinimumSectionSize(80)

        self.vLayoutResult.addWidget(self.resultTable)
        self.gridLayout_5.addWidget(self.groupResult, 2, 0, 1, 1)

        self.horizontalLayout_2.addLayout(self.gridLayout_5)
        self.horizontalLayout_2.setStretch(0, 3)
        self.horizontalLayout_2.setStretch(1, 1)

        self.gridLayout_4.addLayout(self.horizontalLayout_2, 0, 0, 1, 1)

        # ---------------- 日志输出（可折叠） ----------------
        self.groupLog = QtWidgets.QWidget(self.centralwidget)
        self.vLayoutLog = QtWidgets.QVBoxLayout(self.groupLog)
        self.vLayoutLog.setContentsMargins(0, 0, 0, 0)
        self.vLayoutLog.setSpacing(0)

        # 日志内容和工具栏容器
        self.logContainer = QtWidgets.QWidget()
        self.vLayoutLogContainer = QtWidgets.QVBoxLayout(self.logContainer)
        self.vLayoutLogContainer.setContentsMargins(0, 0, 0, 0)
        self.vLayoutLogContainer.setSpacing(0)

        # 日志工具栏（折叠按钮 + 右侧控件）
        self.hLayoutLogTools = QtWidgets.QHBoxLayout()
        self.hLayoutLogTools.setContentsMargins(3, 3, 3, 3)
        self.hLayoutLogTools.setSpacing(5)

        # 折叠/展开按钮
        self.btnToggleLog = QtWidgets.QToolButton()
        self.btnToggleLog.setStyleSheet("QToolButton { border: none; font-size: 16px; }")
        self.btnToggleLog.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.btnToggleLog.setArrowType(QtCore.Qt.DownArrow)  # 默认展开
        self.btnToggleLog.setText(" 日志")
        self.btnToggleLog.setCheckable(True)
        self.btnToggleLog.setChecked(True)

        # 右侧日志控件
        self.levelLabel = QtWidgets.QLabel("日志级别:")
        self.levelLabel.setObjectName("levelLabel")
        self.logLevelBox = QtWidgets.QComboBox()
        self.logLevelBox.addItems(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        self.logLevelBox.setCurrentText("INFO")
        self.logLevelBox.setObjectName("logLevelBox")
        self.btnClearLog = QtWidgets.QPushButton("清空日志")
        self.btnClearLog.setObjectName("btnClearLog")

        # 左右布局
        self.hLayoutLogTools.addWidget(self.btnToggleLog, alignment=QtCore.Qt.AlignLeft)
        self.hLayoutLogTools.addStretch()
        self.hLayoutLogTools.addWidget(self.levelLabel)
        self.hLayoutLogTools.addWidget(self.logLevelBox)
        self.hLayoutLogTools.addWidget(self.btnClearLog)

        # 工具栏加入容器
        self.vLayoutLogContainer.addLayout(self.hLayoutLogTools)

        # 日志输出内容
        self.logOutput = QtWidgets.QPlainTextEdit()
        self.logOutput.setReadOnly(True)
        self.logOutput.setStyleSheet("font-size: 18px; background-color: #F5F5F5; color: #000;")
        self.logOutput.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)

        # 设置日志输出最大高度
        self.logOutput.setMaximumHeight(300)

        self.vLayoutLogContainer.addWidget(self.logOutput)

        # 添加到日志总布局
        self.vLayoutLog.addWidget(self.logContainer)

        self.gridLayout_4.addWidget(self.groupLog, 1, 0, 1, 1)
        self.gridLayout_4.setRowStretch(0, 1)  # 上半部分优先填充
        self.gridLayout_4.setRowStretch(1, 0)  # 日志区不拉伸

        # 折叠/展开逻辑
        def toggle_log_content(checked):
            self.logOutput.setVisible(checked)
            self.btnToggleLog.setArrowType(QtCore.Qt.DownArrow if checked else QtCore.Qt.RightArrow)

        self.btnToggleLog.toggled.connect(toggle_log_content)



        self.gridLayout_4.addWidget(self.groupLog, 1, 0, 1, 1)
        self.gridLayout_4.setRowStretch(0, 3)
        self.gridLayout_4.setRowStretch(1, 1)

        MainWindow.setCentralWidget(self.centralwidget)

        # ---------------- 日志绑定 ----------------
        self.log_handler = QtHandler()
        self.log_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
        self.log_handler.log_signal.connect(self.append_log)

        # file_handler = logging.FileHandler("logs/app.log", encoding="utf-8")
        # file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))

        logging.getLogger().addHandler(self.log_handler)
        # logging.getLogger().addHandler(file_handler)
        logging.getLogger().setLevel(logging.INFO)

        # 日志级别切换
        self.logLevelBox.currentTextChanged.connect(self.change_log_level)
        self.btnClearLog.clicked.connect(self.clear_log)

        # 初始化控件状态
        self.ComboModels.setEnabled(True)
        self.bnOpen.setEnabled(False)
        self.bnClose.setEnabled(False)
        self.bnStart.setEnabled(False)
        self.bnStop.setEnabled(False)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        

        # ---------------- AI 科技风格 QSS ----------------
        MainWindow.setStyleSheet(f"""
            QWidget {{
                font-family: "Microsoft YaHei";
                font-size: 22px;
                background-color: #F8F9FA;
                color: #2C3E50;
            }}
            QGroupBox {{
                font-weight: bold;
                border: 2px solid #DDE3EA;
                border-radius: 12px;
                margin-top: 16px;
                padding: 16px;
                background-color: #FFFFFF;
                font-size: 22px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 16px;
                padding: 0 10px;
                color: #0D8BF0;
                font-size: 22px;
            }}
            QPushButton {{
                background-color: #0D8BF0;
                color: white;
                border-radius: 10px;
                padding: 14px 24px;
                font-size: 22px;
                font-weight: bold;
                border: none;
                min-height: 52px;
            }}
            QPushButton:hover {{
                background-color: #33AFFF;
            }}
            QPushButton:pressed {{
                background-color: #0A6BC2;
            }}
            QPushButton:disabled {{
                background-color: #E0E6ED;
                color: #A0AAB4;
            }}
            QTableView {{
                border: 2px solid #DDE3EA;
                background: #FFFFFF;
                gridline-color: #E6EBF2;
                selection-background-color: #0D8BF0;
                selection-color: white;
                alternate-background-color: #F7FAFC;
                font-size: 22px;
            }}
            QHeaderView::section {{
                background-color: #F0F4F9;
                border: 2px solid #DDE3EA;
                padding: 12px;
                font-weight: bold;
                font-size: 22px;
                color: #0D8BF0;
            }}
            QStatusBar {{
                background: #FFFFFF;
                color: #2C3E50;
                font-size: 20px;
                border-top: 2px solid #DDE3EA;
            }}
            QComboBox {{
                border: 2px solid #DEE2E6;
                border-radius: 10px;
                padding: 12px 16px;
                background: white;
                color: #495057;
                font-size: 24px;
                min-height: 42px;
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 28px;
                border: none;
                background: transparent;
                padding-right: 12px;
            }}
            QComboBox::down-arrow {{
                image: url("{icon_path('arrow-drop-down')}");
                width: 38px;
                height: 48px;
            }}
            QComboBox QAbstractItemView {{
                border: 2px solid #E9ECEF;
                background: white;
                selection-background-color: #E9ECEF;
                selection-color: #495057;
            }}
            QListWidget {{
                border: 2px solid #E9ECEF;
                border-radius: 10px;
                background: #FFFFFF;
                font-size: 22px;
                color: #495057;
                padding: 8px;
                alternate-background-color: #F8F9FA;
            }}
            QListWidget::item {{
                padding: 12px;
                border-radius: 8px;
                height: 60px;
                color: #495057;
            }}
            QListWidget::item:selected {{
                background-color: #E9ECEF;
                color: #212529;
                font-weight: bold;
            }}
            QListWidget::item:hover {{
                background-color: #F1F3F5;
            }}
            QLineEdit {{
                border: 2px solid #D0D7E0;
                border-radius: 10px;
                padding: 6px 16px;
                background: #FFFFFF;
                font-size: 22px;
                color: #2C3E50;
                min-height: 38px;
            }}
            QLineEdit:focus {{
                border: 2px solid #ADB5BD;
                background: #FFFFFF;
            }}
            QLineEdit:disabled {{
                background-color: #F8F9FA;
                color: #ADB5BD;
            }}
            QLineEdit#camera_list {{
                padding: 2px 12px;
                padding-right: 2px;
                border: none;
                background: #F1F3F5;
            }}
            QLineEdit#camera_list:focus {{
                border: none;
            }}
            QCheckBox {{
                spacing: 12px;
                font-size: 24px;
                color: #495057;
                min-height: 40px;
            }}
            QCheckBox::indicator {{
                width: 28px;
                height: 28px;
                border: 2px solid #CED4DA;
                border-radius: 6px;
                background: #FFFFFF;
            }}
            QCheckBox::indicator:checked {{
                background-color: #6C757D;
                border: 2px solid #6C757D;
            }}
            QCheckBox::indicator:disabled {{
                background: #E9ECEF;
                border: 2px solid #CED4DA;
            }}
            QCheckBox:disabled {{
                color: #ADB5BD;
            }}
            QScrollBar:vertical {{
                border: none;
                background: #F1F3F5;
                width: 16px;
                margin: 0px;
                border-radius: 8px;
            }}
            QScrollBar::handle:vertical {{
                background: #CED4DA;
                border-radius: 8px;
                min-height: 40px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: #ADB5BD;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QTabWidget::pane {{
                border: 2px solid #E9ECEF;
                border-radius: 10px;
                background: #FFFFFF;
            }}
            QTabBar::tab {{
                background: #F8F9FA;
                border: 2px solid #E9ECEF;
                border-bottom: none;
                padding: 12px 24px;
                color: #6C757D;
                font-size: 22px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }}
            QTabBar::tab:selected {{
                background: #FFFFFF;
                color: #495057;
                font-weight: bold;
            }}
            QTabBar::tab:hover {{
                background: #F1F3F5;
            }}
            #groupLog {{
                margin-top: 0px;
                padding: 8px;
            }}
            #levelLabel {{
                font-size: 16px;
                min-height: 32px;
                max-height: 32px;
                padding: 0px;
            }}
            #logLevelBox {{
                font-size: 16px;
                min-height: 32px;
                max-height: 32px;
                padding: 2px 6px;
            }}
            #btnClearLog {{
                background-color: #D6D8DB;
                color: #495057;
                font-size: 16px;
                min-height: 32px;
                max-height: 32px;
                padding: 2px 10px;
            }}
            #btnClearLog:hover {{
                background-color: #C8CBCE;
            }}
            #btnClearLog:pressed {{
                background-color: #ADB1B5;
            }}
        """)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "预制梁外观质量缺陷检测"))
        self.groupCamera.setTitle(_translate("MainWindow", "相机控制"))
        self.groupDetect.setTitle(_translate("MainWindow", "图像检测"))
        self.groupResult.setTitle(_translate("MainWindow", "检测记录"))
        self.modelLabel.setText(_translate("MainWindow", "选择模型："))
        # self.groupLog.setTitle(_translate("MainWindow", "日志输出"))

    def append_log(self, msg, level):
        """在日志窗口显示日志，不同级别不同颜色"""
        color_map = {
            "DEBUG": "#808080",
            "INFO": "#000000",
            "WARNING": "#FFA500",
            "ERROR": "#FF0000",
            "CRITICAL": "#800000"
        }
        color = color_map.get(level, "#000000")
        self.logOutput.appendHtml(f'<span style="color:{color};">{msg}</span>')
        self.logOutput.verticalScrollBar().setValue(self.logOutput.verticalScrollBar().maximum())

    def change_log_level(self, level):
        """切换日志级别"""
        logging.getLogger().setLevel(getattr(logging, level))
        self.append_log(f"日志级别切换为 {level}", "INFO")

    def clear_log(self):
        """清空日志窗口"""
        self.logOutput.clear()