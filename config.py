"""
Configuration management for mcp-slop
"""
import json
import subprocess
from pathlib import Path
from typing import Optional


class SlopConfig:
    """Manages slop configuration stored in ~/.slop-at/config.json"""

    def __init__(self, config_dir: Path = None):
        self.config_dir = config_dir or Path.home() / ".slop-at"
        self.config_file = self.config_dir / "config.json"
        self._config = None

    def load(self) -> dict:
        """Load config from file, or return defaults if not exists"""
        if self._config is not None:
            return self._config

        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self._config = json.load(f)
        else:
            # Default config
            self._config = {
                "graph_server": "https://slop.at",
                "github_repo": None,
                "github_username": self._get_git_username(),
                "real_name": self._get_git_real_name()
            }

        return self._config

    def save(self):
        """Save config to file"""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self._config, f, indent=2)

    def set(self, key: str, value: any):
        """Set a config value and save"""
        config = self.load()
        config[key] = value
        self.save()

    def get(self, key: str, default=None):
        """Get a config value"""
        return self.load().get(key, default)

    def _get_git_username(self) -> Optional[str]:
        """Extract GitHub username from git config"""
        try:
            result = subprocess.run(
                ["git", "config", "--global", "user.email"],
                capture_output=True,
                text=True,
                check=True
            )
            email = result.stdout.strip()
            # Extract username from email (if github email format)
            if "@" in email:
                return email.split("@")[0]
            return None
        except (subprocess.CalledProcessError, FileNotFoundError):
            return None

    def _get_git_real_name(self) -> Optional[str]:
        """Extract real name from git config"""
        try:
            result = subprocess.run(
                ["git", "config", "--global", "user.name"],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            return None

    def is_repo_configured(self) -> bool:
        """Check if a GitHub repo has been configured"""
        return self.get("github_repo") is not None

    def get_repo_path(self) -> Optional[Path]:
        """Get the local path to the slop repo"""
        repo = self.get("github_repo")
        if not repo:
            return None
        # Convert "user/repo" to ~/.slop-at/user/repo
        return self.config_dir / repo
