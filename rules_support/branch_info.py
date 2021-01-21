import copy
import json
from git import Repo

class BranchInfo:
    """
    Extract version and commit infor from hdps repo branches

    Attributes:
        _folder (str): Full path to repo directory
    """

    def __init__(self, folder):
        """
        Args:
            folder (str): Full path to repo directory
        """
        self._folder = folder
        self._repo = Repo(path = self._folder)

    @classmethod
    def from_json(cls, json_str):
        attr_dict = json.loads(json_str)
        if not isinstance(attr_dict, dict):
            raise ValueError(f'{cls.__name__}: Error loading incompatible data')
        temp = cls(attr_dict['_folder'])
        temp._repo = Repo(path = temp.folder)
        return temp

    def to_json(self):
        # the git stuff is not serializable
        temp_dict = copy.deepcopy(self.__dict__)
        temp_dict.pop('_repo')
        return json.dumps(temp_dict)

    @property
    def branch_name(self):
        """The git branch name for the folder

        Returns:
            str: Full branch name
        """
        return self._repo.active_branch.name

    @property
    def folder(self):
        """The folder path

        Returns:
            str: Full folder path
        """
        return self._folder

    @property
    def rules_url(self):
        return "https://github.com/hdps/core/wiki/Branch-naming-rules"

    @property
    def version(self):
        raise NotImplementedError