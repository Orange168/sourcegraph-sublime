import os
import sys
sys.path.append(os.path.dirname(__file__))
import sourcegraph_lib
from sourcegraph_lib import ExportedParams
from sourcegraph_lib import LookupArgs


class TestCase(object):
	def __init__(self, lookup_args=None, expected_output=None):
		super(TestCase, self).__init__()
		self.lookup_args = lookup_args
		self.expected_output = expected_output


class Tests(object):
	GODEFINFO_INSTALL = TestCase(lookup_args=LookupArgs(filename='local_func.go', cursor_offset='63', selected_token='func_helper('), expected_output=ExportedParams(Error=sourcegraph_lib.ERR_GODEFINFO_INSTALL.title, Fix=sourcegraph_lib.ERR_GODEFINFO_INSTALL.description))
	GOPATH_EMPTY = TestCase(lookup_args=LookupArgs(filename='.go', cursor_offset='0', selected_token=''), expected_output=ExportedParams(Error=sourcegraph_lib.ERR_GOPATH_UNDEFINED.title, Fix=sourcegraph_lib.ERR_GOPATH_UNDEFINED.description))

	def __init__(self):
		self.PACKAGE_IMPORT = TestCase(lookup_args=LookupArgs(filename='package_import.go', cursor_offset='30', selected_token='net/http'), expected_output=ExportedParams(Repo='net/http', Package='net/http', Status=sourcegraph_lib.STATUS_GOOD))
		self.PACKAGE_INSIDE_FUNC = TestCase(lookup_args=LookupArgs(filename='package_inside_func.go', cursor_offset='72', selected_token='net/http'), expected_output=ExportedParams(Repo='net/http', Package='net/http', Status=sourcegraph_lib.STATUS_GOOD))
		self.IMPORTED_STRUCT = TestCase(lookup_args=LookupArgs(filename='imported_struct.go', cursor_offset='93', selected_token='Request'), expected_output=ExportedParams(Def='Request', Repo='net/http', Package='net/http', Status=sourcegraph_lib.STATUS_GOOD))
		self.IMPORTED_STRUCT_FIELD = TestCase(lookup_args=LookupArgs(filename='imported_struct_field.go', cursor_offset='114', selected_token='Vars'), expected_output=ExportedParams(Def='RouteMatch/Vars', Repo='github.com/gorilla/mux', Package='github.com/gorilla/mux', Status=1))
		self.LOCAL_FUNC = TestCase(lookup_args=LookupArgs(filename='local_func.go', cursor_offset='63', selected_token='helper('), expected_output=ExportedParams(Def='func_helper', Repo='github.com/luttig/sg-live-plugin-tests/go_tests', Package='github.com/luttig/sg-live-plugin-tests/go_tests', Status=sourcegraph_lib.STATUS_GOOD))
		self.LOCAL_VAR = TestCase(lookup_args=LookupArgs(filename='local_var.go', cursor_offset='58', selected_token='test_var'), expected_output=ExportedParams(Error=sourcegraph_lib.ERR_GODEFINFO_INVALID.title, Fix=sourcegraph_lib.ERR_GODEFINFO_INVALID.description, Status=sourcegraph_lib.STATUS_BAD))

	def syntax_tests(self):
		all_tests = dict()
		for test_name in self.__dict__:
			if self.__dict__[test_name]:
				all_tests[test_name] = self.__dict__[test_name]
		return all_tests
