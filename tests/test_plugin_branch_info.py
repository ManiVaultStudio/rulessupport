import json
import os
import pathlib
import unittest
from rules_support.plugin_branch_info import PluginBranchInfo
from tests.utils import TestRepo


class TestPluginBranchInfo(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Create a test repo for the plugin with the following example branches
            1) master (or main)
            2) feature/XYZ_unittest_feature (core does not exist)
            3) feature/test_ci_cd (core does exist)
            3) feature/core_0.1/ABC_unittest_feature
            3) release/core_0.1/1.0

        core release/0.1 exists in the artifactory
        """
        cls.test_repo = TestRepo(prefix=cls.__name__)
        cls.test_repo.create_feature_branch('XYZ_unittest_feature')
        cls.test_repo.create_feature_branch('test_ci_cd')
        cls.test_repo.create_plugin_feature_core_release_branch(
            'ABC_unittest_feature', '0.1')
        cls.test_repo.create_plugin_release_branch('1.0', '0.1')
        if os.environ.get('GITHUB_ACTION', None) is None:
            # create a local .env file and define these secret variables there:
            #  LOCAL_ACCESS_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxx
            #  LOCAL_ACCESS_NAME=xxxxxxxxxxxxxxxx
            os.environ['LKEB_CORE_ACCESS_TOKEN'] = os.environ['LOCAL_ACCESS_TOKEN']
            os.environ['LKEB_CORE_ACCESS_NAME'] = os.environ['LOCAL_ACCESS_NAME']

    # ********************TESTING SERIALIZE********************
    def test_to_json_no_core_feature(self):
        self.test_repo.checkout_branch('feature/XYZ_unittest_feature')
        test_obj = PluginBranchInfo(self.test_repo.directory)
        json_str = test_obj.to_json()
        expect_dict = {
            "_folder": test_obj.folder,
            "_version": "XYZ_unittest_feature",
            "_core_dep_type": 'LATEST',
            "_core_version": 'latest'}
        print(f'Saved core: f{json_str}')
        test_dict = json.loads(json_str)
        self.assertDictEqual(test_dict, expect_dict)

    def test_to_json_core_feature(self):
        self.test_repo.checkout_branch('feature/test_ci_cd')
        test_obj = PluginBranchInfo(self.test_repo.directory)
        json_str = test_obj.to_json()
        expect_dict = {
            "_folder": test_obj.folder,
            "_version": "test_ci_cd",
            "_core_dep_type": 'FEATURE',
            "_core_version": 'test_ci_cd'}
        print(f'Saved core: f{json_str}')
        test_dict = json.loads(json_str)
        self.assertDictEqual(test_dict, expect_dict)

    def test_to_json_release_core_feature(self):
        self.test_repo.checkout_branch('feature/core_0.1/ABC_unittest_feature')
        test_obj = PluginBranchInfo(self.test_repo.directory)
        json_str = test_obj.to_json()
        expect_dict = {
            "_folder": test_obj.folder,
            "_version": "ABC_unittest_feature",
            "_core_dep_type": 'RELEASE',
            "_core_version": '0.1'}
        print(f'Saved core: f{json_str}')
        test_dict = json.loads(json_str)
        self.assertDictEqual(test_dict, expect_dict)

    def test_to_json_release_core_plugin(self):
        self.test_repo.checkout_branch('release/core_0.1/1.0')
        test_obj = PluginBranchInfo(self.test_repo.directory)
        json_str = test_obj.to_json()
        expect_dict = {
            "_folder": test_obj.folder,
            "_version": "1.0",
            "_core_dep_type": 'RELEASE',
            "_core_version": '0.1'}
        print(f'Saved core: f{json_str}')
        test_dict = json.loads(json_str)
        self.assertDictEqual(test_dict, expect_dict)

    # ********************TESTING DESERIALIZE********************
    def test_from_json_no_core_feature(self):
        self.test_repo.checkout_branch('feature/XYZ_unittest_feature')
        test_pbinfo = PluginBranchInfo.from_json(
            json.dumps({
            "_folder": self.test_repo.directory,
            "_version": "XYZ_unittest_feature",
            "_core_dep_type": 'LATEST',
            "_core_version": 'latest'}))
        self.assertEqual('master', test_pbinfo.core_branch_name)
        self.assertEqual('XYZ_unittest_feature', test_pbinfo.version)
        self.assertEqual(self.test_repo.directory, test_pbinfo.folder)
        self.assertEqual('feature/XYZ_unittest_feature',
                         test_pbinfo.branch_name)

    def test_from_json_core_feature(self):
        self.test_repo.checkout_branch('feature/test_ci_cd')
        test_pbinfo = PluginBranchInfo.from_json(
            json.dumps({
            "_folder": self.test_repo.directory,
            "_version": "test_ci_cd",
            "_core_dep_type": 'FEATURE',
            "_core_version": 'test_ci_cd'}))
        self.assertEqual('feature/test_ci_cd', test_pbinfo.core_branch_name)
        self.assertEqual('test_ci_cd', test_pbinfo.version)
        self.assertEqual(self.test_repo.directory, test_pbinfo.folder)
        self.assertEqual('feature/test_ci_cd',
                         test_pbinfo.branch_name)

    def test_from_json_release_core_feature(self):
        self.test_repo.checkout_branch('feature/core_0.1/ABC_unittest_feature')
        test_pbinfo = PluginBranchInfo.from_json(
            json.dumps({
            "_folder": self.test_repo.directory,
            "_version": "ABC_unittest_feature",
            "_core_dep_type": 'RELEASE',
            "_core_version": '0.1'}))
        self.assertEqual('release/0.1', test_pbinfo.core_branch_name)
        self.assertEqual('ABC_unittest_feature', test_pbinfo.version)
        self.assertEqual(self.test_repo.directory, test_pbinfo.folder)
        self.assertEqual('feature/core_0.1/ABC_unittest_feature',
                         test_pbinfo.branch_name)

    def test_from_json_release_core_plugin(self):
        self.test_repo.checkout_branch('release/core_0.1/1.0')
        test_pbinfo = PluginBranchInfo.from_json(
            json.dumps({
            "_folder": self.test_repo.directory,
            "_version": "1.0",
            "_core_dep_type": 'RELEASE',
            "_core_version": '0.1'}))
        self.assertEqual('release/0.1', test_pbinfo.core_branch_name)
        self.assertEqual('1.0', test_pbinfo.version)
        self.assertEqual(self.test_repo.directory, test_pbinfo.folder)
        self.assertEqual('release/core_0.1/1.0',
                         test_pbinfo.branch_name)

    # ********************TESTING INIT FROM BRANCH********************
    def test_master_branch(self):
        self.test_repo.checkout_branch('master')
        test_obj = PluginBranchInfo(self.test_repo.directory)
        self.assertEqual(test_obj.version, 'latest')
        self.assertEqual(test_obj.core_version, 'latest')

    def test_feature_branch_core_latest(self):
        self.test_repo.checkout_branch('feature/XYZ_unittest_feature')
        test_obj = PluginBranchInfo(self.test_repo.directory)
        self.assertEqual(test_obj.version, 'XYZ_unittest_feature')
        self.assertEqual(test_obj.core_version, 'latest')

    def test_feature_branch_core_feature(self):
        self.test_repo.checkout_branch('feature/test_ci_cd')
        test_obj = PluginBranchInfo(self.test_repo.directory)
        self.assertEqual(test_obj.version, 'test_ci_cd')
        self.assertEqual(test_obj.core_version, 'test_ci_cd')

    def test_feature_core_release(self):
        self.test_repo.checkout_branch('feature/core_0.1/ABC_unittest_feature')
        test_obj = PluginBranchInfo(self.test_repo.directory)
        self.assertEqual(test_obj.version, 'ABC_unittest_feature')
        self.assertEqual(test_obj.core_version, '0.1')

    def test_release_branch(self):
        self.test_repo.checkout_branch('release/core_0.1/1.0')
        test_obj = PluginBranchInfo(self.test_repo.directory)
        self.assertEqual(test_obj.version, '1.0')
        self.assertEqual(test_obj.core_version, '0.1')

   # ********************TESTING CORE TIMESTAMP********************
    def test_master_branch_core_timestamp(self):
        self.test_repo.checkout_branch('master')
        test_obj = PluginBranchInfo(self.test_repo.directory)
        #  Expect the timestamp to be between Sept 2020 and Jan 2027
        print(f'test_cid_cd core timestamp {test_obj.get_timestamp_for_core_commit()}')
        self.assertGreater(test_obj.get_timestamp_for_core_commit(), 1600000000)
        self.assertLess(test_obj.get_timestamp_for_core_commit(), 1800000000)

    def test_feature_branch_core_timestamp(self):
        self.test_repo.checkout_branch('feature/test_ci_cd')
        test_obj = PluginBranchInfo(self.test_repo.directory)
        #  Expect the timestamp to be between Sept 2020 and Jan 2027
        print(f'test_cid_cd core timestamp {test_obj.get_timestamp_for_core_commit()}')
        self.assertGreater(test_obj.get_timestamp_for_core_commit(), 1600000000)
        self.assertLess(test_obj.get_timestamp_for_core_commit(), 1800000000)

    def test_feature_release_core_timestamp(self):
        self.test_repo.checkout_branch('release/core_0.1/1.0')
        test_obj = PluginBranchInfo(self.test_repo.directory)
        print(f'release 0.1 core timestamp {test_obj.get_timestamp_for_core_commit()}')
        # core release commit was at January 27, 2020 10:37:31
        self.assertEqual(test_obj.get_timestamp_for_core_commit(), 1580125051)

    def test_core_manifest_timestamp(self):
        manifest_path = pathlib.Path(pathlib.Path(__file__).parent.absolute(), 'data/conanmanifest.txt')
        self.assertEqual(PluginBranchInfo.read_manifest_timestamp(manifest_path), 1611246753)

    @classmethod
    def tearDownClass(cls):
        del cls.test_repo
