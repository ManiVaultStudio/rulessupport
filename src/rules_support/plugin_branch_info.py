import calendar
import copy
import datetime
import json
import os
import re
import requests
from enum import Enum
from requests.auth import HTTPBasicAuth
from urllib3.exceptions import InsecureRequestWarning
from .branch_info import BranchInfo
import warnings


class CoreDependencyType(str, Enum):
    """JSON Serializable enum noting type of core dependency
    """
    UNDEF = 'UNDEF'
    FEATURE = 'FEATURE'
    RELEASE = 'RELEASE'
    LATEST = 'LATEST'


class PluginBranchInfo(BranchInfo):

    stale_core_warning = """
.oOOOo.  oOoOOoOOo    Oo     o      o.OOoOoo        .oOOOo.   .oOOOo.  `OooOOo.  o.OOoOoo
o     o      o       o  O   O        O             .O     o  .O     o.  o     `o  O
O.           o      O    o  o        o             o         O       o  O      O  o
 `OOoo.      O     oOooOoOo o        ooOO          o         o       O  o     .O  ooOO
      `O     o     o      O O        O             o         O       o  OOooOO'   O
       o     O     O      o O        o             O         o       O  o    o    o
O.    .O     O     o      O o     .  O             `o     .o `o     O'  O     O   O
 `oooO'      o'    O.     O OOoOooO ooOooOoO        `OoooO'   `OoooO'   O      o ooOooOoO
    """

    core_url_template =\
        'https://lkeb-artifactory.lumc.nl/artifactory/conan-local/lkeb/hdps-core/{}/stable/'

    core_require_template = 'hdps-core/{}@lkeb/stable'

    def __init__(self, folder):
        super().__init__(folder)
        self._core_dep_type = CoreDependencyType.UNDEF
        self._core_version = None

        self._init_branch_info()

    def _init_branch_info(self):
        if self.branch_name == "master" or self.branch_name == "main":
            self._version = "latest"
            self._core_version = "latest"
            self._core_dep_type = CoreDependencyType.LATEST
            print(f"Master/main as: {self.version}")
        else:
            # Feature with release core dependency
            cap = re.search(r"^feature-|feature\/core_(.*)\/(.*)$", self.branch_name)
            if cap is not None:
                self._version = cap.group(2)
                self._core_version = cap.group(1)
                self._core_dep_type = CoreDependencyType.RELEASE
                print(f"Feature branch version: {self.version} "
                      f"Core version: {self.core_version} "
                      f"type: {self._core_dep_type}")
            else:
                # Core branch handling
                # Feature branch handling
                cap = re.search(r"^feature-|feature\/(.*)$", self.branch_name)
                if cap is not None:
                    self._version = cap.group(1)
                    # If a core feature does not exist fallback to latest
                    if self._does_core_version_exist(self._version):
                        self._core_version = self._version
                        self._core_dep_type = CoreDependencyType.FEATURE
                    else:
                        self._core_version = 'latest'
                        self._core_dep_type = CoreDependencyType.LATEST
                    print(f"Feature branch version: {self.version} "
                          f"Core version: {self.core_version} "
                          f"type: {self._core_dep_type}")
                else:
                    # Release branch handling
                    cap = re.search(r"^release-|release\/core_(.*)\/(.*)$", self.branch_name)
                    if cap is not None:
                        self._version = cap.group(2)
                        self._core_version = cap.group(1)
                        self._core_dep_type = CoreDependencyType.RELEASE
                        print(f"Release branch version: {self.version} "
                              f"type: {self._core_dep_type}")
                    else:
                        raise RuntimeError(f"Branch {self.branch_name} does not meet the HDPS "
                                           "naming conventions! "
                                           f"See {self.rules_url}")

    @classmethod
    def read_manifest_timestamp(cls, path_to_manifest):
        """Read the first line from a conanmanifest.txt file
        and return it as an integer timestamp

        Args:
            path_to_manifest (str): full filepath for /x/y/z/conanmanifest.txt
        """
        with open(os.path.join(path_to_manifest), 'r') as manifile:
            artifact_timestamp = int(manifile.readline())
            return artifact_timestamp

    @classmethod
    def from_json(cls, json_str):
        attr_dict = json.loads(json_str)
        if not isinstance(attr_dict, dict):
            raise ValueError(f'{cls.__name__}: Error loading incompatible data')
        temp = cls(attr_dict['_folder'])
        return temp

    def to_json(self):
        # the git stuff is not serializable
        temp_dict = copy.deepcopy(self.__dict__)
        temp_dict.pop('_repo')
        return json.dumps(temp_dict)

    def _does_core_version_exist(self, version):
        warnings.filterwarnings('ignore', category=InsecureRequestWarning)
        resp = requests.get(self.core_url_template.format(version), verify=False)
        warnings.filterwarnings('default')
        return (resp.status_code == 200)

    def _get_git_access_credentials(self):
        has_git_access = False
        access_token = os.environ['LKEB_CORE_ACCESS_TOKEN']
        access_name = ''
        if access_token != '':
            access_name = os.environ['LKEB_CORE_ACCESS_NAME']
            if access_name == '':
                raise EnvironmentError('When a LKEB_CORE_ACCESS_TOKEN environment variable ',
                                       'is present a LKEB_CORE_ACCESS_NAME is required')
            else:
                has_git_access = True
        return (access_token, access_name, has_git_access)

    def _parse_core_commit_timestamp(self, branch_json):
        """From the commit time return the seconds in epoch time stamp
        based on UTC

        Args:
            branch_json (str): The commit json

        Returns:
            int: seconds in Unix epoch
        """
        date = datetime.datetime.strptime(
            branch_json['commit']['commit']['author']['date'],
            "%Y-%m-%dT%H:%M:%SZ")
        return int(calendar.timegm(date.timetuple()))

    def get_timestamp_for_core_commit(self):
        """Returns an integer timestamp for the required core version

        For this to work the job requires access to the hdps/core repo
        using the environment variables: LKEB_CORE_ACCESS_TOKEN and
        LKEB_CORE_ACCESS_NAME. If these are not present the return value is None.

        Raises:
            EnvironmentError: If LKEB_CORE_ACCESS_TOKEN is present without LKEB_CORE_ACCESS_NAME

        Returns:
            int: The core commit timestamp in seconds
        """

        access_token, access_name, has_git_access = self._get_git_access_credentials()

        if has_git_access is False:
            return None

        url = None
        if self._core_dep_type == CoreDependencyType.LATEST:
            url = "https://api.github.com/repos/hdps/core/branches/master"
        elif self._core_dep_type == CoreDependencyType.FEATURE:
            url = "https://api.github.com/repos/hdps/core/branches/feature/{}"\
                .format(self._core_version)
        elif self._core_dep_type == CoreDependencyType.RELEASE:
            url = "https://api.github.com/repos/hdps/core/branches/release/{}"\
                .format(self._core_version)
        else:
            raise NotImplementedError("Unknown core requirement state "
                                      f"{self._core_dep_typ}")

        response = requests.get(
            url,
            auth=HTTPBasicAuth(access_name, access_token)).json()

        if response.get('name', None) is None:
            raise RuntimeError("Failed to access hdps/core branch")
        return self._parse_core_commit_timestamp(response)

    @property
    def version(self):
        return self._version

    @property
    def dependency_state(self):
        raise NotImplementedError
        return None

    @property
    def core_dependency_type(self):
        return self._core_dep_type

    @property
    def core_branch_name(self):
        if self._core_dep_type == CoreDependencyType.LATEST:
            return 'master'
        elif self._core_dep_type == CoreDependencyType.RELEASE:
            return f'release/{self._core_version}'
        elif self._core_dep_type == CoreDependencyType.FEATURE:
            return f'feature/{self._core_version}'
        else:
            raise NotImplementedError(f'Core type {self._core_dep_type} ',
                                      'is not handled for branch_name derivation')

    @property
    def core_version(self):
        return self._core_version

    @property
    def core_requirement(self):
        return self.core_require_template.format(self.core_version)
