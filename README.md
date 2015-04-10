git-submodule-describe
======================

Prerequisit: `git` and `git submodule` knowledge

Problem
-------

Imagine a repository with some submodules. How do you reproduce the
state the main repo and the submodules were in without
commiting and tagging it?

In my case the development in some submodules is very active, but not
so much in the main repo. The whole project is compiled many times using
different branches on the submodules. – Every such build should be
reproduceable but commiting and tagging would produce a huge amount
of tags (and commits) no-one really cares about most of the time.

Including a version string a la `git describe` with the sha1 commit
hashes of all submodules would quickly produce a very long and
unappealing string. The more submodules, the uglier it gets.

git submodule describe
----------------------

Git-submodule-describe produces an especially short ASCII string
describing the commits involved and tries to produce a string that even
looks nice.
