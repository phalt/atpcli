# Contributing

First things first: thank you for contributing! This project will be successful thanks to everyone who contributes, and we're happy to have you.

## Bug or issue?

To raise a bug or issue please use [our GitHub](https://github.com/phalt/atpcli/issues).

Please check the issue has not been raised before by using the search feature.

When submitting an issue or bug, please make sure you provide thorough detail on:

1. The version of atpcli you are using
2. Any errors or outputs you see in your terminal
3. Steps to reproduce the issue

## Contribution

If you want to directly contribute you can do so in two ways:

1. Documentation
2. Code

### Documentation

Fixing grammar, spelling mistakes, or expanding the documentation to cover features that are not yet documented, are all valuable contributions.

### Code

Contribution by writing code for new features, or fixing bugs, is a great way to contribute to the project.

#### Set up

Clone the repo:

```sh
git clone git@github.com:phalt/atpcli.git
cd atpcli
```

Move to a feature branch:

```sh
git branch -B my-branch-name
```

Install UV (if not already installed):

```sh
# On macOS and Linux:
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or using pip:
pip install uv
```

Install all the dependencies:

```sh
make install
```

This will use UV to create a virtual environment and install all dependencies. UV handles the virtual environment automatically, so you don't need to manually activate it.

To make sure you have things set up correctly, please run the tests:

```sh
make test
```

### Preparing changes for review

Once you've made changes, here's a good checklist to run through before publishing for review:

Run tests:

```sh
make test
```

Format and lint the code:

```sh
make format
```

### Making a pull request

Please push your changes up to a feature branch and make a new [pull request](https://github.com/phalt/atpcli/compare) on GitHub.

Please add a description to the PR and some information about why the change is being made.

After a review, you might need to make more changes.

Once accepted, a core contributor will merge your changes!
