__all__ = ['default']


def default(default):
    """
    A filter to provide a default value when a field is empty, e.g.,

    class AgeForm(pecan.ext.wtforms.SecureForm):
        age = pecan.ext.wtforms.TextField('Age', filters=[default(25)])
    """
    def wrap(data):
        if data is None or data == '':
            return default
        else:
            return data
    return wrap
