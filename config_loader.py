import json
from pathlib import Path

class CfgLoader:
    _instances = {}

    def __new__(cls, cfg_file=None, *args, **kwargs):
        cfg_path = Path(cfg_file).resolve() if cfg_file else None

        # Check if an instance with the given cfg_file already exists
        if cfg_path in cls._instances:
            return cls._instances[cfg_path]

        # Create a new instance if it doesn't exist
        instance = super(CfgLoader, cls).__new__(cls)
        cls._instances[cfg_path] = instance
        return instance

    def __init__(self, cfg_file=None):
        self.cfg_path = Path(cfg_file).resolve() if cfg_file else None

        # Ensure initialization only happens once per instance
        if not hasattr(self, "initialized"):
            self.initialized = True
            self.data = None
            self.home_dir = Path(__file__).resolve().parent

            if self.cfg_path and self.cfg_path.exists():
                with open(self.cfg_path, 'r') as f:
                    self.data = json.load(f)

    def save(self, new_data):
        """
        Updates the existing data with the new_data dictionary and saves it to the configuration file.
        """
        if self.data is None:
            self.data = {}

        # Update the current data with the new data
        self.data = new_data

        # Save the updated data back to the file
        with open(self.cfg_path, 'w') as f:
            json.dump(self.data, f, indent=4)

    def get_data(self, reload=True):
        if reload:
            with open(self.cfg_path, 'r') as f:
                self.data = json.load(f)

        return self.data