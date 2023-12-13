from .settings import *

DEBUG = True

ALLOWED_HOSTS = ['*']

INTERNAL_IPS = [
    '127.0.0.1',
    'localhost'
]


def show_toolbar(request):
    return DEBUG


MIDDLEWARE += [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK": show_toolbar,
}

INSTALLED_APPS += [
    'debug_toolbar',
    'template_timings_panel',
    # "template_profiler_panel",
]

DEBUG_TOOLBAR_PANELS = [
    'debug_toolbar.panels.versions.VersionsPanel',
    'debug_toolbar.panels.timer.TimerPanel',
    'debug_toolbar.panels.settings.SettingsPanel',
    'debug_toolbar.panels.headers.HeadersPanel',
    'debug_toolbar.panels.request.RequestPanel',
    'debug_toolbar.panels.sql.SQLPanel',
    'debug_toolbar.panels.staticfiles.StaticFilesPanel',
    'debug_toolbar.panels.templates.TemplatesPanel',
    'debug_toolbar.panels.cache.CachePanel',
    'debug_toolbar.panels.signals.SignalsPanel',
    'debug_toolbar.panels.logging.LoggingPanel',
    'debug_toolbar.panels.redirects.RedirectsPanel',
    'template_timings_panel.panels.TemplateTimings.TemplateTimings',
]

IGNORED_TEMPLATES = ['debug_toolbar/*']
