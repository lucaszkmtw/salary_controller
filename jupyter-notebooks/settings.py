from project.settings.settings import *


DEBUG = True

ALLOWED_HOSTS = ['*']

INSTALLED_APPS += [
    "django_extensions",
]

SHELL_PLUS = "ipython"

SHELL_PLUS_PRINT_SQL = True

NOTEBOOK_ARGUMENTS = [
    "--port",
    "8888",
    "--allow-root",
    "--no-browser",
]

IPYTHON_ARGUMENTS = [
    "--ext",
    "django_extensions.management.notebook_extension",
    "--debug",
]

IPYTHON_KERNEL_DISPLAY_NAME = "Django Shell-Plus"

"""SHELL_PLUS_POST_IMPORTS = [ # extra things to import in notebook
    ("module1.submodule", ("func1", "func2", "class1", "etc")),
    ("module2.submodule", ("func1", "func2", "class1", "etc"))
]"""

os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true" # only use in development
