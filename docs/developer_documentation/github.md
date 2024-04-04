!!! warning

    This documentation is currently under construction and may not be up to date.

Getting up to speed with git
Clone working copy
General
Clone the CDDS project
Using SSH Key
Generate SSH key for Github using Seahorse:
Add your SSH key to Github
Clone working copy of cdds-testing-project
View status of your working copy
Get latest changes
Switching between branches
Create a new branch
Commit and Push Changes:
Commit Changes
Push Changes
Commit Messages
Template
Rules
Examples
Simple log message example:
Log message with body example:
Viewing history of commits
Seeing all full commit messages decreasing history
Seeing first line of the commit messages decreasing history
Viewing branches
Seeing the information on the branch you are on:
List all child branches
Reset changes
Reset all local changes
Reset changes of a specific file
Reset changes of last n commits:
Reset to the last commit:
Reset to the previous last commit:
Revert changes
Undo changes of a specific commit:
Stash changes
Stashing your work
Re-applying your stashed changes
Delete Branches
Getting up to speed with git
The develop branch is called main. When you start working on the project, first of all you need to get a working copy on your developer environment:

Clone working copy
General


 git clone <repository-url>
For the cdds-inline-testing project, we use ssh. You can import the ssh key into seahorse. That prevents you to type in your git credentials each time when you use a git command.

Therefore, you need to use the SSH repository URL:



git clone git@github.com:<permission-group>/<repository-name>.git
Clone the CDDS project
For the CDDS project, we use ssh. You can import the ssh key into seahorse. That prevents you to type in your git credentials each time when you use a git command.

Using SSH Key
Generate a SSH key for Github or use an already existing key. You can do it via seahorse or on the command line.

Generate SSH key for Github using Seahorse:
Start seahorse

Click on File in the menu and choose New

A creation window should pop up. In that, choose Secure Shell Key. Then click on continue

Now, you need to add a description of your key, for example “Github”.

Click on Just Create Key

It will ask you for a password. You can also use an empty password but it is highly recommended to use one. Click at OK.

You need to confirm your chosen password again.

After confirmation, the key will be created. You should see the key in the Open SSH keys tab.

Now, open a terminal. You can find the public key that you need for Github in your home folder:



cd ~/.ssh
Your new created public key is id_rsa.<number>.pub file, where <number> is the highest number of the id_rsa files. To get the key phrase that is needed for Github, simply open the public key file with an editor of your choice, for example with vi:



vi id_rsa.<number>.pub
The file content should start with ssh-rsa.

Add your SSH key to Github
Login to Github and go to your account settings

Go to the SSH and GPG keys tab

Click on the green Add SSH key button

Copy your public key phrase of your SSH key into the text box

Click Add SSH key

A confirm password box should be shown. Enter your Github password (not the SSH key password!) and then the key is added. You will get a email confirming that a new key has been added to your Github account.

Clone working copy of cdds-testing-project
Use following command to clone the cdds-testing-project:



git clone git@github.com:MetOffice/CDDS.git
View status of your working copy


git status
This command shows you the status of your working copy:

On which branch you are

What files are not committed but modified, added or removed

If files have any conflicts during a merge, switch, etc.

Get latest changes
You need to pull the latest changes from upstream by hand. Therefor, use following command:



git pull
This gets the latest changes from the remote repository for the branch you are currently in.

Switching between branches


git checkout <branch_name>
Make sure that you stash or commit any uncommited local changes first otherwise it could be that you get some awful conflicts.

Create a new branch
Each ticket should be developed in a new “feature“ branch. Also, bug releases etc. should have their own branches.

Switch to the branch you want to branch of. This branch is called parent branch:



git checkout <parent_branch_name>
 

Then, pull the changes from upstream. Your parent branch needs to be up to date:



git pull
 

Create the branch on your local machine and switch in this branch:



git checkout -b <name_of_the_new_branch>
 

Push the branch on github:



git push origin <name_of_the_new_branch>
 

You can check if your branch is created remotely:



git branch -a
This command should list your new created branch.

Commit and Push Changes:
After you did some changes you first need to commit them to your local repository afterwards you must push them to the remote repository.

Commit Changes
If you want to commit your changes locally, run:



git commit
It opens a vim or gvim, where you can specify your commit message. For the requirements of the commit messages see “Commit Messages“ section.

If you want to have one commit for each ticket then use for the first commit git commit and for all following commits git comment --amend.

Push Changes
Before pushing any changes you first need to commit them locally!

If you want to push your changes, you must tell git on which branch to push them:



git push
To be absolutely sure, that you push on the right branch, you can add the branch name to the git command:



git push origin <name_of_the_branch>
Commit Messages
Template


<ticket-number>: <short ticket description not longer than 72 characters>
<some additional description wrap after 72 charachters>
Rules
Git does not wrap commit messages automatically. That makes it hard to see the whole message in a terminal.

So following rules will apply for commit messages:

The first line of the commit starts with the ticket number, after that there will be a colon and followed by a short description what the ticket is for:

The message should not be longer than 72 characters!

Do not wrap this first line

If you need more descriptions:

Leave one line empty after the first main message

Write more descriptions.

For better reading try not to write more than 72 characters per line

Here, you can wrap the lines

Try to be short and precise

Examples
Simple log message example:


178: Use critical log level instead error in cdds_store
Log message with body example:


178: Use critical log leve instead error in cdds_store
* Change general log level to critical
* Print stack trace for critial logging
Viewing history of commits
Seeing all full commit messages decreasing history


git log
Seeing first line of the commit messages decreasing history


git log --oneline
Viewing branches
Seeing the information on the branch you are on:


git branch
List all child branches


git branch --list
Reset changes
Reset all local changes


git reset --hard
This discard all local changes to all files permanently.

Reset changes of a specific file


git reset --hard HEAD <file>
HEAD is your current branch.

Reset changes of last n commits:


git reset --hard HEAD~<number-of-changes>
The HEAD is your current branch.

Reset to the last commit:


git reset --hard HEAD~1
Reset to the previous last commit:


git reset --hard HEAD~2
Revert changes
Undo changes of a specific commit:
Find the commit number:



git log --online
The commit number is the number before each commit message

Revert changes to the commit number:



git revert <commit-number>
The git revert will undo the given commit but will create a new commit without deleting the older one. The git revert command will not touch the commits in your history, even the reverted ones.

Stash changes
You can temporarily stashes changes you have made to your working copy. You can work on something else and come back late and re-apply them. It helps you when you need to quickly switch context and work on something else on your local working copy. You can switches between branches your stashed changes will be still available.

Stashing your work


git stash
That stashes your local (uncommited) changes, save them for later use and revert them from your working copy.

Re-applying your stashed changes


git stash pop
This removes the changes from your stash and re-applies them to your working copy.

If you do not want that you changes will be removed from the stash use:



git stash apply
The stash apply command is really helpful if you need to apply the changes on multiple branches.

Delete Branches
This should be only a well-considered option. You can delete a branch locally or remotely:

Delete the branch locally:



git branch -D <name_of_branch_to_delete>
This deletion command force to delete the branch even if it is un-merged.

 

Delete the branch on github:



git push origin --delete <name_of_branch_to_delete>