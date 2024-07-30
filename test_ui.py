import unittest
from unittest.mock import MagicMock, patch
import tkinter as tk
from ui import SubjectFrame

class TestSubjectFrame(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.core_mock = MagicMock()
        self.subject_frame = SubjectFrame(self.root, self.core_mock)

    def tearDown(self):
        self.root.destroy()

    def test_add_subject(self):
        self.subject_frame.name_entry.insert(0, "John Doe")
        self.subject_frame.category_combo.set("Main Character")
        self.subject_frame.description_text.insert("1.0", "A brave hero")

        with patch('tkinter.messagebox.showerror') as mock_error:
            self.subject_frame.add_subject()

        self.core_mock.add_subject.assert_called_once_with("John Doe", "Main Character", "A brave hero")
        self.assertEqual(self.subject_frame.subjects_listbox.size(), 1)
        self.assertEqual(self.subject_frame.subjects_listbox.get(0), "John Doe (Main Character)")
        mock_error.assert_not_called()

    def test_add_subject_empty_fields(self):
        with patch('tkinter.messagebox.showerror') as mock_error:
            self.subject_frame.add_subject()

        self.core_mock.add_subject.assert_not_called()
        self.assertEqual(self.subject_frame.subjects_listbox.size(), 0)
        mock_error.assert_called_once_with("Error", "All fields must be filled")

    def test_toggle_subject(self):
        self.subject_frame.subjects_listbox.insert(tk.END, "John Doe (Main Character)")
        self.subject_frame.subjects_listbox.selection_set(0)

        self.subject_frame.toggle_subject()

        self.core_mock.toggle_subject.assert_called_once_with("John Doe")
        self.assertEqual(self.subject_frame.subjects_listbox.get(0), "John Doe (Main Character) (Inactive)")

    def test_toggle_subject_no_selection(self):
        with patch('tkinter.messagebox.showerror') as mock_error:
            self.subject_frame.toggle_subject()

        self.core_mock.toggle_subject.assert_not_called()
        mock_error.assert_called_once_with("Error", "No subject selected")

    def test_remove_subject(self):
        self.subject_frame.subjects_listbox.insert(tk.END, "John Doe (Main Character)")
        self.subject_frame.subjects_listbox.selection_set(0)

        self.subject_frame.remove_subject()

        self.core_mock.remove_subject.assert_called_once_with("John Doe")
        self.assertEqual(self.subject_frame.subjects_listbox.size(), 0)

    def test_remove_subject_no_selection(self):
        with patch('tkinter.messagebox.showerror') as mock_error:
            self.subject_frame.remove_subject()

        self.core_mock.remove_subject.assert_not_called()
        mock_error.assert_called_once_with("Error", "No subject selected")

if __name__ == '__main__':
    unittest.main()
