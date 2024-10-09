# Этот файл — часть "Конструктора интерактивных инструкций".
#
# Конструктор интерактивных инструкций — свободная программа:
# вы можете перераспространять ее и/или изменять ее на условиях
# Стандартной общественной лицензии GNU в том виде,
# в каком она была опубликована Фондом свободного программного обеспечения;
# либо версии 3 лицензии, либо (по вашему выбору) любой более поздней версии.
# Конструктор интерактивных инструкций распространяется в надежде,
# что она будет полезной, но БЕЗО ВСЯКИХ ГАРАНТИЙ;
# даже без неявной гарантии ТОВАРНОГО ВИДА
# или ПРИГОДНОСТИ ДЛЯ ОПРЕДЕЛЕННЫХ ЦЕЛЕЙ.
# Подробнее см. в Стандартной общественной лицензии GNU.
#
# Вы должны были получить копию Стандартной общественной лицензии GNU
# вместе с этой программой. Если это не так,
# см. <https://www.gnu.org/licenses/>.


from PySide6.QtCore import (
    QModelIndex,
    QObject,
    QPersistentModelIndex,
    QSize,
    Qt,
)
from PySide6.QtGui import QKeySequence, QPainter, QShortcut
from PySide6.QtWidgets import (
    QDialog,
    QHeaderView,
    QLabel,
    QStyledItemDelegate,
    QStyleOptionViewItem,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from .data import BaseModel, CustomDataRole, SynonymsSetModel
from .primitives.sceneitems import Arrow, SceneNode
from .synonyms import SynonymsSetView


class StepModel(BaseModel):
    __arrow: Arrow
    __node_from: SceneNode
    __node_to: SceneNode

    """ Модель стрелочки на сцене """

    def __init__(
        self,
        arrow,
        from_node,
        to_node,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)

        self.__arrow = arrow
        self.__node_from = from_node
        self.__node_to = to_node

        self._data_init(index_roles=[CustomDataRole.SynonymsSet])

    def flags(self, index: QModelIndex | QPersistentModelIndex) -> Qt.ItemFlag:
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable

    def arrow(self) -> Arrow:
        return self.__arrow

    def node_from(self) -> SceneNode:
        return self.__node_from

    def node_to(self) -> SceneNode:
        return self.__node_to


class StepInputWidget(QWidget):
    __synonyms_set: SynonymsSetView
    __name_label: QLabel

    def __init__(
        self,
        synonyms_set_model: SynonymsSetModel,
        parent: QWidget = None,
    ) -> None:
        super().__init__(parent)

        self.__name_label = QLabel("Набор синонимов", self)

        self.__synonyms_set = SynonymsSetView(self)
        self.__synonyms_set.setModel(synonyms_set_model)

        main_lay = QVBoxLayout(self)
        main_lay.setContentsMargins(0, 0, 0, 0)
        main_lay.setSpacing(0)
        main_lay.addWidget(self.__name_label, 1)
        main_lay.addWidget(self.__synonyms_set, 0)

    def sizeHint(self) -> QSize:
        size = super().sizeHint()
        size.setHeight(
            self.__name_label.height()
            + self.__synonyms_set.sizeHint().height(),
        )
        return size


class StepInputSetDelegate(QStyledItemDelegate):
    """Реализация части MVC фреймворка Qt для набора синонимов в группе"""

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        data = index.data(CustomDataRole.SynonymsSet)
        wgt = StepInputWidget(data)
        wgt.resize(option.rect.size())

        painter.setClipRect(option.rect)

        super().paint(painter, option, index)
        painter.save()
        painter.drawPixmap(option.rect, wgt.grab())
        painter.restore()

    def sizeHint(
        self,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> QSize:
        data = index.data(CustomDataRole.SynonymsSet)
        wgt = StepInputWidget(data)
        wgt.adjustSize()
        return wgt.size()


class StepInputSetView(QTableView):
    """Реализация части MVC фреймворка Qt для набора синонимов в группе"""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setSelectionBehavior(QTableView.SelectionBehavior.SelectItems)
        self.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self.__delegate = StepInputSetDelegate(self)
        self.setItemDelegate(self.__delegate)
        self.setVerticalScrollMode(self.ScrollMode.ScrollPerPixel)

        self.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch,
        )
        self.horizontalHeader().hide()

        self.verticalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents,
        )
        # self.verticalHeader().hide()

        shotcut = QShortcut(QKeySequence.StandardKey.Delete, self)
        shotcut.activated.connect(self.remove_selected_row)

    def remove_selected_row(self):
        for index in self.selectedIndexes():
            self.model().removeRow(index.row())


class StepEditor(QDialog):
    __model: StepModel

    def __init__(
        self,
        model: StepModel,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("Просмотр связи")

        self.__model = model

        view = StepInputSetView(self)
        view.setModel(self.__model)

        main_lay = QVBoxLayout(self)
        main_lay.addWidget(view)

        self.__model.rowsRemoved.connect(
            lambda parent_idx, first, last: self.__auto_close(),
        )

    def __auto_close(self):
        if len(self.__model) == 0:
            self.close()
