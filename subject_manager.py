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
                    subjects.append({
                        "name": row['name'],
                        "category": row['category'],
                        "description": row['description'],
                        "active": row['active'] == 'True'
                    })
        return subjects

    def save_subjects(self):
        with open(self.filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['name', 'category', 'description', 'active'])
            writer.writeheader()
            for subject in self.subjects:
                writer.writerow({
                    'name': subject['name'],
                    'category': subject['category'],
                    'description': subject['description'],
                    'active': subject['active']
                })

    def add_subject(self, subject):
        self.subjects.append(subject)
        self.save_subjects()

    def update_subject(self, updated_subject):
        for i, subject in enumerate(self.subjects):
            if subject["name"] == updated_subject["name"]:
                self.subjects[i] = updated_subject
                break
        self.save_subjects()

    def remove_subject_by_name(self, name):
        self.subjects = [s for s in self.subjects if s["name"] != name]
        self.save_subjects()

    def get_subjects(self):
        return self.subjects

    def get_subject_by_name(self, name):
        return next((s for s in self.subjects if s["name"] == name), None)
