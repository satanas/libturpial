How to write code
=================

If you are a developer and want to collaborate with code for features, fixes or improvements you are in the right place. Follow this single steps that define our coding flow and show us your code! (you will need git to interact with us).

  - Clone or fork turpial or libturpial repo::
    
    $ git clone git://github.com/Turpial/libturpial.git your_folder

  - Be sure that you are on development branch::

    $ git checkout development

  - Create a local branch with a descriptive name of the feature/fix/improvement that you are going to work::

    $ git branch my_awesome_fix

  - Code, code, code
  - When you are ready, sync with development branch of libturpial using::

    $ git pull origin development

  - Resolve all possible conflicts when merging (please be aware of not remove or break current code)
  - Make a pull request in github from your branch to development branch of libturpial
  - Wait until one of the trusted developers merge your changes into main repo and pay attention to any question they ask you
  - If everything went fine, enjoy your fame XD

If you are new to github
------------------------

In the case this is the first time you are going to use github for development, here are some links for you: 

      * https://help.github.com/articles/set-up-git
      * https://help.github.com/articles/create-a-repo
      * https://help.github.com/articles/fork-a-repo
      * https://help.github.com/articles/be-social

Remember
--------

  * If your changes can't be automatically merged from github interface we **WON'T apply them**
  * **DO NOT delete your branch** until we have merged, otherwise you will lost your changes and we won't merge into main repo