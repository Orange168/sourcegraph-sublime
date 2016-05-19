import os
import subprocess
import sys
import unittest

try:
    from unittest.mock import patch
except:
    from mock import patch

sys.path.append(os.path.dirname(__file__))
import sg_lib

from test_data import Tests


def start_default_instance():
    test_settings = sg_lib.Settings()
    sg_lib_instance = sg_lib.SourcegraphEdge(test_settings)
    sg_lib_instance.post_load()
    return sg_lib_instance


def check_output(test_case_class, test_output, expected_output):
    if expected_output is None:
        test_case_class.assertIsNone(test_output)
        return
    test_case_class.assertEqual(expected_output, test_output)


def run_go_test(test, sg_lib_instance):
    full_filename = os.path.join(sg_lib_instance.settings.ENV['GOPATH'], 'src', 'github.com', 'luttig', 'sg-live-plugin-tests', 'go_tests', test.lookup_args.filename)
    buff = b''
    if test.lookup_args.filename != '' and test.lookup_args.filename != '.go':
        try:
            with open(full_filename, 'r') as test_file:
                buff = test_file.read().encode()
        except:
            pass
    return sg_lib_instance.get_sourcegraph_request(full_filename, test.lookup_args.cursor_offset, buff, test.lookup_args.selected_token)


class VerifyClearCacheOnHardReload(unittest.TestCase):
    @patch('sg_lib.SourcegraphEdge.open_channel_os')
    def test(self, mock_open_edge_channel):
        sg_lib_instance = start_default_instance()
        self.assertIsNone(sg_lib_instance.LAST_SYMBOL_LOOKUP)
        self.assertIsNone(sg_lib_instance.LAST_REPO_PACKAGE_LOOKUP)

        imported_struct_test = Tests().IMPORTED_STRUCT
        run_go_test(imported_struct_test, sg_lib_instance)
        self.assertEqual(imported_struct_test.lookup_args.selected_token, sg_lib_instance.LAST_SYMBOL_LOOKUP)
        self.assertEqual(imported_struct_test.expected_output.Repo, sg_lib_instance.LAST_REPO_PACKAGE_LOOKUP)

        sg_lib_instance.open_edge_channel(hard_refresh=True)
        self.assertIsNone(sg_lib_instance.LAST_SYMBOL_LOOKUP)
        self.assertIsNone(sg_lib_instance.LAST_REPO_PACKAGE_LOOKUP)


class VerifySyntaxVarieties(unittest.TestCase):
    def test(self):
        syntax_tests = Tests().syntax_tests()
        for test in syntax_tests:
            sg_lib_instance = start_default_instance()
            test_params = syntax_tests[test]
            test_output = run_go_test(test_params, sg_lib_instance)
            check_output(self, test_output, test_params.expected_output)


class VerifyGoPathEmptyError(unittest.TestCase):
    def test(self):
        sg_lib_instance = start_default_instance()
        sg_lib_instance.settings.ENV['GOPATH'] = ''
        test = Tests.GOPATH_EMPTY
        test_output = run_go_test(test, sg_lib_instance)
        check_output(self, test_output, test.expected_output)

        error_message = sg_lib_instance.add_gopath_to_path()
        self.assertEqual(error_message.Error, sg_lib.ERR_GOPATH_UNDEFINED.title)
        self.assertEqual(error_message.Fix, sg_lib.ERR_GOPATH_UNDEFINED.description)


# When godefinfo binary not yet installed
class VerifyGodefInfoInstallError(unittest.TestCase):
    def test(self):
        sg_lib_instance = start_default_instance()
        sg_lib_instance.settings.ENV['GOPATH'] = '/'
        sg_lib_instance.settings.ENV['PATH'] = '/path/that/does/not/contain/godefinfo'
        test = Tests.GODEFINFO_INSTALL
        test_output = run_go_test(test, sg_lib_instance)
        check_output(self, test_output, test.expected_output)


class VerifyGoBinaryError(unittest.TestCase):
    def test(self):
        sg_lib_instance = start_default_instance()
        bad_gobin_path = '/path/not/to/gobin'
        test_output = sg_lib.godefinfo_auto_install(sg_lib_instance.settings.ENV['SHELL'], bad_gobin_path, sg_lib_instance.settings.ENV['GOPATH'])
        self.assertEqual(test_output.Error, sg_lib.ERR_GO_BINARY.title)
        self.assertEqual(test_output.Fix, sg_lib.ERR_GO_BINARY.description)


class ValidateSettings(unittest.TestCase):
    def test(self):
        settings = sg_lib.Settings()
        validation_output = sg_lib.validate_settings(settings)
        if validation_output is not None:
            self.fail('Failed settings validation: %s' % validation_output.title)


class VerifyGodefinfoAutoUpdate(unittest.TestCase):
    def git_commit(self, git_dir):
        get_commit_process = subprocess.Popen(['git', 'rev-parse', 'HEAD'], cwd=git_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        commit, stderr = get_commit_process.communicate()
        self.assertEqual(stderr, b'')
        return commit

    def test(self):
        test_settings = sg_lib.Settings()
        godefinfo_dir = os.path.join(os.environ.get('GOPATH'), 'src', 'github.com', 'sqs', 'godefinfo')
        current_commit = self.git_commit(godefinfo_dir)

        reset_commit_process = subprocess.Popen(['git', 'reset', '--hard', 'HEAD~'], cwd=godefinfo_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        reset_commit, stderr = reset_commit_process.communicate()
        self.assertEqual(stderr, b'')

        old_commit = self.git_commit(godefinfo_dir)
        self.assertNotEqual(current_commit, old_commit)

        sg_lib.SourcegraphEdge(test_settings).post_load()
        self.assertEqual(current_commit, self.git_commit(godefinfo_dir))


# When godef is called on package that user doesn't have, send error message to user on how to install it
class VerifyGoGetError(unittest.TestCase):
    def test(self):
        return  # TODO
        sg_lib_instance = start_default_instance()
        package_name = 'asdf'
        test = Tests.BAD_IMPORT_PATH
        test.expected_output = sg_lib.ExportedParams(Error=sg_lib.ERR_GO_GET(package_name).title, Fix=sg_lib.ERR_GO_GET(package_name).description)
        test_output = run_go_test(test, sg_lib_instance)
        check_output(self, test_output, test.expected_output)

if __name__ == '__main__':
    unittest.main()
