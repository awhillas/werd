import hashlib
import pickle
from pathlib import Path


class ContentTracker:
    """Class to check for changes in the content of a file."""

    def __init__(self, db_path):
        """Initialize."""
        self.db_path = Path(db_path)
        try:
            self.hash = pickle.load(self.db_path.open("rb"))
        except IOError:
            self.hash = {}

    def get_checksum(self, filepath: str):
        """Get the checksum of a file."""
        return hashlib.md5(open(filepath).read().encode("utf-8")).hexdigest()

    def save(self):
        """Save the hash."""
        pickle.dump(self.hash, self.db_path.open("wb"))

    def update(self, filepath: str):
        """Update the hash with new file path."""
        filepath = str(filepath)
        self.hash[filepath] = self.get_checksum(filepath)
        self.save()

    def has_changed(self, filepath: str):
        """Check if content has changed or we don't know about it yet."""
        filepath = str(filepath)
        if filepath not in self.hash or self.hash[filepath] != self.get_checksum(
            filepath
        ):
            return True
        else:
            return False
