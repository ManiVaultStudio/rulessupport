import os
import re
import requests
from enum import Enum
from requests.auth import HTTPBasicAuth
from .branch_info import BranchInfo

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

    def __init__(self, folder):
        super().__init__(folder)
        self._version
        self._core_dep_type = CoreDependencyType.UNDEF
        self._core_version = None
        self._core_branch_name = None
        self._rules_url = "https://github.com/hdps/core/wiki/Branch-naming-rules"
        self._init_branch_info()

    def _init_branch_info(self):
        result = None
        if self.branch_name == "master" or self.branch_name == "main":
            self._version = "latest"
            self._core_version = "latest"
            self._core_branch_name = "master"  # TBD - will migrate to name main
            self._core_dep_type = CoreDependencyType.LATEST
            print(f"Master/main as: {self.version}")
        else:
            # Core branch handling
            # Feature branch handling
            cap = re.search(r"^feature-|feature\/(.*)$", self.branch_name)
            if cap is not None:
                self._version = cap.group(1)
                self._core_version = self._version
                self._core_dep_type = CoreDependencyType.FEATURE
                print(f"Derived feature branch version: {self.version}"
                      f" type: {self._core_dep_type}")
            else:
                # Release branch handling
                cap = re.search(r"^release-|release\/core_(.*)\/(.*)$", self.branch_name)
                if cap is not None:
                    self.version = cap.group(2)
                    self._core_version = cap.group(1)
                    self._core_dep_typ = CoreDependencyType.RELEASE
                    print(f"Derived release branch version: {self.version}"
                          f" type: {self._core_dep_type}")
                else:
                    raise RuntimeError(f"Branch {self.branch_name} does not meet the HDPS "
                                         "naming conventions! "
                                         f"See {self._rules_url}")

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

    def get_dependent_core_version(self):
        """Return the version of the dependent core.

        Repositories with access to the hdps/core repo must have
        both environemtn variables: LKEB_CORE_ACCESS_TOKEN and LKEB_CORE_ACCESS_NAME
        present

        Raises:
            EnvironmentError: If LKEB_CORE_ACCESS_TOKEN is present without LKEB_CORE_ACCESS_NAME
            EnvironmentError: If required core release version is not available

        Returns:
            str: The core version.
        """

        access_token, access_name, has_git_access = self._get_git_access_credentials()

        if self._core_dep_typ ==CoreDependencyType.LATEST:
            self._core_version = 'latest'
        # elif self._core_dep_typ == CoreDependencyType.FEATURE:
        #     # check if the version branch exists in github or revert to latest
        #     if not has_git_access:
        #         print(f"Can't access core. Defaulting to hdps-core version: latest")
        #         self._core_version = 'latest'
        #     else:
        #         url = "https://api.github.com/repos/hdps/core/branches/feature/{}"\
        #             .format(hdpscore['version'])
        #         response = requests.get(url, auth=HTTPBasicAuth(access_name, access_token)).json()
        #     if response.get('name', '') == f'feature/{hdpscore["version"]}':
        #         core_reference = hdpscore['template'].format(hdpscore['version'])
        #         self.requires(core_reference)
        #         self._save_core_timestamp(response, hdpscore)
        #         print(f"Core Feature version is {core_reference}")
        #     else:
        #         # No commit so there is no branch - default to latest
        #         self.requires(hdpscore['template'].format('latest'))
        #         print(f"No core version {hdpscore['version']}. Defaulting to hdps-core *latest*")

        # elif hdpscore['dependency_state'] == DependencyState.RELEASE:
        #     url = "https://api.github.com/repos/hdps/core/branches/release/{}"\
        #         .format(hdpscore['version'])
        #     response = requests.get(url, auth=HTTPBasicAuth(access_name, access_token)).json()
        #     if response.get('name', '') == f'release/{hdpscore["version"]}':
        #         core_reference = hdpscore['template'].format(hdpscore['version'])
        #         self.requires(core_reference)
        #         self._save_core_timestamp(response, hdpscore)
        #         print(f"Core Release version is {core_reference}")
        #     else:
        #         # No commit so there is no branch - in release case this is an error
        #         raise ConanException(f"Core release branch release/{hdpscore['version']} "
        #                              "does not exist but was specified in the plugin.")
        # else:
        #     raise NotImplementedError("Unknown requirement state "
        #                               f"{hdpscore['dependency_state']}")
        return self._core_version

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
        return self._core_branch_name

    @property
    def core_version(self):
        return self._core_version