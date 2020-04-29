import os

import toml


class Config:
    def __init__(self, path):
        self.default_section = 'default'
        self.path = path
        self.config = {}
        self.active_section = self.default_section
        self.load()

    def __str__(self):
        return str(self.config)

    def add_section(self, section_name):
        self.config[section_name] = {}
        self.select_section(section_name)
        return self

    def select_section(self, section_name):
        self.active_section = section_name
        return self

    def get_section(self):
        return self.config.get(self.active_section)

    def load(self):
        if not os.path.exists(self.path):
            with open(self.path, 'w', encoding='utf8', ):
                toml.dump(self.config)
        with open(self.path, encoding='utf8', ) as f:
            self.config = toml.load(f)
            return self

    def save(self):
        with open(self.path, 'w', encoding='utf8') as f:
            toml.dump(self.config, f)
            return True

    def get(self, value, section_name=None):
        section_name = section_name or self.active_section
        self.select_section(section_name)
        section = self.config.get(section_name)
        if section:
            return section.get(value)

    def set(self, params, section_name=None):
        section_name = section_name or self.active_section
        self.select_section(section_name)
        section = self.config.setdefault(self.active_section, {})
        if isinstance(section, dict):
            for key, value in params.items():
                section.setdefault(key, value)
        return self
