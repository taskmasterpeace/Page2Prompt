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

    def add_subject(self, name, category, description, active):
        self.subjects.append({
            "name": name,
            "category": category,
            "description": description,
            "active": active
        })
        self.save_subjects()

    def edit_subject(self, index, name, category, description, active):
        if 0 <= index < len(self.subjects):
            self.subjects[index] = {
                "name": name,
                "category": category,
                "description": description,
                "active": active
            }
            self.save_subjects()

    def remove_subject(self, index):
        if 0 <= index < len(self.subjects):
            del self.subjects[index]
            self.save_subjects()
