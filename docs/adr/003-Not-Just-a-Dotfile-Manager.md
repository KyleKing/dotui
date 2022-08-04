# Not Just a .FILE Manager

One of the ideas I had brainstormed was to track at the snippet-level instead of the file-level

This would be useful because it is much easier to conceptualize that these are the bits of code related to this tool that I want to use. Rather than thinking about these bits of code are in these files with other bits of code and what was the tool they were for?

This is a really hard problem to solve generically, but [callrbx/meld](https://github.com/callrbx/meld) ([libmeld](https://docs.rs/meld-config-manager/latest/libmeld)) looks to be going in this direction

## Background

> "While syncing dot files is fantastic among collaborators at any project, I would prefer if the entire files didn't have to be synced. A selective sync/composability would be the killer feature for me."

Instead of per file, could group snippets into groups which contain multiple snippets, entire files, and/or commands (such as `brew install <package_name>`). There would also need to be dependencies between individual snippets or whole groups to create hierarchies. The tool could then convert these abstract collections into concrete files, which are loaded in the right order.

Because the snippets are grouped, you could do interesting things, like compare against use in shell history or identify if an orphaned package isn't being used. If needed, the snippets could be mapped to certain files and then added as templates as appropriate. Or the snippets could just be put into massive files that collect all of the necessary code

This does get very complicated, but another workaround might to improve templating like I implemented for calcipy, but at that point there are much more robust alternatives like jinja2 or even copier or cruft. Generally a package manager like `oh-my-zsh` or `pipx` might better accomplish the general goal of making CLI-tools configurable.

