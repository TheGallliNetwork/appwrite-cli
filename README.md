# 3rd party Appwrite CLI - `appw`

> This is not a replacement for the official Appwrite CLI. It just provides
> additional functionality by using the Appwrite API directly.

### Installation
```sh
pip install appw
```

This installs a command line tool called `appw` which helps you manage your
appwrite instance.


### Usage

```sh
$ appw --help

 Usage: appw [OPTIONS] COMMAND [ARGS]...

 Appwrite wrapper cli to perform administrative tasks

╭─ Options ─────────────────────────────────────────────────────────────────────────────────╮
│ --help      Show this message and exit.                                                   │
╰───────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ────────────────────────────────────────────────────────────────────────────────╮
│ create       Create a new org, project, key, db, collection etc;                          │
│ delete       Remove org, project, key, db, collection etc;                                │
│ get          Get a specific org, project, key, db, collection etc; details                │
│ list         List org, project, key, db, collection etc;                                  │
│ login                                                                                     │
│ show         View summary/information of the current context                              │
│ snapshot     Create/restore/migrate snapshots                                             │
│ switch       Switch the default org/project/database                                      │
╰───────────────────────────────────────────────────────────────────────────────────────────╯
```

```sh
appw snapshot --help                          1 changed file  main

 Usage: appw snapshot [OPTIONS] COMMAND [ARGS]...

 Create/restore/migrate snapshots

╭─ Options ─────────────────────────────────────────────────────────────────────────────────╮
│ --help      Show this message and exit.                                                   │
╰───────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ────────────────────────────────────────────────────────────────────────────────╮
│ create                                                                                    │
│ restore   Restores an existing snapshot and syncs everything - names, schema and more     │
╰───────────────────────────────────────────────────────────────────────────────────────────╯
```

More details below.


### Creating a snapshot
Assuming you are running your appwrite instance at http://localhost (this will
be made configurable in the upcoming changes), you can run the following
command to create a snapshot of your entire configuration.

```sh
appw login  # enter your credentials
appw snapshot create
```

This creates the `snapshots` directory under the current directory where you
are running the command with a backup of all the configurations. You can
check-in these files into your (private) repo. If you are using public
repositories keep in mind that your OAuth credentials also get backend up in
plain text.

### Restoring/Syncing snapshot
You can use the `snapshot restore` command to either sync/migrate an existing
appwrite instance or setup a completely new instance.

```sh
appw snapshot restore
```

Once you have the snapshot restored, you can run the official `appwrite` cli to
initialize the project (to generate appwrite.json) - helps in deploying functions
during development

```
appwrite init
```

## NOTE
As mentioned above, this is not a replacement for the offcial CLI. But it has
commands to create a new/update/remove organization, projects etc; without
having to create them on the appwrite web console directly. This is what helps
us to create and restore snapshots.

## Contribute
Features, bug-fixes, issue reports are all welcome.
