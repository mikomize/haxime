## Haxime
Haxe plugin for [Sublime 3](http://www.sublimetext.com/3)
#### Introduction
I've been using [clemos/haxe-sublime-bundle](https://github.com/clemos/haxe-sublime-bundle) for developing in Haxe using Sublime but mainly due to lack of support for multiple haxe compilers and some other inconvenient for me features i decided to write my own plugin. I have included his .tmLanguage syntax file though, so all credits goes to him for it.
#### Features
- [X] fully configurable including setting for haxe compiler per project
- [X] auto completion using haxe completion server
- [X] build system for haxe
- [X] highlighting build errors in code
- [X] highlighting errors returned from completion server in code
- [X] auto completion extended by variety of snippets
- [ ] better context autocompletion
- [ ] integration with Package Control
 
#### Install
Go to your sublime package directory (one way to find it is to click Sublime Text -> Preferences -> Browse Packages) , then:
```
git clone https://github.com/mikomize/haxime.git
```

#### Usage
* [Haxe compiler](http://haxe.org/download/) is required as external dependency. By default **Haxime** will search system path to find it. To provide path to specific haxe instance, use settings.
* Build system by default looks for `build.hxml` file at level of `.sublime-project` file. If project file does not exist, opened `.hx` file directory is taken into consideration instead. Paths and `.hxml` file name can be altered using settings.
* In general , using configured projects in sublime is advised

#### Settings

I recommend configuring haxime using project settings. Example poject setting:
```
{
	"folders":
	[
		{
			"follow_symlinks": true,
			"path": "server"
		}
	],
	"settings": {
		"haxime_build_hxml_file": "production.hxml",
		"haxime_cwd_path": "server",
		"haxime_haxe_exec_path": "/usr/lib/haxe-3.2.0/haxe",
		"haxime_haxe_std_path"": "/usr/lib/haxe-3.2.0/haxe/std
	}
}
```

* `haxime_build_hxml_file` : relative to your cwd path of your `.hxml` file. Default `build.hxml`
* `haxime_cwd_path` : relative to your project dir (dir that contains `.sublime-project` file). Default `""`
* `haxime_enabled"` : enables/disabled plugin. Default `true`
* `haxime_build_system_enabled` : enables/disabled plugin build system. Default `true`
* `haxime_auto_completion_enabled` : enables/disables plugin auto completion. Default `true`
*	`haxime_completion_server_enabled` : enables/disables use of haxe completion server for plugin auto completion. Default `true`
* `haxime_parse_errors_from_auto_completion` : haxe autocompletion server while auto completing tries to suppres all errors to provide completion, however sometimes it cannot be done and in that case, completion server returns "compilation" errors that caused him to fail. Setting it to `true` enables error highlighting similar to highlighting regular build errors. The reason you might not want to have it turned on is that completion server does not really compile in the way that normal build would do and that can result in strange errors that does not apply to your project. Especially it happens when it comes to use macros. Default `true`
* `haxime_server_port` : provides port number used for setting up completion server, useful for multiple haxe instances used in diffrent projects. Default `6113`
* `haxime_haxe_exec_path` : path to haxe binary. Default `haxe`
* `haxime_haxe_std_path` : path to haxe std lib. Default `""`

#### Troubleshooting

* Make sure that your desired haxe instance is installed and add to system paths. If not or using multiple haxe instances make sure that your paths are configured in project settings (or user settings)
* If completion server does not seem to work, make sure that server port is free. Server port can be configured in settings.
* Due to my limited access to windows os it might happen that some of the features wont work on it. Feel free to let me know if that happens via github issues system, i'll try to do my best to fix it.
