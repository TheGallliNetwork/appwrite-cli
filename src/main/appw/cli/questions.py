import inquirer as iq

login = [
    iq.Text("email_id", message="Email ID"),
    iq.Password("password", message="Password"),
]

empty_organizations = [
    iq.Confirm(
        "create_org",
        default=True,
        message="There are no organizations, do you want to create one?")
]

create_organization = [
    iq.Text("name",
            message="Name of the organization",
            default="JigiJigi",
            show_default=True),
    iq.Text("team_id",
            message="Override the organization id",
            default="unique()",
            show_default=True)
]

create_project = [
    iq.Text("name",
            message="Name of the project",
            default="GalliStats",
            show_default=True),
    iq.Text("project_id",
            message="Override the project id",
            default="unique()",
            show_default=True)
]

remove_project = [
    iq.Password("password", message="Enter your account password")
]

create_database = [
    iq.Text("name",
            message="Name of the database",
            default="gallistats",
            show_default=True),
    iq.Text("database_id",
            message="Override the database id",
            default="unique()",
            show_default=True)
]

create_keys = [
    iq.Text("name", message="Name of the API key"),
    iq.Checkbox("auth",
                message="Auth permissions allowed for the API key",
                choices=[
                    "users.read",
                    "users.write",
                    "teams.read",
                    "teams.write",
                ]),
    iq.Checkbox("database",
                message="Database permissions allowed for the API key",
                choices=[
                    "databases.read",
                    "databases.write",
                    "collections.read",
                    "collections.write",
                    "attributes.read",
                    "attributes.write",
                    "indexes.read",
                    "indexes.write",
                    "documents.read",
                    "documents.write",
                ]),
    iq.Checkbox("function",
                message="Function permissions allowed for the API key",
                choices=[
                    "functions.read",
                    "functions.write",
                    "executions.read",
                    "executions.write",
                ]),
    iq.Checkbox("storage",
                message="Storage/File permissions allowed for the API key",
                choices=[
                    "files.read",
                    "files.write",
                    "buckets.read",
                    "buckets.write",
                ]),
]

create_platform = [
    iq.List("type",
            message="Select the platform type to register",
            choices=[
                ("Web App", "web"),
                ("Flutter Android", "flutter-android"),
                ("Flutter iOS", "flutter-ios"),
                ("Flutter Mac OS", "flutter-macos"),
                ("Flutter Linux", "flutter-linux"),
                ("Flutter Windows", "flutter-windows"),
                ("Apple iOS", "apple-ios"),
                ("Apple Mac OS", "apple-macos"),
                ("Android", "android"),
            ]),
    iq.Text("name",
            message="Name of your app"),
    iq.Text("key",
            message="App hostname/package name/bundle id")
]

create_provider = [
    iq.List("provider",
            message="Select the Oauth provider",
            choices=[
                ("Google", "google"),
                ("Facebook", "facebook"),
                ("Microsoft", "microsoft"),
                ("Yahoo", "yahoo"),
                ("Amazon", "amazon"),

            ]),
    iq.Text("app_id", message="App ID"),
    iq.Text("secret", message="App Secret")
]


def select_from_list(items, message=None, id_attr=None):
    return [
        iq.List("id",
                choices=list(
                    map(lambda x: (x.get('name'), x.get(id_attr or "$id")),
                        items)),
                message=message or "Select from the list")
    ]


def select_multiple_from_list(items, message=None, id_attr=None):
    return [iq.Checkbox("id",
                        choices=list(
                            map(lambda x: (
                                f"{x.get('name')}: {x.get(id_attr or '$id')}",
                                x.get(id_attr or "$id")),
                                items)),
                        message=message or "Select from the list")]


def confirm_delete(resource_type, resource_name, message=None):
    return [
        iq.Confirm("confirm",
                   default=False,
                   message=(message
                            or "Are you sure you want to remove the "
                               "{} [{}]".format(resource_type, resource_name)))
    ]


create_function = [
    iq.Text("name",
            message="Name of your function"),
    iq.List("execute",
            message="Select who has execution permissions",
            default="users",
            choices=[
                ("None", ""),
                ("Any", "any"),
                ("Guests", "guests"),
                ("All Users", "users"),
            ]),
    iq.List("runtime",
            message="Select function runtime",
            default="python-3.10",
            choices=[
                ("Python", "python-3.10"),
                ("Node JS", "node-16.0"),
                ("PHP", "php-8.0"),
            ]),
    iq.Text("entrypoint",
            message="Entry point file path of your function",
            default="src/index.py"),
    iq.Confirm("logging",
               message="Enable logging",
               default=False),

]
