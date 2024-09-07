import git
from git.exc import GitCommandError

def commit_and_push_to_git(log_file):
    try:
        repo = git.Repo(".")  # Open the current repository
        repo.git.add(log_file)  # Stage the updated log file

        # Commit the changes
        repo.index.commit("Update search_log.xlsx with new search term")

        # Push the changes to the repository
        origin = repo.remote(name='origin')
        origin.push()
        
        print("Successfully committed and pushed changes.")

    except GitCommandError as e:
        print(f"An error occurred during Git operations: {e}")
