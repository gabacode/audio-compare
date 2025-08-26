from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class PlotCanvas(FigureCanvas):
    """Matplotlib canvas for displaying spectrum plots."""

    def __init__(self, parent=None):
        self.fig = Figure(figsize=(6, 3), dpi=100)
        self.axes = self.fig.add_subplot(111)
        super().__init__(self.fig)
        self.setParent(parent)
        self.fig.tight_layout(pad=2.0)
