# Contributing

Thank you so much for your interest in contributing to `commensurability`!

## Reporting Issues

Please report bugs & other problems by opening an [issue](https://github.com/ilikecubesnstuff/commensurability/issues) on GitHub.

You may want to check the existing issues for [`commensurability`](https://github.com/ilikecubesnstuff/commensurability/issues?q=is%3Aissue) and [`pidgey`](https://github.com/ilikecubesnstuff/pidgey/issues?q=is%3Aissue) in case your specific report has already been made.

## Contributing Code

Please fork the repository and create a [pull request](https://github.com/ilikecubesnstuff/commensurability/pulls) to contribute code.

### Contributing a New Commensurability Evaluation Method

New commensurability evaluation methods should be contained in a subpackage of commensurability, like `tessellation`.
This package should provide an `Evaluation` instance for analysis classes to use.
The corresponding analysis classes can be defined in `analysis.py`.
