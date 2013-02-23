title: "Git for the Cocoa Developer"
subtitle: "A Typical Workflow"
published: false
date: 2008-11-26
tags: [cocoa, git]
---

Lately I've been doing a bit of Cocoa development. To be perfectly honest, Between an [ABM](http://en.wikipedia.org/wiki/Agent-based_model) Simulation Framework I've been working on (I'll talk about this a bit more in a future post) and the [iPhone development class](http://www.stanford.edu/class/cs193p/cgi-bin/index.php) that I'm taking, I've actually been doing quite a lot of Cocoa development. Now, I like to use some type source control system when I develop software, even when I'm developing by myself. I also typically like to use a distributed source control system (the reasons for why are another blog post for another time when I'm feeling a bit more iconoclastic) such as Mercurial or Git. When I started developing my ABM framework I decided that I would give SVN a try since support for it was built into Xcode and typically if you try not to fight the tools, you find that development is quite a bit easier. Unfortunately, this time that didn't ring true. From the get-go I ran into troubles, and considering my disdain for SVN and all the other centralized repository systems, I decided to drop it and go with Git instead.

The rest of this post deals with everything I've learned along the way. Aside from being a repository for me of all the tasks I commonly do with Git, I'm hoping that this post will act as a quick start guide for anyone who's interested in using Git for their Cocoa development source control needs. So, enjoy the post, and if anyone runs into anything that's not properly explained or if there's a topic that you think is missing, leave a comment, and I'll do my best to update this post or create a new one if the topic is big enough to deserve one.

### Gittin' Git

To get started, the very first thing that you'll need to do is get Git installed on your system. I've found that, by far, the easiest way to do this is just to download the OS X installer from [Google Code][installer] and run through it, rather than trying to build it from source, which can be a slight pain to do so.

### My Typical Workflow

Whenever I setup a new Xcode project, the first thing I do is initialize it as a Git repository and add some configuration to the project that will make using Git with Xcode a bit less messy. I also typically create a remote repository, without a working set of code (i.e., a bare repository), that I use as a way of transferring my code between the different machines I use for development. Finally, I add some files to the newly created project, make the initial commit, and push the changes to the remote repository.

##### Create a new remote repository

    :::bash
    $ ssh url.to.remote.server.com
    $ mkdir -p /path/to/repo/myrepo.git
    $ cd /path/to/repo/myrepo.git
    $ git --bare init
    $ exit

##### Create a new local repository

    :::bash
    $ cd /path/to/new/project/MyProject
    $ git init
    $ git remote add origin \
      url.to.remote.server.com:path/to/repo.git

##### Config the repository for Cocoa development

The configuration that we will be specifying for our Git project will be contained in two hidden files: `.gitignore` and `.gitattributes`. The format for both of these files is very simple, its just a list of [globs][glob], representing a set of files with the second file (`.gitattributes`) also specifying how each file should be treated by Git with special attributes.

First, create a `.gitignore` file. This file is responsible for telling Git which files you feel it doesn't need to track. We'll be telling Git to ignore some Xcode and OS X noisiness, the build directory's contents, and anything related to SVN. Below is the contents of the `.gitignore` file that you will create and add to the root directory of your new Xcode project with whatever text editor you find yourself partial to.

    :::bash
    ####################
    # .gitignore
    ####################

    # xcode noise
    build/*
    *.mode1v3

    # SVN directories
    .svn

    # osx noise
    .DS_Store
    profile

Next, create a `.gitattributes` file to specify how we would like Git to treat specific files in our Xcode project.

    :::bash
    ######################
    # .gitattributes
    ######################

    *.pbxproj -crlf -diff -merge

In the example above, each of the globs describing a set of files is paired with a set of attributes that detail how the resultant files should be treated. With the first two attributes (i.e., `-crlf` `-diff`), we are telling Git to treat all Xcode project files with the `.pbxproj` as a binary and thus preventing Git from reporting differences in newlines or showing it in diffs. The last attribute, `-merge`, tells Git to exclude the project files from merges.

##### Add some files

    :::bash
    $ touch newfile
    $ git status
    $ git add .
    $ git commit -m "Initial check-in"

##### Push the changes to the origin (remote repository)

At this point in time we have just one branch, the master branch, so we'll be specifying it when we push our changes to the origin. In future posts, I'll show you how to create branches and add them to remote repository.

    :::bash
    $ git push origin master

##### Check out the project from another machine

Once we've pushed our initial changes to the master branch to the remote repository, we'll be able to access the project from any machine that has Git installed on it. To check out a fresh copy of the project from the remote repository, you'll run the following from the command line of the machine to which you want to check out the code.

    :::bash
    $ git clone \
      url.to.remote.server.com:path/to/repo.git

##### Update a local copy with the latest changes

Finally, if you've got a local copy of the repository on several different machines and you want to make sure that the one you're currently working on has the latest set of changes, you'll run the `pull` command with the repository and branch from which you want to pull the changes.

    :::bash
    $ git pull origin master

Well, that's pretty much everything that you'll need to get you started with Cocoa development using Git for your source control management needs. I hope you enjoyed the post and found it useful. Keep your eyes peeled to this weblog for future posts on using Git with Xcode for Cocoa development.

[installer]: http://code.google.com/p/git-osx-installer/ "Git OS X Installer"
[glob]: http://en.wikipedia.org/wiki/Globbing "Wikipedia: glob"
