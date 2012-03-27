__version__ = 0.1

from wtforms import fields, widgets, validators  # noqa
from wtforms.fields import *
from wtforms.validators import *
from wtforms.widgets import *
from wtforms import ValidationError  # noqa

from .form import Form

from .decorator import with_form

__all__ = ['Form', 'ValidationError', 'fields', 'validators', 'widgets',
            'with_form']
