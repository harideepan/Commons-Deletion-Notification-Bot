import sys
import _thread

from PyQt5.QtWidgets import QMainWindow, QApplication

import CommonsDeletionNotificationBotModule1
import CommonsDeletionNotificationBotModule2
import CommonsDeletionNotificationBotModule3
import CommonsDeletionNotificationBotUI


class AppWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = CommonsDeletionNotificationBotUI.Ui_MainWindow()
        self.ui.setupUi(self)
        self.show()
        self.ui.pushButton_1.clicked.connect(self.notify_about_deletion_nomination)
        self.ui.pushButton_2.clicked.connect(self.notify_about_deletion)
        self.ui.pushButton_3.clicked.connect(self.notify_about_kept_images)

        self.ui.pushButton_4.clicked.connect(self.stop_module1)
        self.ui.pushButton_5.clicked.connect(self.stop_module2)
        self.ui.pushButton_6.clicked.connect(self.stop_module3)

        self.ui.pushButton_4.setDisabled(True)
        self.ui.pushButton_5.setDisabled(True)
        self.ui.pushButton_6.setDisabled(True)

    def notify_about_deletion_nomination(self):
        self.ui.pushButton_1.setDisabled(True)
        self.ui.pushButton_2.setDisabled(True)
        self.ui.pushButton_3.setDisabled(True)
        self.ui.pushButton_4.setDisabled(False)
        _thread.start_new_thread(CommonsDeletionNotificationBotModule1.parse_category,
                                 (self.ui, "Deletion requests", "Deletion requests", "DR"))

    def notify_about_deletion(self):
        self.ui.pushButton_1.setDisabled(True)
        self.ui.pushButton_2.setDisabled(True)
        self.ui.pushButton_3.setDisabled(True)
        self.ui.pushButton_5.setDisabled(False)
        _thread.start_new_thread(CommonsDeletionNotificationBotModule2.notify_articles, (self.ui,))

    def notify_about_kept_images(self):
        self.ui.pushButton_1.setDisabled(True)
        self.ui.pushButton_2.setDisabled(True)
        self.ui.pushButton_3.setDisabled(True)
        self.ui.pushButton_6.setDisabled(False)
        _thread.start_new_thread(CommonsDeletionNotificationBotModule3.parse_category,
                                 (self.ui, "Deletion requests/kept"))

    def stop_module1(self):
        CommonsDeletionNotificationBotModule1.stop(self.ui)

    def stop_module2(self):
        CommonsDeletionNotificationBotModule2.stop(self.ui)

    def stop_module3(self):
        CommonsDeletionNotificationBotModule3.stop(self.ui)


app = QApplication(sys.argv)
w = AppWindow()
w.setMinimumSize(700, 500)
sys.exit(app.exec_())