[![Build Status](https://github.com/adamrdrew/nasti/actions/workflows/tests.yml/badge.svg?branch=master)](https://github.com/adamrdrew/nasti/actions)
[![codecov](https://codecov.io/gh/adamrdrew/nasti/branch/master/graphs/badge.svg?branch=master)](https://codecov.io/github/adamrdrew/nasti?branch=master)

# NASTI
NASTI is A Strange Templating Implementation.


NASTI allows you to create project templates, similar to tools like [Cookiecutter](https://github.com/cookiecutter/cookiecutter). What makes NASTI unique is that your project templates remain as valid, living code. You can run, test, and debug your project templates just like any other application while still enabling end users to bootstrap new projects from your template.

## Features
* Templates remain valid source code you can run, build, etc
* No opinionated project or directory structure
* Works with any language
* Tightly scoped single-file template definition
* Powerful template and project validation system
* Super easy, barely an inconvenience

## Usage

```sh
# Process a template on github
$ nasti process git@github.com:somedev/some-template.git
# Or gitlab, or any other git repo you can clone
$ nasti process git@gitlab.mycomand.com:someorg/some-template.git
# Process a local template
$ nasti process ~/Development/some-template
# Let NASTI greate your new project's repo
$ nasti process --git ~/Development/some-template
```

## Template Creation
All you need to get started is a project you that want to be available as a template. It can be in any language, with any project layout. 

Simply add a nastifile called `nasti.yaml` to the root of your project and add some mutations:

```yaml
---
mutations:
    # Name is an ID used internally and will appear in error messages
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
Nastifile is valid
```

If there's something wrong with your nastifile, such as a mutation being applied to a file that doesn't contain the replacement text, or an omitted field, `validate` will tell you:

```bash
$ nasti validate
Error: mutation email file: main.go at: /home/adamdrew/Development/someapp/main.go does not contain somedev@corpo.net 

$ nasti validate 
Error: Invalid mutation config: {'name': 'quay', 'help': 'The quay repo is the location of your container image. Should be in the form of quay.io/username/repo', 'replace': 'quay.io/someorg/some-project', 'files': ['Makefile'], 'validations': ['^quay\\.io/[a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+$']} missing 'prompt'
```

You can easily build out your nastifile by adding or updating mutations, validating, and fixing what doesn't work. It also makes a good fit for an automated PR check in your repo.

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

## Project Justification
Do we really need another project template system? And if we do, do we really want one this weird?

A cookiecutter template contains a bunch of source files that have bits of text stripped out and replaced with jinja template syntax along with a JSON config file that contains the prompts, default values, and more. It is a great system and many projects use it. However, for some use cases it has a fatal flaw. Once the project has been converted to a template it is no longer valid source code. You can't run, debug, test, build, or develop on it without a complex and error prone process.

NASTI attempts to solve this problem by flipping the concept of a template on its head. The source files are left as is, to be worked with as normal and no specific directory structure is mandated. All NASTI requires is a file called `nasti.yaml`, in your project's root directory. The nastifile defines a set of mutations. Each mutation defines a text string to be replaced, a list of files that text string occurs in, and some extras like prompts and validations. NASTI clones or copies the nastified™️ project, applies the mutations, and the result is a brand new project ready to build on.

This may seem strange at first, but it really isn't any worse than a standard template system. Both approaches rest on text substitution. Putting curly braces around the text to be substituted doesn't make it any less of a text substitution system. It just breaks the project. NASTI's main difference is that we shift the work of defining what text should be replaced to the nastifile and away from the code itself. Additionally, the NASTI approach comes with benefits. The nastifile defines everything about your project's template config in one place. You don't have to search through files or wonder if there's some jinja syntax in some file you forgot about. And you don't have to worry about something getting substituted that you didn't expect, because all mutations are explicitely scoped. The nastifile also allows us to provide a robust validation system that ensures your project and nastifile are in sync. So, though the approach may seem a bit strange at first, but if you try NASTI out I think you'll agree that it makes your life as a developer simpler and more pleasent. And that's exactly what software should do above all else.

"That's not a template! That's NASTI!"



