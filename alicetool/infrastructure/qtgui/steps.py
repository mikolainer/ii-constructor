from PySide6.QtCore import (
    Qt,
    Slot,
    Signal,
    QObject,
    QPoint,
    QModelIndex,
    QPersistentModelIndex,
    QSize,
    QAbstractItemModel,
)

from PySide6.QtGui import (
    QPainter,
)

from PySide6.QtWidgets import (
    QListView,
    QWidget,
    QStyledItemDelegate,
    QStyleOptionViewItem,
    QVBoxLayout,
    QLabel,
)

from alicetool.infrastructure.qtgui.data import ItemData, CustomDataRole, BaseModel, SynonymsSetModel
from alicetool.infrastructure.qtgui.primitives.sceneitems import Arrow, SceneNode
from alicetool.infrastructure.qtgui.synonyms import SynonymsSetView

class StepModel(BaseModel):
    __arrow: Arrow
    __node_from: SceneNode
    __node_to: SceneNode
    
    ''' Модель стрелочки на сцене '''
    def __init__( self, arrow, from_node, to_node, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self.__arrow = arrow
        self.__node_from = from_node
        self.__node_to = to_node

        self._data_init(index_roles= [ CustomDataRole.SynonymsSet ] )

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

    def __init__(self, synonyms_set_model:SynonymsSetModel, parent: QWidget = None):
        super().__init__(parent)

        self.__synonyms_set = SynonymsSetView(self)
        self.__synonyms_set.setModel(synonyms_set_model)
        
        main_lay = QVBoxLayout(self)
        main_lay.setContentsMargins(0,0,0,0)
        main_lay.setSpacing(0)
        main_lay.addWidget(QLabel('Набор синонимов', self))
        main_lay.addWidget(self.__synonyms_set)

class StepInputSetDelegate(QStyledItemDelegate):
    ''' Реализация части MVC фреймворка Qt для набора синонимов в группе '''
    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex) -> None:
        data = index.data(CustomDataRole.SynonymsSet)
        wgt = StepInputWidget(data)
        wgt.resize(option.rect.size())

        painter.setClipRect(option.rect)

        painter.save()
        painter.drawPixmap(option.rect, wgt.grab())
        painter.restore()

        super().paint(painter, option, index)

    def sizeHint(self, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex) -> QSize:
        data = index.data(CustomDataRole.SynonymsSet)
        wgt = StepInputWidget(data)
        wgt.adjustSize()
        return wgt.size()

class StepInputSetView(QListView):
    ''' Реализация части MVC фреймворка Qt для набора синонимов в группе '''
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setSelectionBehavior(QListView.SelectionBehavior.SelectItems)
        self.setSelectionMode(QListView.SelectionMode.SingleSelection)
        self.__delegate = StepInputSetDelegate(self)
        self.setItemDelegate(self.__delegate)
        self.setVerticalScrollMode(self.ScrollMode.ScrollPerPixel)
