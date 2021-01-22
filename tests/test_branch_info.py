import json
import unittest
from rules_support.branch_info import BranchInfo
from tests.utils import TestRepo


class TestBranchInfo(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.test_repo = TestRepo(prefix=cls.__name__)

    @classmethod
    def tearDownClass(cls):
        del cls.test_repo

    def setUp(self):
        self.master_branch = BranchInfo(self.test_repo.directory)
        self.dict_form = {"_folder": self.master_branch.folder}

    def test_branch_name(self):
        self.assertEqual(self.master_branch.branch_name, 'master')

    def test_to_json(self):
        json_str = self.master_branch.to_json()
        test_dict = json.loads(json_str)
        self.assertDictEqual(test_dict, self.dict_form)

    def test_from_json(self):
        test_binfo = BranchInfo.from_json(json.dumps(self.dict_form))
        self.assertEqual(test_binfo.folder, self.master_branch.folder)
        self.assertEqual(test_binfo.branch_name,
                         self.master_branch.branch_name)


if __name__ == '__main__':
    unittest.main()
