# pylint: disable=all
import numpy as np

from AnyQt.QtCore import Qt, QPoint
from AnyQt.QtGui import QPalette, QColor
from AnyQt.QtTest import QTest
from AnyQt.QtWidgets import QGraphicsScene, QGraphicsView

from orangewidget.tests.utils import mouseMove
from orangewidget.tests.base import GuiTest

from Orange.clustering import hierarchical
from Orange.widgets.utils.dendrogram import DendrogramWidget


T = hierarchical.Tree
C = hierarchical.ClusterData
S = hierarchical.SingletonData


def t(h: float, left: T, right: T):
    return T(C((left.value.first, right.value.last), h), (left, right))


def leaf(r, index):
    return T(S((r, r + 1), 0.0, index))


class TestDendrogramWidget(GuiTest):
    def setUp(self) -> None:
        super().setUp()
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.resize(300, 300)
        self.widget = DendrogramWidget()
        self.scene.addItem(self.widget)

    def tearDown(self) -> None:
        self.scene.clear()
        del self.widget
        super().tearDown()

    def test_widget(self):
        w = self.widget
        w.set_root(t(0.0, leaf(0, 0), leaf(1, 1)))
        w.resize(w.effectiveSizeHint(Qt.PreferredSize))
        h = w.height_at(QPoint())
        self.assertEqual(h, 0)
        h = w.height_at(QPoint(10, 0))
        self.assertEqual(h, 0)

        self.assertEqual(w.pos_at_height(0).x(), w.rect().x())
        self.assertEqual(w.pos_at_height(1).x(), w.rect().x())

        height = np.finfo(float).eps
        w.set_root(t(height, leaf(0, 0), leaf(1, 1)))

        h = w.height_at(QPoint())
        self.assertEqual(h, height)
        h = w.height_at(QPoint(int(w.size().width()), 0))
        self.assertEqual(h, 0)

        self.assertEqual(w.pos_at_height(0).x(), w.rect().right())
        self.assertEqual(w.pos_at_height(height).x(), w.rect().left())

        view = self.view
        view.grab()  # ensure w is laid out
        root = w.root()
        rootitem = w.item(root)
        r = view.mapFromScene(rootitem.sceneBoundingRect()).boundingRect()
        # move/hover over the item
        mouseMove(view.viewport(), r.center())
        self.assertEqual(w._highlighted_item, rootitem)
        # click select
        QTest.mouseClick(view.viewport(), Qt.LeftButton, Qt.NoModifier, r.center())
        self.assertTrue(w.isItemSelected(rootitem))
        p = r.topLeft() + QPoint(-3, -3)  # just out of the item
        mouseMove(view.viewport(), p)
        self.assertEqual(w._highlighted_item, None)

    def test_update_palette(self):
        w = self.widget
        w.set_root(t(1.0, leaf(0, 0), leaf(1, 1)))
        w.setSelectedClusters([w.root()])
        p = QPalette()
        p.setColor(QPalette.All, QPalette.WindowText, QColor(Qt.red))
        w.setPalette(p)
        item = w.item(w.root())
        self.assertEqual(item.pen().color(), p.color(QPalette.WindowText))
