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
        with open(self.filename, 'w', newline='') as f:
            fieldnames = ['name', 'category', 'description', 'active']
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

    def toggle_subject_active(self, name):
        for subject in self.subjects:
            if subject['name'] == name:
                subject['active'] = str(not (subject.get('active') == 'True'))
                break
        self.save_subjects()

    def get_subject_description(self, name, shot_type):
        subject = self.get_subject_by_name(name)
        if not subject:
            return ""
        
        description = subject['description']
        if shot_type == 'close-up':
            # Focus on facial features or detailed characteristics
            return " ".join(description.split()[:20])  # First 20 words
        elif shot_type == 'medium':
            # Include upper body details
            return " ".join(description.split()[:30])  # First 30 words
        else:  # wide shot
            # General appearance and positioning
            return " ".join(description.split()[:10])  # First 10 words
