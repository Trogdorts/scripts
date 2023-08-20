import os
import shutil
import requests
import argparse
import tempfile
import subprocess

def get_pat_from_file(file_path):
    """
    Reads and returns the GitHub Personal Access Token (PAT) from the specified file.

    Args:
        file_path (str): Path to the file containing the GitHub Personal Access Token.

    Returns:
        str: The GitHub Personal Access Token read from the file.
    """
    with open(file_path, 'r') as file:
        return file.read().strip()

def get_repositories(username, pat):
    """
    Fetches both public and private repositories of a GitHub user using their username and PAT.

    Args:
        username (str): The GitHub username for which repositories are to be fetched.
        pat (str): GitHub Personal Access Token for authentication.

    Returns:
        list: A list of dictionaries representing the user's repositories.
    """
    public_response = requests.get(f'https://api.github.com/users/{username}/repos',
                                   headers={"Authorization": f"token {pat}"})
    public_repositories = public_response.json()

    private_response = requests.get(f'https://api.github.com/user/repos',
                                    headers={"Authorization": f"token {pat}"})
    private_repositories = private_response.json()

    all_repositories = public_repositories + private_repositories
    return all_repositories

def clone_repositories(username, pat, output_dir, zip_repos=True):
    """
    Clones the GitHub repositories of a user into the specified output directory.

    Args:
        username (str): The GitHub username whose repositories are to be cloned.
        pat (str): GitHub Personal Access Token for authentication.
        output_dir (str): Directory where the cloned repositories will be saved.
        zip_repos (bool): Flag indicating whether to zip the cloned repositories.

    Returns:
        None
    """
    repositories = get_repositories(username, pat)

    if not output_dir:
        output_dir = f'{username}_repositories'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    git_executable = r"C:\Program Files\Git\bin\git.exe"

    for repo in repositories:
        repo_name = repo['name']
        repo_url = repo['clone_url']
        repo_dir = os.path.join(output_dir, repo_name)

        if zip_repos:
            # Create a temporary directory for cloning
            with tempfile.TemporaryDirectory() as temp_dir:
                clone_command = [
                    git_executable, "-c",
                    "core.sshCommand=ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no", "clone",
                    repo_url, temp_dir]
                subprocess.run(clone_command, shell=True)

                # Zip the cloned repository to the main output directory
                repo_zip_name = f'{repo_name}.zip'
                shutil.make_archive(os.path.join(output_dir, repo_name), 'zip', temp_dir)
        else:
            # Clone directly to the output directory
            clone_command = [
                git_executable, "-c",
                "core.sshCommand=ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no", "clone",
                repo_url, repo_dir]
            subprocess.run(clone_command, shell=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clone all of your GitHub repositories.")
    parser.add_argument("username", help="GitHub username")
    parser.add_argument("-p", "--pat-file", required=True, help="File containing GitHub Personal Access Token")
    parser.add_argument("-o", "--output-dir", help="Output directory for cloned repositories")
    parser.add_argument("--no-zip", dest="zip_repos", action="store_false", help="Do not zip repositories")
    args = parser.parse_args()

    pat = get_pat_from_file(args.pat_file)

    clone_repositories(args.username, pat, args.output_dir, args.zip_repos)
