from pathlib import Path
from github import Github
from github.Issue import Issue
from github.PaginatedList import PaginatedList
import numpy as np


WORKSPACE_ROOT = Path.cwd()
TOKEN_FILE = "git.token"
ORGANISATION_NAME = "Aparking"
REPOSITORY_NAME = "AparKing_Backend"
MILESTONE = 1


def calculate_statistics(issues: PaginatedList[Issue]) -> dict:
    opened_issues = []
    closed_issues = []
    for issue in issues:
        if issue.closed_at is not None:
            closed_issues.append(issue)
        else:
            opened_issues.append(issue)

    opened_issues.sort(key=lambda x: x.number, reverse=False)
    closed_issues.sort(key=lambda x: x.closed_at, reverse=False)

    statistics = {
        "opened_issues": opened_issues,
        "closed_issues": closed_issues,
        "total_issues": issues.totalCount,
    }

    return statistics


def create_chart(
    issues: PaginatedList[Issue], chart_name="chart.png", chart_type="burndown"
) -> str:

    if chart_type == "burndown":
        pass
    elif chart_type == "burnup":
        pass
    else:
        raise ValueError(
            f"Unknown chart type: {chart_type}. Supported types are 'burndown' and 'burnup'"
        )

    return WORKSPACE_ROOT / chart_name


def write_report(report: dict):
    with open("report.md", "w") as f:
        f.write(f"# Progress Report For {report['repository']}\n\n")
        f.write(f"## Team Information\n\n")
        f.write(f"- Organisation: {report['organisation']}\n\n")
        f.write(f"## Report Information\n\n")
        f.write(f"- Sprint: {report['milestone']}\n")
        f.write(f"- Total issues: {report['total_issues_n']}\n")
        f.write(
            f"- Opened issues: {report['opened_issues_n']} ({round((report['opened_issues_n']/report['total_issues_n'])*100, 1)}%)\n"
        )
        f.write(
            f"- Closed issues: {report['closed_issues_n']} ({round((report['closed_issues_n']/report['total_issues_n'])*100, 1)}%)\n\n"
        )
        f.write("## Progress Chart\n\n")
        f.write("### General\n\n")
        f.write(f"![General Progress Chart]({report['general_chart']})\n\n")
        f.write("### Last week\n\n")
        f.write(f"![Week Progress Chart]({report['week_chart']})\n\n")
        f.write(f"## Issues\n\n")
        f.write("### Opened issues:\n\n")
        for issue in report["opened_issues"]:
            f.write(f"- [{issue.number} - {issue.title}]({issue.html_url})\n")
        f.write("\n### Closed issues:\n\n")
        for issue in report["closed_issues"]:
            f.write(f"- [{issue.number} - {issue.title}]({issue.html_url})\n")


def main():
    token_path = WORKSPACE_ROOT / TOKEN_FILE
    if token_path.exists():
        with open(token_path, "r") as f:
            token = f.read()
    else:
        print("git.token file does not exist")

    github = Github(token)

    # Retrieve repository
    organisation = github.get_organization(ORGANISATION_NAME)
    colaborators = organisation.get_members()
    repository = organisation.get_repo(REPOSITORY_NAME)
    milestones = repository.get_milestones(state="all")
    if MILESTONE > milestones.totalCount:
        raise ValueError(f"Sprint {MILESTONE} does not exist")

    milestone = milestones[MILESTONE - 1]
    issues = repository.get_issues(state="all", milestone=milestone)
    issues = list(filter(lambda i: i.pull_request is None, issues))

    # Calculating statistics
    report = {}
    report["total_issues_n"] = len(issues)
    report["opened_issues"] = sorted(
        filter(lambda i: not i.closed_at, issues), key=lambda x: x.number
    )
    report["closed_issues"] = sorted(
        filter(lambda i: i.closed_at, issues), key=lambda x: x.number
    )
    report["opened_issues_n"] = len(report["opened_issues"])
    report["closed_issues_n"] = len(report["closed_issues"])
    report["general_chart"] = ""
    report["week_chart"] = ""
    report["organisation"] = ORGANISATION_NAME
    report["colaborators"] = colaborators
    report["repository"] = REPOSITORY_NAME
    report["milestone"] = MILESTONE

    write_report(report)


if __name__ == "__main__":
    import sys

    try:
        main()
    except KeyboardInterrupt:
        print("Exiting...")
        sys.exit(0)
    except Exception as e:
        print(f"{e.with_traceback()}")
        sys.exit(1)
