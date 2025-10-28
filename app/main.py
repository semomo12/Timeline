
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QCoreApplication
from PySide6.QtCore import Qt
from core.logic.main_controller import MainController

QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts, True)

def main():
    """Runs the Timeline application."""
   
    app = QApplication(sys.argv)
    app.setApplicationName("Timeline")
    app.setApplicationVersion("1.0.0")

    # Create main controller, which sets up everything
    controller = MainController()
    controller.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()