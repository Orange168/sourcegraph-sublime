import os
import sys

sys.path.append(os.path.dirname(__file__))
import sg_lib

import sublime

import sublime_plugin

SETTINGS_FILENAME = 'Sourcegraph.sublime-settings'
GOSUBLIME_SETTINGS_FILENAME = 'GoSublime.sublime-settings'
SUBLIME_VERSION = int(sublime.version())

SG_LIB_INSTANCE = {}


def find_gopath_from_gosublime():
	if 'env' in sublime.load_settings(GOSUBLIME_SETTINGS_FILENAME):
		gosubl_env = sublime.load_settings(GOSUBLIME_SETTINGS_FILENAME).get('env')
		if 'GOPATH' in gosubl_env:
			return gosubl_env['GOPATH'].replace('$HOME', os.environ.get('HOME')).replace(':$GS_GOPATH', '')
	return None


def load_settings(settings):
	sgedge_settings = sg_lib.Settings()

	if settings.has('LOG_LEVEL'):
		sg_lib.LOG_LEVEL = settings.get('LOG_LEVEL')
		sg_lib.log_output('[settings] Found logging setting in Settings file: %s' % sg_lib.LOG_LEVEL)
	if settings.has('ENABLE_LOOKBACK'):
		sgedge_settings.ENABLE_LOOKBACK = settings.get('ENABLE_LOOKBACK')
	if settings.has('SG_BASE_URL'):
		sgedge_settings.SG_BASE_URL = settings.get('SG_BASE_URL').rstrip('/')
	if settings.has('SG_LOG_FILE'):
		sg_lib.SG_LOG_FILE = settings.get('SG_LOG_FILE')
	if settings.has('AUTO_OPEN'):
		sgedge_settings.AUTO_OPEN = settings.get('AUTO_OPEN')
	if settings.has('AUTO_PROCESS'):
		sgedge_settings.AUTO_PROCESS = settings.get('AUTO_PROCESS')
	if settings.has('GOBIN'):
		sgedge_settings.GOBIN = settings.get('GOBIN').rstrip(os.sep)
	shell_gopath, err, return_code = sg_lib.run_native_shell_command(sgedge_settings.ENV.get('SHELL'), ['echo', '${GOPATH}'])
	if settings.has('GOPATH'):
		sgedge_settings.ENV['GOPATH'] = str(settings.get('GOPATH').rstrip(os.sep)).strip()
		sg_lib.log_output('[settings] Using GOPATH found in Sublime settings file: %s' % sgedge_settings.ENV['GOPATH'])
	elif shell_gopath and shell_gopath.rstrip(os.sep).strip() != '':
		sgedge_settings.ENV['GOPATH'] = shell_gopath.rstrip(os.sep).strip()
	elif find_gopath_from_gosublime():
		sgedge_settings.ENV['GOPATH'] = find_gopath_from_gosublime()
		sg_lib.log_output('[settings] Found GOPATH in GoSublime settings: %s' % sgedge_settings.ENV['GOPATH'])
	if 'GOPATH' in sgedge_settings.ENV and sgedge_settings.ENV.get('GOPATH') != '':
		sgedge_settings.ENV['GOPATH'] = sgedge_settings.ENV['GOPATH'].replace('~', os.environ.get('HOME'))
	global SG_LIB_INSTANCE
	SG_LIB_INSTANCE = sg_lib.SourcegraphEdge(sgedge_settings)
	SG_LIB_INSTANCE.post_load()


def reload_settings():
	old_base_url = SG_LIB_INSTANCE.settings.SG_BASE_URL
	settings = sublime.load_settings(SETTINGS_FILENAME)
	load_settings(settings)
	if SG_LIB_INSTANCE.settings.SG_BASE_URL != old_base_url and SG_LIB_INSTANCE.settings.AUTO_OPEN:
		SG_LIB_INSTANCE.open_edge_channel()


def plugin_loaded():
	settings = sublime.load_settings(SETTINGS_FILENAME)
	settings.clear_on_change('sg-reload')
	settings.add_on_change('sg-reload', reload_settings)

	gosublime_settings = sublime.load_settings(GOSUBLIME_SETTINGS_FILENAME)
	gosublime_settings.clear_on_change('sg-reload-gosubl')
	gosublime_settings.add_on_change('sg-reload-gosubl', reload_settings)

	load_settings(settings)


def cursor_offset(view):
	row, col = view.rowcol(view.sel()[0].begin())
	symbol_start_offset = sg_lib.search_for_symbols(view.sel()[0].begin(), view.substr(view.line(view.sel()[0])), row, col, SG_LIB_INSTANCE.settings.ENABLE_LOOKBACK)

	string_before = view.substr(sublime.Region(0, symbol_start_offset))
	string_before.encode('utf-8')
	buffer_before = bytearray(string_before, encoding='utf8')
	return str(len(buffer_before))


def process_selection(view):
	if len(view.sel()) == 0:
		return
	args = sg_lib.LookupArgs(filename=view.file_name(), cursor_offset=cursor_offset(view), preceding_selection=str.encode(view.substr(sublime.Region(0, view.size()))), selected_token=view.substr(view.extract_scope(view.sel()[0].begin())))
	SG_LIB_INSTANCE.on_selection_modified_handler(args)


class SgOpenEdgeCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		SG_LIB_INSTANCE.open_edge_channel(hard_refresh=True)
		process_selection(self.view)


class SgOpenLogCommand(sublime_plugin.WindowCommand):
	def run(self):
		self.window.open_file(sg_lib.SG_LOG_FILE)


class SgManualProcessCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		process_selection(self.view)


class SgAutoProcessCommand(sublime_plugin.EventListener):
	def __init__(self):
		super().__init__()

	def on_selection_modified_async(self, view):
		if SG_LIB_INSTANCE.settings.AUTO_PROCESS:
			process_selection(view)
