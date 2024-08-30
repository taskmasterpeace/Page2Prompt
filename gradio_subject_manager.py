class SubjectManager:
    def __init__(self):
        self.subjects = []

    def add_subject(self, subject):
        self.subjects.append(subject)

    def update_subject(self, updated_subject):
        for i, subject in enumerate(self.subjects):
            if subject['name'] == updated_subject['name']:
                self.subjects[i] = updated_subject
                break

    def delete_subject(self, name):
        self.subjects = [s for s in self.subjects if s['name'] != name]

    def get_subjects(self):
        return self.subjects

    def get_subject_by_name(self, name):
        for subject in self.subjects:
            if subject['name'] == name:
                return subject
        return None
