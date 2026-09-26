# Contributing to frozendefaultdict

All contributions to this project are welcome, and they are greatly appreciated; every little bit helps.
The most common ways to contribute here are

1. opening an [issue](https://github.com/nelimee/frozendefaultdict/issues/new) to report a bug or propose a new feature, or ask a question, and
2. opening a [pull request](https://github.com/nelimee/frozendefaultdict/pulls) to fix a bug, or implement a desired feature.

The rest of this document describes the technical details of getting set up to develop, and make your first contribution to frozendefaultdict.


## Development environment

frozendefaultdict uses [uv](https://docs.astral.sh/uv/) for packaging and dependency management. It may also be used for managing the virtual environment. 

1. Ensure you have [`uv` installed](https://docs.astral.sh/uv/getting-started/installation/).
2. Clone the [`frozendefaultdict` repository](https://github.com/nelimee/frozendefaultdict). If you are unfamiliar with `git`, check out the [docs](https://git-scm.com/), and learn about what the typical [`git` workflow](https://www.asmeurer.com/git-workflow/) looks like.
3. Inside the `frozendefaultdict` directory (`cd frozendefaultdict`), use `uv sync` to create a virtual environment (`/.venv`) and synchronise dependencies.

```bash
pip install uv
git clone https://github.com/nelimee/frozendefaultdict.git
cd frozendefaultdict
uv sync
```

You should now have a development environment set up to work on frozendefaultdict! 🎉 To go forward with making the desired changes, please consult the ["Making changes" section](https://www.asmeurer.com/git-workflow/#making-changes) of the `git` workflow article. If you've encountered any problems thus far, please let us know by opening an issue! More information about workflow can be found below in the [lifecycle](#lifecycle) section.

> [!NOTE]
> Since `uv` uses a virtual environment, any commands to be run inside the virtual environment will need to be prefaced with `uv run` or the `uv` [managed virtual environment](https://docs.astral.sh/uv/pip/environments/#using-a-virtual-environment) will need to be activated by running `source .venv/bin/activate` in your shell. 

What follows are recommendations/requirements to keep in mind while contributing.

## Making changes

### Adding tests

When modifying and/or adding new code it is important to ensure the changes are covered by tests.
Test thoroughly, but not excessively.
`frozendefaultdict` tests are located in the directory named `tests` at the top level of the repository.

### Running tests

After making changes, ensure your changes pass all the existing tests (and any new tests you've added).
Use `uv run pytest` to run the tests.

### Style guidelines

`frozendefaultdict` code is developed according the best practices of Python development.
- Please get familiar with [PEP 8](https://peps.python.org/pep-0008/) (code) and [PEP 257](https://peps.python.org/pep-0257/) (docstrings) guidelines.
- Use annotations for type hints in the objects' signature.
- Write [google-style docstrings](https://google.github.io/styleguide/pyguide.html#383-functions-and-methods) without duplicating the type annotations from the code in the documentation.

We use [Ruff](https://docs.astral.sh/ruff/) to automatically lint the code and enforce style requirements as part of the CI pipeline.
You can run these style tests yourself locally in the top-level directory of the repository.

You can check for linting/formatting violations with
```bash
uv run ruff format --check
uv run ruff check
```

Many common issues can be fixed automatically using the following command, but some will require manual intervention to appease Ruff.

```bash
uv run ruff format
uv run ruff check --fix
```

We use both [Mypy](https://mypy.readthedocs.io/en/stable/) and [`ty`](https://docs.astral.sh/ty/) as a type checkers to find incompatible types compared to the type
hints in your code. To test this locally, run:

```bash
uv run mypy
uv run ty check
```

If you aren't presented with any errors, then that means your code is ready to commit!

## Code of conduct
frozendefaultdict development abides to the [](./CODE_OF_CONDUCT.md).

## Lifecycle

All releases for `frozendefaultdict` are tagged on the `main` branch with tags for the version number of the release.
Find all the previous releases [here](https://github.com/nelimee/frozendefaultdict/releases).

## AI use policy and guidelines

Go and read the [`AGENTS.md`](./AGENTS.md) file too (mostly targeted at LLMs, but have a look at it).

frozendefaultdict's policy is that contributors can use whatever tools they would like to craft their contributions, but **there must be a human in the loop**.
Contributors must read and review all LLM-generated code or text before they ask other project members to review it.
The contributor is always the author and is fully accountable for their contributions.
Contributors should be sufficiently confident that the contribution is high enough quality that asking for a review is a good use of scarce maintainer time, and they should be able to answer questions about their work during review.

Contributors can use any tools that aid in understanding the `frozendefaultdict` codebase and writing code, including AI tools, but are encouraged to read the documentation themselves and improve it if they find an issue.
However, as noted above, contributors always need to understand and explain the changes they're proposing to make, whether or not they used an LLM as part of your process to produce them.
The answer to "Why is X an improvement?" should never be "I'm not sure. The AI did it."

Contributors are expected to **be transparent and label any contribution that used AI tooling**, whether it produced a whole feature or a single function.
Our policy on labelling is intended to facilitate reviews, and not to track which parts of frozendefaultdict are generated.
Contributors should note tool usage in their pull request description, commit message, or wherever authorship is normally indicated for the work.
For instance, use a commit message trailer like `Assisted-by: `.
The pull request template includes an AI use section; please fill it in rather than leaving it blank.
This transparency helps the community develop best practices and understand the role of these new tools.

### Disclosing AI use

Say so whenever AI tooling contributed to a change, in both places authorship is recorded:

- **In the commit**, with a trailer such as `Assisted-by: <tool name>`.
- **In the pull request**, by ticking the appropriate box in the AI use section of the template. If the work was partially generated, give a rough estimate of how much of it you wrote yourself — a ballpark figure is fine, nobody is going to audit it.

### Particular warnings

**Please write issue and pull request descriptions by hand.**
This is a preference rather than a rule, but a strong one.
A description is the one place you explain *why* a change is worth making, what you considered and rejected, and where you are unsure — none of which a tool can infer from the diff.
Generated descriptions tend to restate what the diff already shows, which makes review slower rather than faster, and they hide exactly the uncertainty a reviewer most needs to see.

Maintainers have the right to close contributor PRs and ban contributors who do not abide by this policy after a warning.