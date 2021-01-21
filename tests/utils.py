from git import Repo
import pathlib
import tempfile
import shutil

class TestRepo:
    """Create a test git repo with a dummy README.md file
    as the single entry.

    Args:
        prefix (str): A prefix used in the directory_name
    """
    def __init__(self, prefix = None):
        self._temp_repo_dir = tempfile.TemporaryDirectory(prefix = prefix + '_')
        self.readme_path = pathlib.Path(self._temp_repo_dir.name, 'README.md')
        self.readme_path.touch()
        self._repo = Repo.init(self._temp_repo_dir.name)
        self._repo.git.init()
        self._repo.git.add(pathlib.Path(self._temp_repo_dir.name, '.'))
        self._repo.git.commit('-m', 'Initial checkin')

    def append_to_readme(self, some_text):
        """Add text to the te README.md

        Args:
            some_text (str): Text to add
        """
        with open(self.readme_path, 'a') as f:
            f.write(some_text)

    def create_feature_branch(self, feature_name):
        """Add a branch according to the hdps feature naming convention.
        feature_name wil be preceeded by 'feature/' in the branch name

        Args:
            feature_name (str): feature name
        """
        self._repo.git.checkout('-b', f'feature/{feature_name}')
        self.append_to_readme(feature_name)
        self._repo.git.commit('-a', message='Created feature branch')

    def create_core_release_branch(self, version):
        """Add a branch according to the hdps release naming convention.
        version wil be preceeded by 'release/' in the branch name

        Args:
            version (str): The release version number
        """
        self._repo.git.checkout('-b', f'release/{version}')
        self.append_to_readme(version)
        self._repo.git.commit('-a', message='Created release branch')

    def create_plugin_release_branch(self, version, core_version):
        """Add a branch according to the hdps release naming convention.
        The branch name will be of the form: 'release/core_<core_version>/<version>'

        Args:
            version (str): plugin version string
            core_version (str): dependant core version string
        """
        self._repo.git.checkout('-b', f'release/core_{core_version}/{version}')
        self.append_to_readme(version + '_' + core_version)
        self._repo.git.commit('-a', message='Created plugin-release branch')

    def create_plugin_feature_core_release_branch(self, version, core_version):
        """Add a branch according to the hdps release naming convention.
        The branch name will be of the form: 'release/core_<core_version>/<version>'

        Args:
            version (str): plugin version string
            core_version (str): dependant core version string
        """
        self._repo.git.checkout('-b', f'feature/core_{core_version}/{version}')
        self.append_to_readme('feature ' + version + '_' + core_version)
        self._repo.git.commit('-a', message='Created plugin-feature/core-release branch')

    def checkout_branch(self, branch_name):
        """Perform a git checkout on the give branch

        Args:
            branch_name (str): branch to checkout
        """
        self._repo.git.checkout(branch_name)

    def clone_this(self, prefix):
        """Clone this repo to a new temporary directory

        Args:
            prefix (str): prefix for the temp directory name

        Returns:
            Repo: The clone Repo
        """
        clone_dir = tempfile.TemporaryDirectory(prefix = prefix)
        return self._repo.clone(clone_dir)

    @property
    def directory(self):
        return str(self._temp_repo_dir.name)

    def __del__(self):
        self._repo.git.clear_cache()
        self._repo.git = None
        # shutil.rmtree(self._temp_repo_dir.name)

