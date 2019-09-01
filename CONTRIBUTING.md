# Contributing Guidelines

*This list may be updated periodically based on how shitty your code is or how bad my OCD
is.*

## Python Guidelines 

- **Use line breaks.** If you have a long line of code, such as a complicated list
    comprehension, use multiple lines. In general, lines of code in python should
    not be longer than 85-90 characters. If horizontal scrollbars show up in your
    editor in a dual view, then the lines are probably too long.

- **Group code meaningfully.** Make use of empty lines to break code into meaningful
    groups. Add comments before groups where the intent/operation may be unclear.

- **Format SQL strings.** Strings of SQL queries inside python code should be formatted
    for readability. This means using newlines and indents for listed arguments as well
    as capitalizing SQL reserved words.

## Repository Guidelines

- **Make use of utils.** There is no point in writing the same code a dozen times. The
    utils folder will have all sorts of classes that simplify the process of connecting
    to the SQL server, formating printing, etc.

- **Add arguments to runners.** Every script that is runnable should have at least a
    `--config` argument to load a custom config and a `--log` argument to save the run
    print output. Add other options as you deem necessary.

- **Update documentation on version release.** Since things may move fast, it would be
    wasteful to document something that will change next week. However, when a new version
    is released, update the documentation for scripts you made.

    - Let's be honest though, this has never actually ever been done before.

- **Use simple, descriptive naming.** Try to make naming as intuituve and readable as
    possible. If a file/module's name is two letters, its probably not clear enough, but
    if it has four or more words seperated by underscores, its probably too wordy.

- **Print script progress.** This is a balance thing. If the console remains quite for 
    ten minutes, the script will look as if has hung or crashed, but if console prints
    something every half second, no one will be able to tell what is going on anyways.

- **Please update your .gitignore.** Nothing is worse than pulling an update to download
    a bunch of script caches and have you IDE settings overwritten. Please add any
    settings folders and script caches (if applicable) to your .gitignore.
