import json

class MemorySystem:
    def __init__(self, long_term_file="long_term.json"):
        self.short_term = {}
        self.long_term_file = long_term_file
        try:
            with open(long_term_file, "r") as f:
                self.long_term = json.load(f)
        except FileNotFoundError:
            self.long_term = {}

    def update_short_term(self, key, value):
        self.short_term[key] = value

    def update_long_term(self, key, value):
        self.long_term[key] = value
        with open(self.long_term_file, "w") as f:
            json.dump(self.long_term, f)

    def get_context(self):
        return {**self.long_term, **self.short_term}
