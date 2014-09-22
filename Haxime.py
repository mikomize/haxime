import sublime, sublime_plugin, subprocess, os, re, string, time
import xml.etree.ElementTree as ET

class BuildHxmlNotFound(Exception):
	def __init__(self, value):
		self.value = value;
	def __str__(self):
		return "hxml file not found ("+ self.value +")"

class Haxime:

	plugin_enabled_settings_key = "haxime_enabled"
	build_system_enabled_settings_key = "haxime_build_system_enabled"
	auto_completion_enabled_settings_key = "haxime_auto_completion_enabled"
	auto_completion_throttle_settings_key = "haxime_auto_completion_throttle"
	auto_completion_server_enabled_settings_key = "haxime_completion_server_enabled"
	server_port_settings_key = "haxime_server_port"

	haxe_exec_path_settings_key = "haxime_haxe_exec_path"
	haxe_std_path_settings_key = "haxime_haxe_std_path"
	haxe_haxelib_path_settings_key = "haxime_haxelib_path"

	build_hxml_file_settings_key = "haxime_build_hxml_file"
	cwd_path_settings_key = "haxime_cwd_path"

	scope_name = "source.haxe.2"

	servers = {}

	def get_plugin_settings(self):
		return sublime.load_settings("Haxime.sublime-settings")

	def get_setting(self, view, key):
		default_settings = self.get_plugin_settings()
		s = view.settings().get(key, default_settings.get(key))
		return s

	def plugin_enabled(self, view):
		return self.get_setting(view, self.plugin_enabled_settings_key)

	def auto_completion_enabled(self, view):
		in_scope = sublime.score_selector(view.scope_name(view.sel()[0].b), self.scope_name)
		return self.get_setting(view, self.plugin_enabled_settings_key) and in_scope > 0

	def auto_completion_server_enabled(self, view):
		return self.get_setting(view, self.auto_completion_server_enabled_settings_key)

	def build_system_enabled(self, view):
		return self.get_setting(view, self.build_system_enabled_settings_key)

	def get_completion_throttle(self, view):
		return self.get_setting(view, self.auto_completion_throttle_settings)

	def get_cwd(self, view):
		tmp = view.window().project_file_name()
		if (tmp == None):
			path = view.file_name()

		if (tmp == None):
			raise Exception('could not determine working directory (save your file first?)')

		dirname = os.path.dirname(tmp)
		settings_cwd = view.settings().get(self.cwd_path_settings_key)
		if settings_cwd != "":
			dirname += "/" + settings_cwd
		return dirname


	def get_build_hxml_path(self, view):
		path = self.get_cwd(view) + "/" + view.settings().get(self.build_hxml_file_settings_key)
		if os.path.exists(path) == False:
			raise BuildHxmlNotFound(path)

		return path
		

	def ensure_completion_server(self, view):
		port = self.get_setting(view, self.server_port_settings_key)
		if port in self.servers:
			return
		print ("ensuring completion server on port " + str(port))
		server = self.call_haxe(view, ['-v', '--wait', str(port), '--no-output'])

		self.servers[port] = server

	def get_completion(self, view, prefix, locations):
		#todo context completion, vars, functions
		region = view.line(locations[0]);
		region.b = locations[0];
		line = view.substr(region);
		m = re.search('(?<=\.|\()\w*$', line);
		if (m == None):
			print("nothing to complete")
			return []
		pref = m.group(0)

		if self.auto_completion_server_enabled(view) == False:
			return []

		self.ensure_completion_server(view)
		display = os.path.relpath(view.file_name(), self.get_cwd(view)) + '@' + str(locations[0] - len(pref))
		view.run_command('save');
		hndl = self.call_haxe(view, ['--connect', str(self.get_setting(view, self.server_port_settings_key)), '--no-output', '--display', display, self.get_build_hxml_path(view)])
		hndl.wait();
		output =  hndl.stderr.raw.readall()
		try:
			root = ET.fromstring(output)

		except:
			print("not an xml response, probably some error")
			return []

		res = []
		if root.tag == "list":
			for item in root:
				name = item.attrib["n"]
				signature = item.find("t").text

				toPaste = name
				snippet = self.make_snippet(signature)
				if snippet != "":
					toPaste += "(" + snippet + ")"
				res.append((name + "\t" + signature, toPaste))

		elif root.tag == "type":
			snippet = self.make_snippet(root.text)
			if snippet == "":
				snippet = " " #empty string will result with pasting first item in tuple
			res = [("function signature:\t" + root.text, snippet)]

		return res

	def make_snippet(self, tmp):
		m = re.findall(r"(\w+\s?:\s?(?:\([\w\s,\-><\.\(\)]+\)|[\w\s,><\.]+))", tmp.strip())

		if len(m) > 0 and re.match(r"^this", m[0]) != None: #yeah i suck and regexp, too lazy merge to it with the one above
			m.pop(0)
		toJoin = []
		i = 0
		for item in m: #make it subject to tab
			i = i+1
			toJoin.append("${" + str(i) + ":" + item.strip() + "}")
		joined = ", ".join(toJoin);
		return joined

	def build(self, view):
		hndl = self.call_haxe(view, [self.get_build_hxml_path(view)])
		hndl.wait()
		return hndl.stderr.raw.readall().decode()

	def call_haxe(self, view, args):
		settings = view.settings()
		env = os.environ.copy()

		cmd = [settings.get(self.haxe_exec_path_settings_key, 'haxe')]
		if (settings.has(self.haxe_std_path_settings_key)):
			env['HAXE_LIBRARY_PATH'] = settings.get(self.haxe_std_path_settings_key) #legacy 
			env['HAXE_STD_PATH'] = settings.get(self.haxe_std_path_settings_key)


		cmd_args = cmd + args +  ['--cwd', self.get_cwd(view)]
		print ("calling haxe cmd")
		print (cmd_args)
		return subprocess.Popen(cmd_args, env=env, stderr=subprocess.PIPE, stdout=subprocess.PIPE, cwd=self.get_cwd(view))


haxime = Haxime()

class HaximeWatcher(sublime_plugin.EventListener):

	def on_query_completions(self, view, prefix, locations):
		if haxime.plugin_enabled(view) and haxime.auto_completion_enabled(view):
			return haxime.get_completion(view, prefix, locations)



class HaximeBuild(sublime_plugin.WindowCommand):
 	def run(self):
 		view = self.window.active_view()
 		
 		if not hasattr(self, 'output_view'):
 			self.output_view = self.window.create_output_panel("exec")

 		self.output_view.settings().set("result_file_regex", "^(.+):(\\d+): (?:lines \\d+-\\d+|character(?:s \\d+-| )(\\d+)) : (.*)$")
 		self.output_view.settings().set("result_base_dir", haxime.get_cwd(self.window.active_view()))

 		self.window.create_output_panel("exec")
 		self.window.run_command("show_panel", {"panel": "output.exec"})

 		if haxime.plugin_enabled(view) == False or haxime.build_system_enabled(view) == False:
 			res = "Haxime build system disabled, check 'haxime_build_system_enabled' and 'haxime_enabled' settings"
 			self.output_view.run_command('append', {'characters': res, 'force': True, 'scroll_to_end': True})
 			return None

 		print("running haxime build")
 		res =  haxime.build(self.window.active_view())
 		if res == "":
 			res = "[Build success]"
 		else:
 			res = "[Build fail]\n" + res
 		self.output_view.run_command('append', {'characters': res, 'force': True, 'scroll_to_end': True})

