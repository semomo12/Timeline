import json
import os
import re
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFileDialog, QMessageBox, QInputDialog, QLineEdit
from core.data.project import Project

class ProjectController:
    """Handles creating, opening and saving projects."""

    def __init__(self, main_controller):
        self.main_controller = main_controller

    def new(self):
        """Create a new empty project"""
        if not self._confirm_before_action("creating a new project"):
            return
        name = self._ask_for_project_name("Untitled Project")
        if name is None:
            return

        self.main_controller.project = Project()
        self.main_controller.project.name = name
        self.main_controller.current_file = None

        self._call_main("_initialize_project_state", new_project=True)
        self._call_main("mark_project_dirty", False)
        self._call_main("_update_ui")
        print("New project created!")

    def open(self):
        """Open a project file from disk."""
        if not self._confirm_before_action("opening another project"):
            return
        dialog = QFileDialog(self.main_controller)
        dialog.setWindowTitle("Open Project")
        dialog.setNameFilter("Timeline Projects (*.json)")
        dialog.setFileMode(QFileDialog.ExistingFile)
        dialog.setModal(True)
        dialog.setWindowModality(Qt.ApplicationModal)
        dialog.raise_()
        dialog.activateWindow()

        if dialog.exec() != QFileDialog.Accepted:
            self._bring_window_to_front()
            return

        selected_files = dialog.selectedFiles()
        if not selected_files:
            self._bring_window_to_front()
            return
        filepath = selected_files[0]
        if not self._validate_path(filepath, for_reading=True):
            self._bring_window_to_front()
            return
        project = self._load_project_from_file(filepath)
        if not project:
            QMessageBox.warning(self.main_controller, "Error", "Failed to load project!")
            self._bring_window_to_front()
            return

        self.main_controller.project = project
        self.main_controller.current_file = filepath
        self._call_main("_initialize_project_state", new_project=False)
        self._call_main("mark_project_dirty", False)
        self._call_main("_update_ui")
        print(f"Project loaded successfully: {filepath}")
        self._bring_window_to_front()

    def save(self):
        """Save the current project to its current filename."""
        self._call_main("_sync_timeline_settings")

        if not getattr(self.main_controller, "current_file", None):
            self.save_as()
            return

        is_dirty = bool(getattr(self.main_controller, "project_dirty", False))
        if not is_dirty:
            self._show_already_saved()
            return

        file_path = self.main_controller.current_file
        if self._save_project_to_file(self.main_controller.project, file_path):
            print(f"Project saved successfully: {file_path}")
            self._call_main("mark_project_dirty", False)
            self._show_save_success()
        else:
            QMessageBox.warning(self.main_controller, "Error", "Failed to save project!")

    def save_as(self):
        """Prompt for a new filename and save the project there."""
        dialog = QFileDialog(self.main_controller)
        dialog.setWindowTitle("Save Project")
        dialog.setNameFilter("Timeline Projects (*.json)")
        dialog.setDefaultSuffix("json")
        dialog.setAcceptMode(QFileDialog.AcceptSave)
        dialog.setModal(True)
        dialog.setWindowModality(Qt.ApplicationModal)

        default_dir = self._default_save_directory()
        dialog.setDirectory(default_dir)

        current_file = getattr(self.main_controller, "current_file", None)
        if current_file:
            dialog.selectFile(current_file)
        else:
            suggested = os.path.join(default_dir, self._suggest_project_filename())
            dialog.selectFile(suggested)

        dialog.raise_()
        dialog.activateWindow()

        if dialog.exec() != QFileDialog.Accepted:
            return

        selected_files = dialog.selectedFiles()
        if not selected_files:
            return

        filepath = selected_files[0]
        if not filepath.endswith(".json"):
            filepath += ".json"

        if not self._validate_path(filepath, for_reading=False):
            return

        self.main_controller.current_file = os.path.abspath(filepath)
        self.save()

    def edit_project_name(self):
        """Prompt the user to rename the current project."""
        current_name = getattr(self.main_controller.project, "name", "")

        while True:
            new_name, ok = QInputDialog.getText(
                self.main_controller,
                "Edit Project Name",
                "Enter new project name:",
                QLineEdit.Normal,
                current_name,
            )
            if not ok:
                return

            is_valid, message = self._validate_project_name_text(new_name)
            if not is_valid:
                QMessageBox.warning(self.main_controller, "Invalid Input", message)
                continue

            if new_name != current_name:
                self.main_controller.project.name = new_name
                self._call_main("_update_ui")
                self._call_main("mark_project_dirty")
                QMessageBox.information(
                    self.main_controller,
                    "Project Name Updated",
                    f"Project name changed to: {new_name}",
                )
            break

    def edit_project(self):
        """Used for backward compatibility with older controllers that still call this method."""
        self._call_main("_prompt_project_name", trigger_update=True)


    def _confirm_before_action(self, description):
        helper = getattr(self.main_controller, "_maybe_save_before_action", None)
        if callable(helper):
            return helper(description)
        return True

    def _call_main(self, attr_name, *args, **kwargs):
        target = getattr(self.main_controller, attr_name, None)
        if callable(target):
            return target(*args, **kwargs)
        return None

    def _bring_window_to_front(self):
        self._call_main("raise_")
        self._call_main("activateWindow")

    def _validate_path(self, filepath, for_reading):
        ui_controller = getattr(self.main_controller, "ui_controller", None)
        if ui_controller and hasattr(ui_controller, "validate_file_path"):
            return ui_controller.validate_file_path(filepath, for_reading=for_reading)
        return True

    def _default_save_directory(self):
        current = getattr(self.main_controller, "current_file", None)
        if current:
            directory = os.path.dirname(current)
            if directory:
                return directory
        return os.getcwd()

    def _suggest_project_filename(self):
        project = getattr(self.main_controller, "project", None)
        name = getattr(project, "name", "") if project else ""
        if not name:
            name = "Timeline Project"
        sanitized = re.sub(r'[<>:"/\\|?*]', "", name).strip()
        if not sanitized:
            sanitized = "Timeline Project"
        return f"{sanitized}.json"

    def _show_save_success(self):
        QMessageBox.information(self.main_controller, "Saved", "Saved successfully.")

    def _show_already_saved(self):
        QMessageBox.information(self.main_controller, "Already Saved", "Project is already saved.")

    def _save_project_to_file(self, project, file_path):
        try:
            with open(file_path, "w", encoding="utf-8") as handle:
                handle.write(project.to_json())
            return True
        except Exception as error:
            print("Error saving project:", error)
            return False

    def _load_project_from_file(self, file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as handle:
                raw = handle.read()
            if not raw.strip():
                raise ValueError("Project file is empty.")
            data = json.loads(raw)
            return Project.from_json(data)
        except Exception as error:
            print("Error loading project:", error)
            return None

    def _ask_for_project_name(self, initial_text):
        current_text = initial_text
        while True:
            name, ok = QInputDialog.getText(
                self.main_controller,
                "Project Name",
                "Project name:",
                QLineEdit.Normal,
                current_text,
            )
            if not ok:
                return None

            is_valid, message = self._validate_project_name_text(name)
            if not is_valid:
                QMessageBox.warning(self.main_controller, "Invalid Input", message)
                current_text = name
                continue

            return name.strip()

    def _validate_project_name_text(self, name):
        if name is None:
            return False, "Project name cannot be empty."

        trimmed = name.strip()
        if not trimmed:
            return False, "Project name cannot be empty or contain only spaces."

        if len(trimmed) > 100:
            return False, "Project name cannot be longer than 100 characters."

        invalid_chars = ['<', '>', ':', '"', '|', '?', '*', '/', '\\']
        for char in invalid_chars:
            if char in trimmed:
                return False, f"Project name cannot contain these characters: {', '.join(invalid_chars)}"

        return True, ""
