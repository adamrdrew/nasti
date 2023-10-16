[![Build Status](https://github.com/adamrdrew/nasti/actions/workflows/tests.yml/badge.svg?branch=master)](https://github.com/adamrdrew/nasti/actions)
[![codecov](https://codecov.io/gh/adamrdrew/nasti/branch/master/graphs/badge.svg?branch=master)](https://codecov.io/github/adamrdrew/nasti?branch=master)

 <center><img src="images/logo.png"></center>

# NASTI
NASTI's A Strange Templating Implementation.

NASTI allows you to create project templates, similar to tools like [Cookiecutter](https://github.com/cookiecutter/cookiecutter). What makes NASTI unique is that your project templates remain as valid, living code. You can run, test, and debug your project templates just like any other application while still enabling end users to bootstrap new projects from your template.

## Features
* Templates remain valid source code you can run, build, etc
* No opinionated project or directory structure
* Works with any language
* Tightly scoped single-file template definition
* Powerful template and project validation system
* Rich text markup including colors, styles, and emoji
* Interactive and silent modes
* Silent mode accepts input on the command line or from JSON or YAML files
* Super easy, barely an inconvenience

## Installation
```sh
$ pip install nasti
```

## Usage

```sh
# Process a template on github
$ nasti process git@github.com:somedev/some-template.git
# Or gitlab, or any other git repo you can clone
$ nasti process git@gitlab.mycompany.com:someorg/some-template.git
# Process a local template
$ nasti process ~/Development/some-template
# Specify an output directory
$ nasti process ~/Development/some-template great_new_app
# Don't let NASTI greate your new project's repo
$ nasti process --git false ~/Development/some-template
# Accept all default values for mutations that have them
$ nasti process -d ~/Development/some-template great_new_app
# Silent mode with input provided on the command line
$ nasti process -s "app_name='My Great App',contact_name='Adam Drew',api_path='my-api',contact_email='adam@email.net'" ~/Development/some-template great_new_app 
# Silent mode with input provided from a YAML file
$ nasti process -f user_input.yaml my_new_app/ 
# Silent mode with input provided by a JSON file
$ nasti process -f user_input.json my_new_app/
```

## Template Creation
All you need to get started is a project you that want to be available as a template. It can be in any language, with any project layout. 

Simply add a nastifile called `nasti.yaml` to the root of your project and add some mutations. Mutations are definition of text replacement operations.

```yaml
---
mutations:
    # Identifies your promp internally, in error messages, and in silent mode
  - name: "github"
    # Prompt to present to the template user
    prompt: "Github Repo"
    # Additional help for the template user
    help: "The github repo is the location of your github repo. Should be in the form of github.com/user_or_org/repo"
    # The text we're going to replace with the user input
    replace: "github.com/somedev/some-project"
    # The files to perform the text substitution in
    files:
      - "go.mod"
      - "providers/database/main.go"
      - "routes/api.go"
      - "routes/main.go"
      - "routes/probes.go"
      - "main.go"
      - "main_test.go" 
    # Optional validation. You can specify a regex or one of the pre-built validations
    validation:
      regex: ^github\.com/[a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+$
```

The mutation format is very simple, and you can add as many mutations as you'd like. Most of the keys are required; `validations` and `help` are optional, but strongly encouraged.

Next verify your nastifile:
```bash
$ nasti validate
✔ Nastifile is valid.
```

If there's something wrong with your nastifile, such as a mutation being applied to a file that doesn't contain the replacement text, or an omitted field, `validate` will tell you:

```bash
$ nasti validate
❌ Nastifile is invalid.
Error: mutation email file: README.md at: /home/adamdrew/Development/someapp/README.md does not contain addrew@corpo.net 

$ nasti validate
❌ Nastifile is invalid. 
Error: Invalid mutation config: {'name': 'quay', 'help': 'The quay repo is the location of your container image. Should be in the form of quay.io/username/repo', 'replace': 'quay.io/someorg/some-project', 'files': ['Makefile'], 'validations': ['^quay\\.io/[a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+$']} missing 'prompt'
```

You can easily build out your nastifile by adding or updating mutations, validating, and fixing what doesn't work. It also makes a good fit for an automated PR check in your repo.

### Find Files Matching a Mutation
Mutations are file-scoped, meaning they'll only replace text in files in the mutation's file list. But what if you aren't sure whether you have the file list complete? Maybe the text you want to replace is in a file you forgot to add to the file list. The `find` command solves this problem by finding all files that contain your mutation replacement text but aren't in your mutation file lists:

```
$ nasti find tests/nastifiles/mutation_unmentioned_files/
Searching for files that match mutations but aren't mentioned in Nastifile...

❗ The following mutations match files not listed in the nastifile:

Mutation example_mutation matches but does not reference:
    • files/nested/unmentioned
    • files/unmentioned
```

In the example above the nastifile has a mutation called `example_mutation` that would match the files `files/nested/unmentioned` and `files/unmentioned` but those files don't appear in the `example_mutation` file list.

### Validation Kinds
As shown above you can create any custom validation regex you want, but for common tasks we ship a bunch of prebuilt validations thanks to the excellent [Validators](https://github.com/python-validators/validators) library.

Here's an example:
```yaml
---
mutations:
  - name: "route"
    prompt: "Route"
    help: "The route the feature responds from"
    replace: "example_route"
    files:
      - "routes/routes.py"
    validation:
      kind: "slug"
```

The valid kinds are:
```
kinds = {
    "domain":       validators.domain,
    "email":        validators.email,
    "ip_address":   validators.ip_address,
    "slug":         validators.slug,
    "url":          validators.url,
    "uuid":         validators.uuid,
}
```

### Globals and Default Templates
You may want to make the same input available to multiple mutations. Globals allow you to gather information from the user and then reference that input in mutations. Globals are accessed through mutation features called default templates. Default templates use Jina2 template syntax allowing you to create derived values such as converting "App Name" to "app_name" or combine mutliple globals.

Example:
```yaml
---
globals:
  - name: "app_name"
    prompt: "App Name"
    help: "The name of your application"
mutations:
  - name: "example_mutation"
    prompt: "Example Mutation"
    help: "Help for an example mutation"
    replace: "example text to replace"
    default: "{{ app_name }}"
    files: []
    validation:
      kind: "slug"
```

In the above example the user will first be prompted to enter data for the global called "app_name". Whatever the user enters will be used as the default value for the mutation "example_mutation". If a default is presented to the user they'll have the option to hit enter without entering any input to use the default.

A more complex example showing the Jinja2 template syntax:
```yaml
---
globals:
  - name: "app_name"
    prompt: "App Name"
    help: "The name of your application"
mutations:
  - name: "example_mutation"
    prompt: "Example Mutation"
    help: "Help for an example mutation"
    replace: "example text to replace"
    default: "{{ app_name.lower().split(' ') | join('-') }}"
    files: []
    validation:
      kind: "slug"
```

In that example if the user entered "My Great App" for the "app_name" global the "example_mutation" would have a default value of "my_great_app". Jinja2 syntax is extremely power, allowing you to use built in filters, call native Python methods, and more. [Check out their documentaiton](https://jinja.palletsprojects.com/en/2.10.x/templates/) for more info. 

Also, note that globals support validations using exactly the same syntax as mutaitons:

```yaml
globals:
  - name: "route_prefix"
    prompt: "Route Prefix"
    help: "Your route prefix"
    validation:
      kind: slug
```

### Greeting
You can display a message to the user via a greeting in your Nastifile. This is a good place to warn a user of what to expect or any prerequisite work you expect them to have done before using the template:

```yaml
greeting: "Welcome to the greeting!"
globals:
  - name: "app_name"
    prompt: "App Nme"
    help: "The name of your application"
```

### Hooks
You can choose to run scripts, such as shell scripts, before and after your template process. This can be useful for doing things like removing files, moving or renaming files, etc. This is done via a hooks property of the Nastifile

```yaml
hooks:
  before_script: "before_nasti.sh"
  after_script: "after_nasti.sh"
  auto_cleanup: true
globals:
  - name: "app_name"
    prompt: "App Nme"
    help: "The name of your application"
```

The example above will run `before_nasti.sh` before running the globals and mutations, run `after_nasti.sh` after running the globals and mutations, and then delete those scripts.

The value of the script field must be an executable script that can be run with sh.

### Rich Text Templates
Nasti can produce rich text output including colors, styles, emojis and more anywhere you specify text in your template, such as prompts, globals, or the greeting message. This functionality is provided by the awesome [Rich](https://github.com/Textualize/rich) library for Python.

Example:
```
---
greeting: >

  :waving_hand: [bold blue]Welcome to the ConsoleDot Go Starter App generator![/bold blue]


  :stop_sign: [bold blue]Before generating your app please do the following:[/bold blue]
    [green]:heavy_check_mark:[/green] Ensure you have access to the ephemeral cluster
    [green]:heavy_check_mark:[/green] Create a new Quay repo for your app
    [green]:heavy_check_mark:[/green] Create a new GitHub repo for your app

  :book: [bold blue]Documentation:[/bold blue]
    :link: [link=https://ourdocs.com/ephemeral][blue]Ephemeral Cluster Access[/blue][/link]
    :link: [link=https://gitlab.internal.com./repo[blue]Create Quay Repo in App Interface[/blue][/link]

globals:
  - name: "app_name"
    prompt: ":computer: [green]App Name[/green]"
    help: "[gray][italic]Alpha-numeric. Spaces. No special characters. Example: My Great App[/italic][/gray]"
    validation:
      regex: ^[A-Za-z0-9 ]+$
```

Produces output that looks like this:
![Rich text example](images/rich_text.png)

Nasti supports any markup that the `rich.print` function accepts, so check out [their docs](https://rich.readthedocs.io/en/latest/markup.html) for a full description of what's possible

## Silent Mode
Silent mode allows you to create a project from a template without having to use the interactive prompts. This makes silent mode suitable for integrating Nasti into other tools, such as GUI projects or template generation systems in things like Github.

To invoke silent mode you use the `-s` switch on the command line and specify a the names and values for the prompts you want to populate:

```bash
$ nasti process -s "app_name='My Great App',contact_name='Adam Drew',api_path='my-api',contact_email='adam@email.net'" ~/Development/some-template great_new_app
```

You must specify names and values for all of the mutations and globals in the template that don't have defaults. Silent mode will use defaults for all mutations except those that you specify on the command line. In the example above we can image that `app_name` and `contact_name` are globals, and so need to be specified, but `api_path` has a default but we're overriding it. In that way silent mode operates like accept defaults mode but with overrides. Also, you must specify an output directory when using silent mode.

## Development

### Dependency Management & Virtual Environment
This project uses [pipenv](https://github.com/pypa/pipenv) to manage dependencies and the virtual environment. You'll want to make sure you have pipenv installed. Then after you pull down the NASTI code run `pipenv install`. You can then enter the virtual environment and get to hacking with `pipenv shell`.

### Running from Source
If you are hacking on the app and you want to run the version you have in the source tree enter the venv with `pipenv shell` and then run the app directly:

```
$ python nasti.py [COMMANDS] [OPTIONS]
```

Even if you have NASTI installed as a command on your machine globally this should run the version in the source tree.

### Tests & Code Coverage
You can run tests with `make test` and generate a codecoverage report with `make coverage`. PRs are very, very much welcome but please make sure anything you introduce or refactor passes tests and includes new tests if required.

### Building & Publishing
I barely understand Python packaging publishing. Describing it as a complex mess would be an understatement. I think I have it working as simply as possible, but I had to do so much trial and error I don't know whether what seems to work on my machine will work on someone else's. Help very much welcome on this!

1. Exit the venv if you are in it
2. Bump the version in `setup.py`
2. (If you need to) Install build deps with `make install-build-deps`
3. Build `make build-app`
4. Publish `make publish`

## Project Justification
Do we really need another project template system? And if we do, do we really want one this weird?

A cookiecutter template contains a bunch of source files that have bits of text stripped out and replaced with jinja template syntax along with a JSON config file that contains the prompts, default values, and more. It is a great system and many projects use it. However, for some use cases it has a fatal flaw. Once the project has been converted to a template it is no longer valid source code. You can't run, debug, test, build, or develop on it without a complex and error prone process.

NASTI attempts to solve this problem by flipping the concept of a template on its head. The source files are left as is, to be worked with as normal and no specific directory structure is mandated. All NASTI requires is a file called `nasti.yaml`, in your project's root directory. The nastifile defines a set of mutations. Each mutation defines a text string to be replaced, a list of files that text string occurs in, and some extras like prompts and validations. NASTI clones or copies the nastified™️ project, applies the mutations, and the result is a brand new project ready to build on.

This may seem strange at first, but it really isn't any worse than a standard template system. Both approaches rest on text substitution. Putting curly braces around the text to be substituted doesn't make it any less of a text substitution system. It just breaks the project. NASTI's main difference is that we shift the work of defining what text should be replaced to the nastifile and away from the code itself. Additionally, the NASTI approach comes with benefits. The nastifile defines everything about your project's template config in one place. You don't have to search through files or wonder if there's some jinja syntax in some file you forgot about. And you don't have to worry about something getting substituted that you didn't expect, because all mutations are explicitely scoped. The nastifile also allows us to provide a robust validation system that ensures your project and nastifile are in sync. So, though the approach may seem a bit strange at first, but if you try NASTI out I think you'll agree that it makes your life as a developer simpler and more pleasent. And that's exactly what software should do above all else.

"That's not a template! That's NASTI!"



