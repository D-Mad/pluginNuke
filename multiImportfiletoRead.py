import os
import re
import nuke
from PySide2.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel, QCheckBox

class ImportFolderWidget(QWidget):
    def __init__(self, parent=None):
        super(ImportFolderWidget, self).__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        import_btn = QPushButton('Chọn folder để import', self)
        import_btn.clicked.connect(self.import_folder)
        layout.addWidget(import_btn)

        self.sequence_checkbox = QCheckBox('Import dưới dạng sequence', self)
        layout.addWidget(self.sequence_checkbox)

        self.info_label = QLabel('Chưa chọn folder nào', self)
        layout.addWidget(self.info_label)

        self.setLayout(layout)

    def import_folder(self):
        folder = QFileDialog.getExistingDirectory(self, 'Chọn folder', os.path.expanduser('~'))
        if folder:
            self.info_label.setText(f'Folder được chọn: {folder}')
            self.import_files_from_folder(folder, self.sequence_checkbox.isChecked())
        else:
            self.info_label.setText('Chưa chọn folder nào')

    def find_leaf_directory(self, folder):
        while True:
            subdirs = [d for d in os.listdir(folder) if os.path.isdir(os.path.join(folder, d))]
            if not subdirs:
                break
            folder = os.path.join(folder, subdirs[0])
        return folder

    def import_files_from_folder(self, folder, import_as_sequence):
        leaf_directory = self.find_leaf_directory(folder)
        supported_exts = ('.exr', '.jpg', '.jpeg', '.png', '.tif', '.tiff', '.mov', '.mp4', '.dpx')
        file_sequences = {}

        for file in os.listdir(leaf_directory):
            if file.lower().endswith(supported_exts):
                file_path = os.path.join(leaf_directory, file).replace('\\', '/')

                if import_as_sequence:
                    match = re.match(r'^(.*\D)(\d+)\.(.+)$', file)
                    if match:
                        base, frame, ext = match.groups()
                        key = (os.path.join(leaf_directory, base).replace('\\', '/'), ext)
                        if key in file_sequences:
                            file_sequences[key].append(int(frame))
                        else:
                            file_sequences[key] = [int(frame)]

                else:
                    read_node = nuke.createNode('Read', f"file {file_path}", inpanel=False)
                    read_node['on_error'].setValue("black")

                    width = read_node.metadata()["input/width"]
                    height = read_node.metadata()["input/height"]
                    read_node['format'].setValue(f"{width} {height} 0 0 {width} {height} 1 square_1")

        if import_as_sequence:
            for (base, ext), frames in file_sequences.items():
                min_frame = min(frames)
                max_frame = max(frames)
                file_pattern = f"{base}%04d.{ext}"
                read_node = nuke.createNode('Read', f"file {file_pattern} first {min_frame} last {max_frame}", inpanel=False)
                read_node['on_error'].setValue("black")

                width = read_node.metadata()["input/width"]
                height = read_node.metadata()["input/height"]
                read_node['format'].setValue(f"{width} {height} 0 0 {width } {height} 1 square_1")

def show_import_folder_widget():
    app = QApplication.instance()
    if not app:
        app = QApplication([])

    import_folder_widget = ImportFolderWidget()
    import_folder_widget.show()
    return import_folder_widget


import_folder_widget = show_import_folder_widget()

    
