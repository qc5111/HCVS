import threading
import globalVar
from PyQt5 import QtCore
from PyQt5.QtGui import QCursor

import ServerAPI
import UI
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox, QTableWidget, QMenu
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QThread, pyqtSignal, Qt
import os
import time

import config
import hash_chain
import public


# 显示UI.Ui_MainWindow
class MyMainWindow(QMainWindow, UI.Ui_MainWindow):
    tabList = []
    tabWidgetList = []

    def __init__(self):
        super(MyMainWindow, self).__init__()
        self.setupUi(self)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.tableWidget.setEditTriggers(QTableWidget.NoEditTriggers)  # 禁止编辑
        self.tableWidget.setContextMenuPolicy(Qt.CustomContextMenu)  # 允许右键产生子菜单
        self.tableWidget.customContextMenuRequested.connect(self.showContextMenu)  # 绑定右键菜单
        # 按钮事件注册
        self.refreshButton.clicked.connect(self.refresh)
        self.pathSelectButton.clicked.connect(self.selectPath)
        # 读取配置文件
        configs = config.getConfig()
        self.lineEdit.setText(configs["Data"]["path"])
        # 启动各种线程
        # 启动时间同步线程
        syncTimeStopFlag = threading.Event()  # 用于停止线程
        thread1 = ServerAPI.syncGlobalTime(syncTimeStopFlag)
        syncUserListStopFlag = threading.Event()  # 用于停止线程
        thread2 = ServerAPI.syncUserList(syncUserListStopFlag, self)
        test = threading.Event()  # 用于停止线程
        thread3 = ServerAPI.syncVoteData(test, self, 17)
        # 测试读取一个raw
        with open(r"C:\Users\24773\HCVS_Verifier\data\VoteRaw\17.bin", "rb") as f:
            raw = f.read()
        print(raw)
        print(hash_chain.verifyVote(raw))

        self.refresh()
        # hash_chain.calcVote(18)

    def showContextMenu(self, pos):
        # 获取所选行的索引
        selected_row = self.tableWidget.rowAt(pos.y())

        if selected_row >= 0:
            # 创建菜单
            menu = QMenu(self)
            if self.tableWidget.item(selected_row, 8).text() == "Yes":
                track_action = menu.addAction("Untrack")
                track_action.triggered.connect(lambda: self.unTrack(selected_row))
            else:
                track_action = menu.addAction("Track")
                track_action.triggered.connect(lambda: self.track(selected_row))
            recalculate_action = menu.addAction("Recalculate")
            recalculate_action.triggered.connect(lambda: self.reCalc(selected_row))
            recalculate_action = menu.addAction("Find User")
            recalculate_action.triggered.connect(lambda: self.findUser(selected_row))

            # 显示菜单
            menu.popup(QCursor.pos())

    def track(self, row):
        # 获取row行的id
        id = self.tableWidget.item(row, 0).text()
        # 设置该行的track状态为Yes
        self.tableWidget.setItem(row, 8, QtWidgets.QTableWidgetItem("Yes"))
        print(id)

    def unTrack(self, row):
        # 获取row行的id
        id = self.tableWidget.item(row, 0).text()
        # 设置该行的track状态为No
        self.tableWidget.setItem(row, 8, QtWidgets.QTableWidgetItem("No"))
        print(id)

    def reCalc(self, row):
        print("reCalc", row)

    def findUser(self, row):
        print("findUser", row)

    def selectPath(self):
        # 选择文件夹
        path = QFileDialog.getExistingDirectory(self, "Select Data Folder", self.lineEdit.text())
        # 判断该文件夹是否存在
        if not os.path.exists(path):
            return
        # print(path)
        self.lineEdit.setText(path)
        # 保存配置文件
        config.setConfig("Data", "path", path)

    def refresh(self):
        ServerData = ServerAPI.getVoteList()
        configs = config.getConfig()
        if ServerData is None:
            # 错误提示并将其设置为红色
            self.serverStatusLabel.setText("Connection failed")
            self.serverStatusLabel.setStyleSheet("color:red")
            return
        self.serverStatusLabel.setText("Online")
        self.serverStatusLabel.setStyleSheet("color:green")
        self.updateTimeLable.setText(public.mtsToDateTime(ServerData["ServerTime"]))
        # 清空表格
        self.tableWidget.clearContents()
        self.tableWidget.setRowCount(0)
        # 重新添加表格内容
        self.tableWidget.setRowCount(len(ServerData["voteList"]))
        for i in range(len(ServerData["voteList"])):
            # print(ServerData["voteList"][i]["id"])
            self.tableWidget.setItem(i, 0, QtWidgets.QTableWidgetItem(str(ServerData["voteList"][i]["id"])))  # id
            self.tableWidget.setItem(i, 1, QtWidgets.QTableWidgetItem(ServerData["voteList"][i]["name"]))  # name
            self.tableWidget.setItem(i, 2, QtWidgets.QTableWidgetItem(
                public.mtsToDateTime(ServerData["voteList"][i]["start_time"])))  # startTime
            self.tableWidget.setItem(i, 3, QtWidgets.QTableWidgetItem(
                public.mtsToDateTime(ServerData["voteList"][i]["end_time"])))  # endTime
            self.tableWidget.setItem(i, 4, QtWidgets.QTableWidgetItem(
                str(ServerData["voteList"][i]["min_choice"]) + "/" + str(
                    ServerData["voteList"][i]["max_choice"])))  # min/max
            # 根据开始时间和结束时间判断状态，和时间颜色
            if ServerData["voteList"][i]["start_time"] > ServerData["ServerTime"]:
                self.tableWidget.setItem(i, 5, QtWidgets.QTableWidgetItem("Not started"))
                self.tableWidget.item(i, 5).setForeground(QtGui.QBrush(QtGui.QColor(255, 0, 0)))  # 红色
            elif ServerData["voteList"][i]["end_time"] < ServerData["ServerTime"]:
                self.tableWidget.setItem(i, 5, QtWidgets.QTableWidgetItem("Ended"))
                self.tableWidget.item(i, 5).setForeground(QtGui.QBrush(QtGui.QColor(0, 0, 255)))  # 蓝色
            else:
                self.tableWidget.setItem(i, 5, QtWidgets.QTableWidgetItem("In progress"))
                self.tableWidget.item(i, 5).setForeground(QtGui.QBrush(QtGui.QColor(0, 255, 0)))  # 绿色
            self.tableWidget.setItem(i, 6, QtWidgets.QTableWidgetItem(
                str(ServerData["voteList"][i]["chain_height"])))  # chainHeight
            # 判断本地是否存在该投票的配置
            # 根据本地配置文件判断是否跟踪
            if configs["Vote_"+str(ServerData["voteList"][i]["id"])] == "1":
                self.tableWidget.setItem(i, 8, QtWidgets.QTableWidgetItem("Yes"))
            else:
                self.tableWidget.setItem(i, 8, QtWidgets.QTableWidgetItem("No"))



if __name__ == '__main__':
    # 初始化UI
    app = QApplication(sys.argv)
    myWin = MyMainWindow()
    myWin.show()
    sys.exit(app.exec_())
