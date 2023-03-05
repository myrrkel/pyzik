from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import (
    QLineEdit,
    QWidget,
    QHBoxLayout,
    QSpinBox,
    QSizePolicy,
    QLabel,
)


class LabeledWidget(QWidget):
    def __init__(self, parent=None, name='', label=''):
        QWidget.__init__(self, parent=parent)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.label = QLabel(self)
        self.label.setText(label)
        size_policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        self.label.setSizePolicy(size_policy)
        self.label.setAlignment(Qt.AlignLeading | Qt.AlignLeft | Qt.AlignVCenter)
        self.layout.addWidget(self.label)


class LineEditLabeledWidget(LabeledWidget):
    def __init__(self, parent=None, name='', label=''):
        LabeledWidget.__init__(self, parent=parent, name=name, label=label)
        self.line_edit = QLineEdit(self)

        size_policy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        size_policy.setHorizontalStretch(100)
        size_policy.setVerticalStretch(0)
        self.line_edit.setSizePolicy(size_policy)
        self.line_edit.setMinimumSize(QSize(50, 27))
        self.line_edit.setMaximumSize(QSize(16777215, 17000))
        self.layout.addWidget(self.line_edit)


class SpinBoxLabeledWidget(LabeledWidget):
    def __init__(self, parent=None, name='', label=''):
        LabeledWidget.__init__(self, parent=parent, name=name, label=label)
        self.spin_box = QSpinBox(self)

        size_policy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(100)
        self.spin_box.setSizePolicy(size_policy)
        self.spin_box.setMinimum(0)
        self.spin_box.setMaximum(9999)
        self.spin_box.setSingleStep(1)
        self.spin_box.setMinimumSize(QSize(70, 27))
        self.spin_box.setMaximumSize(QSize(70, 40))
        self.layout.addWidget(self.spin_box)
