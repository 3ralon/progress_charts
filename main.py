from pathlib import Path
from github import Github, Milestone

WORKSPACE_ROOT = Path.cwd()
TOKEN_FILE = 'git.token'
ORGANISATION_NAME = 'Aparking'
REPOSITORY_NAME = 'AparKing_Backend'

def main():

    token_path = WORKSPACE_ROOT / TOKEN_FILE
    if token_path.exists():
        with open(token_path, 'r') as f:
            token = f.read()
    else:
        print("git.token file does not exist")

    github = Github(token)

    # Retrieve repository
    organisation = github.get_organization(ORGANISATION_NAME)   
    repository = organisation.get_repo(REPOSITORY_NAME)

    milestones = repository.get_milestones(state='all')
    issues = repository.get_issues(state='all', milestone=milestones[0])

    for issue in issues:
        print(issue.labels)

if __name__ == '__main__':
    import sys
    
    try:
        main()
    except KeyboardInterrupt:
        print('Exiting...')
        sys.exit(0)