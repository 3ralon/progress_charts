# Progress charts generator

This repository contains a script that generates progress charts to study the evolution of a project and evaluate team performance. The aim is to provide an automatic visual representation of burndown charts, velocity charts, and cumulative flow diagrams.

It is based on the GitHub issues of a repository, so it is necessary to have a GitHub account and a **personal access token** to use the script. The script uses the GitHub API to retrieve the issues and their metadata.

> **Note:** The script is still under development, and it is not ready for production. It is a personal project to learn how to use the GitHub API and generate progress charts.

## Installation

To install the script, you need to have Python 3.8 or higher. You can install the required dependencies by running:

```bash
pip install -r requirements.txt
```

## Dependencies

The script uses the following libraries:

- `matplotlib` to generate the charts
- `numpy` to handle the data
- `PyGithub` to interact with the GitHub API
- `sys` to handle the command-line exceptions

## References

- [GitHub API](https://docs.github.com/en/rest)
- [alessioarcara - burndown_chart](https://github.com/alessioarcara/burndown_chart)
