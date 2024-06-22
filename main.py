import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QFileDialog, QComboBox, QCheckBox, QMessageBox
from PyQt5.QtCore import Qt
import pathlib
from PIL import Image, ImageColor
import random

# import from snapshotter.py
from snapshotter import (
    get_world_names, get_map_names, create_snapshot, save_snapshot,
    post_to_discord_webhook, is_discord_available
)

class SnapshotGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Dynmap Snapshotter')
        layout = QVBoxLayout()

        # folder selection
        folder_layout = QHBoxLayout()
        self.folder_input = QLineEdit()
        folder_button = QPushButton('Browse')
        folder_button.clicked.connect(self.browse_folder)
        folder_layout.addWidget(QLabel('Tiles Directory:'))
        folder_layout.addWidget(self.folder_input)
        folder_layout.addWidget(folder_button)
        layout.addLayout(folder_layout)

        # world selection
        self.world_combo = QComboBox()
        self.world_combo.currentTextChanged.connect(self.update_maps)
        layout.addWidget(QLabel('World:'))
        layout.addWidget(self.world_combo)

        # map selection
        self.map_combo = QComboBox()
        layout.addWidget(QLabel('Map:'))
        layout.addWidget(self.map_combo)

        # resize options
        self.resize_check = QCheckBox('Resize output')
        self.resize_check.stateChanged.connect(self.toggle_resize_options)
        layout.addWidget(self.resize_check)

        resize_layout = QHBoxLayout()
        self.scale_input = QLineEdit()
        self.scale_input.setPlaceholderText('Scale (e.g., 0.5)')
        self.tile_size_input = QLineEdit()
        self.tile_size_input.setPlaceholderText('Tile size (e.g., 64)')
        resize_layout.addWidget(self.scale_input)
        resize_layout.addWidget(self.tile_size_input)
        layout.addLayout(resize_layout)

        # background color
        color_layout = QHBoxLayout()
        self.color_check = QCheckBox('Apply background color')
        self.color_input = QLineEdit()
        self.color_input.setPlaceholderText('Color hex (e.g., #ff0000)')
        color_layout.addWidget(self.color_check)
        color_layout.addWidget(self.color_input)
        layout.addLayout(color_layout)

        # discord options
        self.discord_check = QCheckBox('Post to Discord')
        layout.addWidget(self.discord_check)

        discord_layout = QVBoxLayout()
        self.webhook_input = QLineEdit()
        self.webhook_input.setPlaceholderText('Discord Webhook URL')
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText('Discord message')
        discord_layout.addWidget(self.webhook_input)
        discord_layout.addWidget(self.message_input)
        layout.addLayout(discord_layout)

        # snapshot button
        create_button = QPushButton('Create Snapshot')
        create_button.clicked.connect(self.create_snapshot)
        layout.addWidget(create_button)

        self.setLayout(layout)
        self.resize(400, 300)

        # initialize ui
        self.toggle_resize_options()
        self.update_worlds()

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Dynmap Tiles Directory")
        if folder:
            self.folder_input.setText(folder)
            self.update_worlds()

    def update_worlds(self):
        tiles_dir = self.folder_input.text()
        if tiles_dir:
            world_names = get_world_names(pathlib.Path(tiles_dir))
            self.world_combo.clear()
            self.world_combo.addItems(world_names)

    def update_maps(self):
        tiles_dir = self.folder_input.text()
        world_name = self.world_combo.currentText()
        if tiles_dir and world_name:
            map_names = get_map_names(pathlib.Path(tiles_dir), world_name)
            self.map_combo.clear()
            self.map_combo.addItems(map_names)

    def toggle_resize_options(self):
        enabled = self.resize_check.isChecked()
        self.scale_input.setEnabled(enabled)
        self.tile_size_input.setEnabled(enabled)

    def create_snapshot(self):
        tiles_dir = self.folder_input.text()
        world_name = self.world_combo.currentText()
        map_name = self.map_combo.currentText()

        if not (tiles_dir and world_name and map_name):
            QMessageBox.warning(self, "Missing Information", "Please fill in all required fields.")
            return

        scale = float(self.scale_input.text()) if self.scale_input.text() else None
        fixed_tile_size = int(self.tile_size_input.text()) if self.tile_size_input.text() else None
        color_hex = self.color_input.text() if self.color_check.isChecked() else None

        try:
            snapshot = create_snapshot(tiles_dir, world_name, map_name, scale, fixed_tile_size, color_hex)
            snapshot_path = save_snapshot(snapshot, world_name, map_name)

            if self.discord_check.isChecked():
                webhook_url = self.webhook_input.text()
                message = self.message_input.text()
                if is_discord_available and webhook_url:
                    post_to_discord_webhook(snapshot_path, webhook_url, message)
                else:
                    QMessageBox.warning(self, "Discord Error", "Unable to post to Discord. Check your webhook URL and/or ensure the 'discord' package is installed.")

            QMessageBox.information(self, "Success", f"Snapshot created and saved to:\n{snapshot_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error has occurred: {str(e)}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = SnapshotGUI()
    ex.show()
    sys.exit(app.exec_())
