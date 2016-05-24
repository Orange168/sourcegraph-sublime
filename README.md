# Sourcegraph for Sublime [![CircleCI](https://circleci.com/gh/sourcegraph/sourcegraph-sublime.svg?style=svg)](https://circleci.com/gh/sourcegraph/sourcegraph-sublime)

## Overview

Sourcegraph for Sublime allows you to view Go definitions in real-time on [sourcegraph.com](http://www.sourcegraph.com) as you code, so you can stay focused on what's important: your code. When your cursor is on a certain Go symbol, it should load in a channel in your browser:

![Sourcegraph for Sublime](images/setup.jpg)

## Setup

To install Sourcegraph for Sublime, clone `sourcegraph-sublime` into your Sublime Text 3 Packages folder:

OSX:

```shell
git clone ssh://git@github.com/sourcegraph/sourcegraph-sublime ~/Library/Application\ Support/Sublime\ Text\ 3/Packages/sourcegraph-sublime
```

Linux:

```shell
git clone ssh://git@github.com/sourcegraph/sourcegraph-sublime ~/.config/sublime-text-3/Packages/sourcegraph-sublime
```

Windows:

```shell
cd %APPDATA%\Sublime Text 3\Packages
git clone ssh://git@github.com/sourcegraph/sourcegraph-sublime
```


## Usage

Sourcegraph for Sublime should automatically open a browser tab to initialize your Sourcegraph session when in Go files. If, for any reason, your tab gets closed, press <kbd>&#8984;</kbd>+<kbd>.</kbd>, <kbd>&#8984;</kbd>+<kbd>0</kbd> in any file to reopen the Sourcegraph tab. Alternatively, you can click on `Sublime Text > Preferences > Package Settings > Sourcegraph > Reopen Browser Tab`. As you navigate through Go files, your browser should automatically load the definition and references for recognized symbols.

## Flags

Sourcegraph for Sublime has a number of flags to customize your experience. To change your Sourcegraph settings, open `Sourcegraph.sublime-settings` by clicking `Sublime Text > Preferences > Package Settings > Sourcegraph > Settings - User`.

### Custom GOBIN or GOPATH

Sourcegraph for Sublime searches your shell to find `GOBIN`, the full path of the Go executable. This is typically `$GOROOT/bin/go`. Similarly, Sourcegraph loads your `/bin/bash` startup scripts to search for the `GOPATH` environment variable. If Sourcegraph cannot find your environment variables, or if you would like to use a custom `GOPATH` or `GOBIN`, add them in the settings file as follows:

```yml
{
	...
	"GOPATH": "/path/to/gopath",
	"GOBIN": "/path/to/gobin",
	...
}
```

### Auto-process selection

With the auto-process feature, Sourcegraph automatically processes your code as you type. If you want to toggle this feature, set the `AUTO_PROCESS` flag in your settings file. If you set it to `false`, you must press <kbd>&#8984;</kbd>+<kbd>,</kbd>, <kbd>&#8984;</kbd>+<kbd>0</kbd> to process your current selection.

```yml
{
	...
	"AUTO_PROCESS": true,
	...
}
```

### Auto-open browser

If set to `true`, this setting will auto-open the Sourcegraph channel in your browser when you click on a definition in Go. If it is set to `false`, then you can access the channel by clicking <kbd>&#8984;</kbd>+<kbd>.</kbd>, <kbd>&#8984;</kbd>+<kbd>0</kbd>. To disable auto-opening, set the `AUTO_OPEN` flag to `false` in your settings:

```yml
{
	...
	"AUTO_OPEN": true,
	...
}
```

### Verbose logging

This setting gives verbose output from Sourcegraph for Sublime to the Sublime Text console, which can be helping when troubleshooting Sourcegraph for Sublime. To open the Sublime console, simply type <kbd>control</kbd>+<kbd>`</kbd>. Different levels of logging are available:

No logging: `0`

Only log symbols identified by godefinfo: `1`

Log network calls: `2`

Log all debugging information: `3`

```yml
{
	...
	"LOG_LEVEL": 1,
	...
}
```

## Godefinfo

Sourcegraph for Sublime should automatically install `godefinfo` when it loads your settings. However, if you still receive error message about `godefinfo` installation, you can install it manually by running the following command:

```shell
go get -u github.com/sqs/godefinfo
```

### Local server

If you want to try Sourcegraph for Sublime on a local Sourcegraph server, you can define its base URL in this file using the key `SG_BASE_URL`.

```yml
{
	...
	"SG_BASE_URL": "https://www.sourcegraph.com",
	...
}
```

## Support

Sourcegraph for Sublime has currently only been tested using Sublime Text 3.
