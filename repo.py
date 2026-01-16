"""
Git repository operations for mcp-slop
"""
import subprocess
from pathlib import Path
from typing import Optional
from config import SlopConfig


class RepoManager:
    """Manages the local slop git repository"""

    def __init__(self, config: SlopConfig = None):
        self.config = config or SlopConfig()

    def ensure_repo_exists(self) -> tuple[bool, str]:
        """
        Check if repo is configured and cloned. If not, guide user through setup.

        Returns:
            (success: bool, message: str)
        """
        if not self.config.is_repo_configured():
            return (False,
                "❌ No slop repo found!\n\n"
                "First-time setup:\n"
                "1. Create a new repo on GitHub: https://github.com/new\n"
                "2. Come back and tell me the repo URL (e.g., github.com/you/slops)\n"
                "   Use the tool: setup_slop_repo('your-username/your-repo-name')"
            )

        repo_path = self.config.get_repo_path()
        if not repo_path or not repo_path.exists():
            return (False, f"❌ Repo configured but not cloned: {self.config.get('github_repo')}\n"
                          f"Run: setup_slop_repo('{self.config.get('github_repo')}')")

        return (True, f"✅ Slop repo ready at {repo_path}")

    def clone_repo(self, github_repo: str) -> tuple[bool, str]:
        """
        Clone a GitHub repo to ~/.axon-repo/{org}/{repo}

        Args:
            github_repo: Format "org/repo" or full URL

        Returns:
            (success: bool, message: str)
        """
        # Normalize repo string
        if github_repo.startswith("http"):
            # Extract org/repo from URL
            parts = github_repo.rstrip("/").split("/")
            github_repo = f"{parts[-2]}/{parts[-1].replace('.git', '')}"
        else:
            github_repo = github_repo.replace("github.com/", "").strip("/")

        repo_url = f"https://github.com/{github_repo}.git"
        repo_path = self.config.config_dir / github_repo

        # Check if already cloned
        if repo_path.exists():
            return (False, f"❌ Repo already exists at {repo_path}")

        # Create parent directory
        repo_path.parent.mkdir(parents=True, exist_ok=True)

        # Clone
        try:
            subprocess.run(
                ["git", "clone", repo_url, str(repo_path)],
                check=True,
                capture_output=True,
                text=True
            )
        except subprocess.CalledProcessError as e:
            return (False, f"❌ Failed to clone repo: {e.stderr}")

        # Save to config
        self.config.set("github_repo", github_repo)

        return (True, f"✅ Cloned {github_repo} to {repo_path}\n🎉 Ready to slop!")

    def commit_and_push(self, filepath: Path, message: str) -> tuple[bool, str]:
        """
        Commit a file and push to remote

        Args:
            filepath: Path to the file to commit
            message: Commit message

        Returns:
            (success: bool, message: str)
        """
        repo_path = self.config.get_repo_path()
        if not repo_path:
            return (False, "❌ No repo configured")

        try:
            # Add file
            subprocess.run(
                ["git", "add", str(filepath.relative_to(repo_path))],
                cwd=repo_path,
                check=True,
                capture_output=True
            )

            # Commit
            subprocess.run(
                ["git", "commit", "-m", message],
                cwd=repo_path,
                check=True,
                capture_output=True
            )

            # Push
            subprocess.run(
                ["git", "push"],
                cwd=repo_path,
                check=True,
                capture_output=True
            )

            return (True, f"✅ Committed and pushed: {message}")

        except subprocess.CalledProcessError as e:
            return (False, f"❌ Git operation failed: {e.stderr}")

    def get_file_github_url(self, filepath: Path) -> Optional[str]:
        """
        Get the public GitHub URL for a file

        Args:
            filepath: Local path to the file

        Returns:
            GitHub URL or None
        """
        repo = self.config.get("github_repo")
        if not repo:
            return None

        repo_path = self.config.get_repo_path()
        if not repo_path:
            return None

        try:
            # Get current commit hash
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            commit_hash = result.stdout.strip()

            # Get relative path from repo root
            rel_path = filepath.relative_to(repo_path)

            return f"https://github.com/{repo}/blob/{commit_hash}/{rel_path}"

        except (subprocess.CalledProcessError, ValueError):
            return None
