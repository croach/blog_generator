layout: post
title: "Git for the Cocoa Developer"
subtitle: "Remote Setup"
date: 2008-12-15
published: true
tags: [cocoa, git]

If your remote repository exists on a server whose `ssh` server is relegated to something other than the typical port, you might find it hard to connect to your repository with Git. Git offers---as far as I can tell---no command line option to change the default port number to one of your own choosing. So, in order to get your work done, you'll have to add a new host configuration to your user-scoped `ssh` config file. The rest of this post deals with creating a new host configuration and setting up your Git repositories to use the new configuration when connecting to a remote repository.

To add a new host configuration to ssh, you'll need to open the config file which can be found at `~/.ssh/config`, or, if one doesn't currently exist at that location, you can just create a new config file. After you've opened---or created, if necessary---the config file, you'll need to add a new configuration just like the one I've listed below.

    :::aconf
    Host mygitrepo
    Hostname christopherroach.com
    Port 2222
    User remote_username

Each new host configuration in your `ssh` config file must contain a `Host` key, value pair. This will take the place of the hostname that you usually pass into the `ssh` command when opening a new connection to a remote server. Next, is the `Hostname` key, value pair in which you will designate the url of your remote repository. The `Port` option is, obviously, the port on which the remote `ssh` daemon is listening. Finally, and this one is completely optional, you can add the `User` key, value pair which allows you to designate the user name that you use to log into the remote machine through ssh. If you do not include this option, you'll be prompted to enter your user name along with your password when doing anything over ssh to the designated remote machine. 

When all is said and done, the following command:

    :::bash
    % ssh mygitrepo

will be equivalent to:

    :::bash
    % ssh -p 2222 christopherroach.com

My suggestion is that you add the host configuration to your `.ssh/config` file and try it out with the `ssh` command above to make sure it works before trying out a git operation with the new setup---it's always a good idea to debug one application at a time. After you've proven that you entered everything correctly with the `ssh` command, it's time to set up your git repo to use the new host configuration. To do so, just `cd` into your local project directory and add the remote repo with the following command:

    :::bash
    % git remote add origin mygitrepo:path/to/git/repo.git

After doing that, you should be able to push and pull to and from the new repo with the following lines (assuming that `master` is the branch you wish to work with):

    :::bash
    % git push origin master
    % git pull origin master

That should be all you need to do to use Git with a remote repository whose `ssh` server listens on a port other than the default port 22.

__UPDATE:__ In the comments below, Eric points out yet another great way to get your local repository working with a remote server whose ssh daemon runs on a non-traditional port. Rather than adding a new host configuration to your `ssh` config file, you can setup each project to work with the remote repo with the following command, issued from within the local git repo, instead:

    :::bash
    % git remote add origin ssh://user@host:PORT/path/to/repo.git

The one difference that I noticed with this method, as opposed to the one that I've described, is that the path to the remote repository in the `git remote add` command had to an absolute path. When I used the host configuration method I detail above, I was able to use a path relative to my home directory on the remote machine (something to keep in mind if you try Eric's method and run into trouble). Anyway, that solution is excellent. Thanks Eric, I really appreciate the comment.
