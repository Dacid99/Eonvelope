# Contributing Guidelines

If you have an idea for the project you are very welcome to implement it yourself!

To make it easier to read and understand your merge requests please follow these guidelines as closely as possible.

- The repositories code style follows the conventions as defined in [PEP8](https://peps.python.org/pep-0008) and enforced by black formatter.

- The variable names should be comprehensive and the code self-explanatory. Use comments only where required for structure, comprehension or warning.

- Avoid suppressing warnings (e.g. by pylint and ruff) by annotations, this only hides potential issues. If such a warning is raised either fix it or explain why you can't in a comment. Only if the correct way to do something raises a warning a suppression should be used. Every suppression needs a comment why it is inevitable.

- The projects default branch is 'development'. Please direct all merge requests to it. There are no changes other than ci config on the master branch. Development is merged into master for new releases.

- Commits should have a clear and descriptive commit message in a standardized format, please refer to [this article which describes the format used for this project](https://www.seyhan.me/blog/post/lost-art-of-commit-messages).

- Every single commit should be able to run, so the changes made in it must be complete. If not that has to be indicated in the commit message.
  The completing commit then mentions the commit it completes.

- Every commit should be as concise and small as possible within the bounds of the rule above. Every commit should be its own logical and consistent unit of change.

- Please do not change and commit the project configuration and test files unless you need to add a new dependency or it is inevitable for your change to work.

- If you change or add strings marked for translation, please do not run `python manage.py makemessages` and change the translation files in the merge request. Changes to these files need to be synchronized with weblate, that will be done after the branches are merged.

- Your merge request should already have been properly tested by yourself.

- Every merge request will be linted and checked using the tools in the validation folder. Please make sure to do this yourself as well.

Thank you for helping with the project!
