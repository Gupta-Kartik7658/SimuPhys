import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QVBoxLayout,
    QStackedWidget, QHBoxLayout
)

class MainMenu(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Physics Lab Simulator", self))

        btn_classical = QPushButton("Classical Mechanics")
        btn_classical.clicked.connect(lambda: stacked_widget.setCurrentIndex(1))

        layout.addWidget(btn_classical)
        self.setLayout(layout)


class DomainPage(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Choose Simulation:"))

        projectile_btn = QPushButton("Projectile Motion")
        projectile_btn.clicked.connect(lambda: stacked_widget.setCurrentIndex(2))

        layout.addWidget(projectile_btn)

        back_btn = QPushButton("Back")
        back_btn.clicked.connect(lambda: stacked_widget.setCurrentIndex(0))
        layout.addWidget(back_btn)

        self.setLayout(layout)


class SimulationPage(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Simulation Config (Placeholder)"))

        run_btn = QPushButton("Run Simulation (Not Implemented)")
        layout.addWidget(run_btn)

        back_btn = QPushButton("Back to Sim List")
        back_btn.clicked.connect(lambda: stacked_widget.setCurrentIndex(1))
        layout.addWidget(back_btn)

        self.setLayout(layout)


class PhysicsSimulatorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Physics Simulation Software")

        self.stacked_widget = QStackedWidget()
        self.stacked_widget.addWidget(MainMenu(self.stacked_widget))      # Index 0
        self.stacked_widget.addWidget(DomainPage(self.stacked_widget))    # Index 1
        self.stacked_widget.addWidget(SimulationPage(self.stacked_widget))# Index 2

        layout = QVBoxLayout()
        layout.addWidget(self.stacked_widget)
        self.setLayout(layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PhysicsSimulatorApp()
    window.resize(500, 400)
    window.show()
    sys.exit(app.exec_())







