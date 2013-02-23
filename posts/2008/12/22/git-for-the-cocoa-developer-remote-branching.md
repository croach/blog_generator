layout: post
title: "Git for the Cocoa Developer"
subtitle: "Remote Branching"
date: 2008-12-22
published: false
tags: [cocoa, git]
---

If you've been following the rest of this series, so far what you've learned is how to set up a Cocoa-specific project folder, how to host a bare repository for the project on a remote server, and how to set up your local project to deal with an alternate ssh port on the remote machine. In this episode, I'll go over the few commands that you'll need to branch your project and push those branches to your remote repository.

### Creating the Remote Branch

To create a remote branch what we'll do is create a new local branch and then push the new branch to the remote repository. Creating a new branch is easy, simply call the `git branch` command and pass into it the name you wish to associate with the new branch. Pushing the new branch to the remote repository is just as easy. Just call the `git push` command as we've done in earlier posts with the name of the remote repository (in our case that would be `origin`) and append to that the name of the local branch.

    :::bash
    % git branch <local_branch_name>
    % git push origin <local_branch_name>

Now that you've created a new branch, you'll probably want to begin working in it. To do that, you'll need to switch to the new branch. First, let's take a look at the branches that we have in our local project. To do so, execute `git branch` at the command line. What you'll see is a list of all the branches in the local repository with the currently checked out branch prefaced with an asterisk. To switch to the new branch, execute the following line:

    :::bash
    % git checkout <branch_name>

Now, if you run the `git branch` command again, you'll see the same list, but this time the new branch you created will marked as the currently checked out one.

### Properly Tracking the Remote Branch

Now, you could use the checkout command that was demonstrated in the section above, however, that command will simply checkout the branch, it won't set it up to track the remote branch. What that means is that you'll need to add the remote repository name and the remote branch name to each `push` and `pull` command that you issue while working in this branch. If you find that a bit annoying, and you really just want to call `push` and `pull` and have Git figure out the details of where everything is supposed to go, you're in luck. The Git checkout command offers an option to specify the remote branch that it is supposed to be tracking. So, instead of calling the checkout command with nothing more than our local branch's name, as we did in the previous section, what you'll want to do is specify the track branch option and give it the name of the remote branch you wish to track. The command will then look like the following:

    :::bash
    % git checkout --track -b <local_branch_name> \
        origin/<remote_branch_name>

Keep in mind that the line above is totally optional. If you choose not to set up your local branch to automatically track the correct branch remotely, you'll simply have to identify the branch that you are pushing and pulling to and from like so:

    :::bash
    % git push origin <remote_branch_name>
    % git pull origin <remote_branch_name>

If, however, you do decide to run the checkout command with the tracking option, as we did above, you'll simply be able to call the `push` and `pull` commands without specifying either the remote repository or the branch name and, as my algorithms professor was always so fond of saying, everything will just work itself out in the wash.
