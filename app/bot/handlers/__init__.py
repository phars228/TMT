from .auth import setup_auth
from .teams import setup_teams
from .tasks import setup_tasks

def setup_handlers(application):
    setup_auth(application)
    setup_teams(application)
    setup_tasks(application)