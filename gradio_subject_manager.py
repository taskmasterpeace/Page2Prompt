import csv
import os

class SubjectManager:
    def __init__(self, filename: str = "subjects.csv"):
        self.filename = filename
        self.subjects = self.load_subjects()

    def load_subjects(self):
        subjects = []
        if os.path.exists(self.filename):
            with open(self.filename, 'r', newline='') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    subjects.append(row)
        return subjects

    def save_subjects(self):
        fieldnames = ['name', 'category', 'description', 'active', 'hairstyle', 'clothing', 'body_type', 'accessories', 'age', 'height', 'distinguishing_features', 'scene_order']
        with open(self.filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for subject in self.subjects:
                writer.writerow(subject)

    def add_subject(self, subject):
        self.subjects.append(subject)
        self.save_subjects()

    def update_subject(self, updated_subject):
        for i, subject in enumerate(self.subjects):
            if subject['name'] == updated_subject['name']:
                self.subjects[i] = updated_subject
                break
        self.save_subjects()

    def delete_subject(self, name):
        self.subjects = [s for s in self.subjects if s['name'] != name]
        self.save_subjects()

    def get_subjects(self):
        return self.subjects

    def get_subject_by_name(self, name):
        for subject in self.subjects:
            if subject['name'] == name:
                return subject
        return None

    def get_active_subjects(self):
        return [s for s in self.subjects if s.get('active') == 'True']

    def toggle_subject_active(self, name, is_active):
        for subject in self.subjects:
            if subject['name'] == name:
                subject['active'] = str(is_active).lower()
                break
        self.save_subjects()

    def update_subject(self, updated_subject):
        for i, subject in enumerate(self.subjects):
            if subject['name'] == updated_subject['name']:
                self.subjects[i] = updated_subject
                break
        self.save_subjects()

    def get_subject_description(self, name, shot_type):
        subject = self.get_subject_by_name(name)
        if not subject:
            return ""
        
        description = subject['description']
        if shot_type == 'close-up':
            return f"{description} {subject.get('hairstyle', '')} {subject.get('distinguishing_features', '')}"
        elif shot_type == 'medium':
            return f"{description} {subject.get('clothing', '')} {subject.get('accessories', '')}"
        else:  # wide shot
            return f"{subject.get('body_type', '')} {subject.get('height', '')} {subject.get('age', '')}-year-old"

    def get_subjects_by_scene_order(self):
        return sorted(self.subjects, key=lambda x: int(x.get('scene_order', 0)))

    def get_subjects_by_character(self):
        return sorted(self.subjects, key=lambda x: x['name'])

    def get_subjects_by_category(self, category):
        return [subject['name'] for subject in self.subjects if subject['category'] == category]

    def get_all_subject_names(self):
        return [subject['name'] for subject in self.subjects]
