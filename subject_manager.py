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
        print(f"Loaded subjects: {subjects}")  # Debug print
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
        print(f"Removing subject: {name}")  # Debug print
        self.subjects = [s for s in self.subjects if s["name"] != name and s["name"].strip()]
        print(f"Subjects after removal: {self.subjects}")  # Debug print
        self.save_subjects()
        return self.get_subjects()  # Return the updated list of subjects

    def save_subjects(self):
        print(f"Saving subjects: {self.subjects}")  # Debug print
        try:
            with open(self.filename, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['name', 'category', 'description', 'active'])
                writer.writeheader()
                for subject in self.subjects:
                    if subject['name'].strip():  # Only save non-empty subjects
                        writer.writerow({
                            'name': subject['name'],
                            'category': subject['category'],
                            'description': subject['description'],
                            'active': subject['active']
                        })
            print("Subjects saved successfully")  # Debug print
        except Exception as e:
            print(f"Error saving subjects: {str(e)}")  # Error logging

    def get_subjects(self):
        return self.subjects

    def get_subject_by_name(self, name):
        return next((s for s in self.subjects if s["name"] == name), None)
