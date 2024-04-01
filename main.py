from pathlib import Path

from github import Github
from github.Issue import Issue
from github.PaginatedList import PaginatedList

from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd


WORKSPACE_ROOT = Path.cwd()
TOKEN_FILE = "git.token"
ORGANISATION_NAME = "Aparking"
REPOSITORY_NAME = "AparKing_Backend"
MILESTONE = 1


def create_burndown_chart(
    issues,
    start_date,
    end_date,
    start_date_dt,
    end_date_dt,
    chart_name="Burndown Chart",
):

    dates = pd.date_range(start=start_date, end=end_date, freq="D").to_list()
    dates = list(map(lambda x: x.date(), dates))
    total_issues = len(issues)
    ideal_progress = np.linspace(total_issues, 0, len(dates))
    real_progress = [total_issues]

    closed_dates = []
    for issue in issues:
        if (
            issue.closed_at
            and start_date_dt.date() <= issue.closed_at.date() <= end_date_dt.date()
        ):
            closed_dates.append(issue.closed_at.date())

    closed_dates.sort()
    closed_idx = 0
    for date in dates[1:]:
        while closed_idx < len(closed_dates) and closed_dates[closed_idx] <= date:
            total_issues -= 1
            closed_idx += 1
        real_progress.append(total_issues)

    plt.figure(figsize=(10, 8))
    plt.plot(dates, ideal_progress, label="Ideal Progress")
    plt.step(dates, real_progress, where="mid", label="Real Progress")
    plt.title(chart_name.capitalize())
    plt.xlabel("Date")
    plt.ylabel("Number of Issues")
    plt.legend()
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%m-%d"))
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.savefig(f"{chart_name.replace(' ','_')}.png")


def create_burnup_chart(
    issues, start_date, end_date, start_date_dt, end_date_dt, chart_name="Burnup Chart"
):
    dates = pd.date_range(start=start_date, end=end_date, freq="D").to_list()
    dates = list(map(lambda x: x.date(), dates))
    closed_dates = []
    for issue in issues:
        if (
            issue.closed_at
            and start_date_dt.date() <= issue.closed_at.date() <= end_date_dt.date()
        ):
            closed_dates.append(issue.closed_at.date())
    closed_counts = [closed_dates.count(date) for date in dates]

    plt.figure(figsize=(10, 8))
    plt.bar(dates, closed_counts, label="Closed Issues")
    plt.title("Burnup Chart")
    plt.xlabel("Date")
    plt.ylabel("Number of Issues Closed")
    plt.legend()
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%m-%d"))
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.savefig(f"{chart_name.replace(' ','_')}.png")


def create_chart(
    issues: PaginatedList[Issue],
    start_date: str | datetime,
    end_date: str | datetime,
    chart_name="chart",
    chart_type="burndown",
) -> str:

    if not isinstance(start_date, datetime):
        start_date_dt = datetime.strptime(start_date, "%Y-%m-%d").astimezone()
    else:
        start_date_dt = start_date.astimezone()
        start_date = start_date_dt.strftime("%Y-%m-%d")

    if not isinstance(end_date, datetime):
        end_date_dt = datetime.strptime(end_date, "%Y-%m-%d").astimezone()
    else:
        end_date_dt = end_date.astimezone()
        end_date = end_date_dt.strftime("%Y-%m-%d")

    if chart_type == "burndown":
        create_burndown_chart(
            issues,
            start_date,
            end_date,
            start_date_dt,
            end_date_dt,
            chart_name=chart_name,
        )
    elif chart_type == "burnup":
        create_burnup_chart(
            issues,
            start_date,
            end_date,
            start_date_dt,
            end_date_dt,
            chart_name=chart_name,
        )
    else:
        raise ValueError(
            f"Unknown chart type: {chart_type}. Supported types are 'burndown' and 'burnup'"
        )

    return WORKSPACE_ROOT / f"{chart_name}.png"


def write_report(report: dict):
    with open("report.md", "w") as f:
        f.write(f"# Progress Report For {report['repository']}\n\n")
        f.write(f"## Team Information\n\n")
        f.write(f"- Organisation: {report['organisation']}\n\n")
        f.write(f"- Colaborators:\n")
        for colaborator in report["colaborators"]:
            f.write(f"  - {colaborator.login}\n")
        f.write(f"\n## Report Information\n\n")
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
    report["general_chart"] = create_chart(
        issues,
        chart_name="general_chart",
        start_date=milestone.created_at,
        end_date="2024-04-01",
    )
    report["week_chart"] = create_chart(
        issues,
        chart_name="week_chart",
        start_date="2024-03-12",
        end_date="2024-03-21",
    )
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
