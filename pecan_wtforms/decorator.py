from pecan import request, response
from pecan.middleware.recursive import ForwardRequestException

__all__ = ['with_form']


def with_form(formcls, key='form', error_cfg={}, **kw):
    """
    Used to decorate a Pecan controller with form creation for GET | HEAD and
    form validation for anything else (e.g., POST | PUT | DELETE ).

    For an HTTP GET or HEAD request, the form is instantiated and
    injected into the request object at ``request.pecan['form']`` and in
    the template namespace at ``form`` (unless the ``key`` is otherwise
    specified).

    For an HTTP POST, PUT, or DELETE (non-idempotent) request, the form is
    instantiated and validated.  Errors from validation (if any) are accessible
    at ``request.pecan['form'].errors``.

    Optionally, validation errors can be made to trigger an internal HTTP
    redirect by specifying a ``handler`` in the ``error_cfg`` argument.

    :param formcls: A subclass of ``wtforms.form.Form``
    :param key: The key used to inject the form in the template namespace
    :param error_cfg: a dictionary containing configuration for
                         displaying validatior errors:

                         ``handler`` - a URI path to redirect to when form
                                       validation fails.  Can also be a
                                       callable that returns a URI path.

                         ``auto_insert_errors`` - when True, markup for
                                                  validation errors will
                                                  automatically be added
                                                  adjacent to erronuous fields.

                         ``prepend_errors`` - when True, error markup will be
                                              added before the input control.
                                              When False, error markup will be
                                              added after the input control.
                                              Defaults to True.

                         ``formatter`` - a callable used to wrap error messages
                                         with HTML.  The default wraps messages
                                         in <span>'s separated by newlines.

                          ``class_`` - the class added to input fields when
                                       there is an error for that field.
                                       Defaults to 'error`.
    """
    def deco(f):

        def wrapped(*args, **kwargs):
            copy_error_cfg = error_cfg.copy()
            error_handler = copy_error_cfg.pop('handler', None)

            form = request.environ.pop('pecan.validation_form', None) or \
                   formcls(
                       request.POST,
                       csrf_context={
                           'request': request,
                           'response': response
                       },
                       error_cfg=copy_error_cfg, **kw
                   )

            if key not in request.pecan:
                request.pecan[key] = form

            if request.method not in ('GET', 'HEAD') and \
                not form.validate() and error_handler is not None:
                location = error_handler
                if callable(location):
                    location = location()
                request.environ['REQUEST_METHOD'] = 'GET'
                request.environ['pecan.validation_redirected'] = True
                request.environ['pecan.validation_form'] = form
                raise ForwardRequestException(location)

            # Remove the CSRF token (so it's not passed to the controller)
            kwargs.pop('csrf_token', None)

            ns = f(*args, **kwargs)
            if type(ns) is dict and key not in ns:
                ns[key] = form
            return ns

        return wrapped

    return deco
