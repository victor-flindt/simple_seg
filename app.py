import sys
from open3d import geometry
import open3d as o3d
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QDialog, QApplication, QMainWindow, QMenuBar, QMenu, QAction, QVBoxLayout, QWidget, QFileDialog, QShortcut, QComboBox
from PyQt5.QtWidgets import QGridLayout, QDialogButtonBox, QLabel
from PyQt5.QtGui import QKeySequence, QWindow
import win32gui  # Used to access window handle (hwnd)
from pathlib import Path


class VisualizeFormatDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Set the dialog window properties
        self.setWindowTitle("Visualize Format")
        self.setGeometry(200, 200, 300, 150)
        
        # Layout for the dialog
        layout = QVBoxLayout(self)

        # Add a label
        self.label = QLabel("Select the visualization format for .ply files:", self)
        layout.addWidget(self.label)

        # Create a dropdown (QComboBox)
        self.combo_box = QComboBox(self)
        self.combo_box.addItem("Point Cloud")
        self.combo_box.addItem("Triangle Mesh")
        layout.addWidget(self.combo_box)

        # Add OK/Cancel buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

        # Store the selected visualization type
        self.visualization_type = None

    def get_selected_visualization(self):
        # Return the selected type (either "Point Cloud" or "Triangle Mesh")
        return self.combo_box.currentText()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.selected_file = Path("")
        self.visualization_type = "Point Cloud"  # Default visualization type

        # Set up the main window properties
        self.setWindowTitle("Open3D with PyQt")
        self.setGeometry(100, 100, 800, 600)

        # Create a central widget and set it as the main widget
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Create a layout for the central widget
        layout = QGridLayout(central_widget)

        # Keybindings
        self.keybind_closemain = QShortcut(QKeySequence("Ctrl+W"), self)
        self.keybind_closemain.activated.connect(self.close_main_window)

        # Set up Open3D Visualizer
        self.vis = o3d.visualization.Visualizer()
        self.vis.create_window(window_name="Open3D", width=800, height=600, visible=True)

        # Get the window handle of the Open3D window
        hwnd = win32gui.FindWindowEx(0, 0, None, "Open3D")

        # Create a QWindow from the Open3D window handle and embed it in the Qt window
        self.window = QWindow.fromWinId(hwnd)
        self.windowcontainer = self.createWindowContainer(self.window, central_widget)

        # Add the Open3D window container to the Qt layout
        layout.addWidget(self.windowcontainer, 0, 0)

        # Set up a timer to continuously update Open3D visualization
        timer = QTimer(self)
        timer.timeout.connect(self.update_vis)
        timer.start(16)  # Updates every 16 ms (roughly 60 FPS)
        
        # Setup the menu bar / ribbon bar
        self.setup_menu_bar()

    def setup_menu_bar(self):
        # Create the menu bar
        menu_bar = self.menuBar()

        # Create the "File" menu
        file_menu = menu_bar.addMenu("File")
        open_action = QAction("Open", self)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close_main_window)
        file_menu.addAction(exit_action)

        clear_model_view_action = QAction("Clear model view", self)
        clear_model_view_action.triggered.connect(self.vis.clear_geometries)
        file_menu.addAction(clear_model_view_action)

        # Create the "Options" menu
        options_menu = menu_bar.addMenu("Options")
        
        # Add "Visualize Format" option to the menu
        visualize_format_action = QAction("Visualize Format", self)
        visualize_format_action.triggered.connect(self.show_visualize_format_dialog)
        options_menu.addAction(visualize_format_action)

    def show_visualize_format_dialog(self):
        dialog = VisualizeFormatDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.visualization_type = dialog.get_selected_visualization()
            print(f"Visualization type selected: {self.visualization_type}")

    def select_file(self):
        file_dialog = QFileDialog(self)
        file_dialog.setWindowTitle("Open File")
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        file_dialog.setViewMode(QFileDialog.ViewMode.Detail)

        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            self.selected_file = Path(selected_files[0])

    def update_vis(self):
        # This will update the Open3D visualization (polling events and rendering)
        self.vis.poll_events()
        self.vis.update_renderer()

    def close_main_window(self):
        # Close the Open3D visualizer and the Qt window
        self.vis.destroy_window()
        self.close()

    def open_file(self):
        self.select_file()
        if self.selected_file.suffix == ".ply":
            self.load_ply_file()

    def load_ply_file(self):        
        if self.visualization_type == "Point Cloud":
            pcd = o3d.io.read_point_cloud(str(self.selected_file))
            self.vis.add_geometry(pcd)
        elif self.visualization_type == "Triangle Mesh":
            mesh = o3d.io.read_triangle_mesh(str(self.selected_file))
            self.vis.add_geometry(mesh)

    def draw_bounding_box(self):
        bbox = o3d.geometry.AxisAlignedBoundingBox()        
        return 1


# Main function to run the PyQt app
def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
