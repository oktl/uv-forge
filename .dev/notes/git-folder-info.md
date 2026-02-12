# Git folder info

Since you are new to Git, looking inside the `.git` folder can feel like looking under the hood of a complex engine. These folders and files make up your project's "database," which Git uses to track every change you make.

Here is a breakdown of the folders you see in your project's local `.git` directory:

## 1. `objects`

This is the most important folder—it is the heart of the Git database.

* **Purpose**: It stores all the actual content of your files and your commit history.
* **What's inside**: Git doesn't store files by name; it hashes the content into a 40-character ID. You will see many two-character subfolders (like `0a/`, `f2/`).
* **Key File Types**:
* **Blobs**: Compressed versions of your project files.
* **Trees**: Represent your folder structure at a specific point in time.
* **Commits**: Store the snapshot metadata (who, when, and the commit message).

## 2. `refs` (References)

* **Purpose**: This folder acts as a map of "bookmarks" to specific points in your history.
* **What's inside**:
* **`heads/`**: Contains files named after your branches (like `main`). Inside the `main` file is simply the ID of the latest commit on that branch.
* **`remotes/`**: Stores where your "hub" (the `origin` you set up in `git-repos`) currently stands.
* **`tags/`**: Stores any specific versions you’ve marked (like `v1.0`).

## 3. `hooks`

* **Purpose**: These are scripts that Git can trigger automatically when certain actions happen.
* **What's inside**: You will see many `.sample` files (like `pre-commit.sample`).
* **Usage**: If you rename a sample to remove the `.sample` extension and write code inside, you can make Git do things like "automatically run my Python tests before I am allowed to commit."

## 4. `logs`

* **Purpose**: This folder keeps a history of where your branches have been over time.
* **What's inside**: It contains a "reflog" (Reference Log).
* **Usage**: If you ever accidentally delete a branch or "lose" a commit, the logs folder is where you go to find the history of the branch's movements so you can recover your work.

## 5. `info`

* **Purpose**: This contains global-style configuration for the specific repository that you don't want to share with others.
* **Key File**: `exclude`.
* **Usage**: It works exactly like your `.gitignore` file, but because it is inside the `.git` folder, it stays private to your local machine even if you eventually shared the project with others.

## Important Files in the Root

* **`HEAD`**: A very important file that tells Git which branch you are currently working on. It usually just says `ref: refs/heads/main`.
* **`config`**: This is where your local settings live, including the link to your "hub" folder in `~/Projects/git-repos`.
* **`description`**: This is a legacy file used by GitWeb; for your local Python projects, you can safely ignore it.

**Note**: You generally never need to edit these files manually. Your `git_handler.py` script and the VS Code UI handle all the interaction with these folders for you by running standard Git commands.
