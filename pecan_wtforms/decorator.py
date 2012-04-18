from pecan import request, response, redirect

__all__ = ['with_form', 'redirect_to_handler']


def with_form(formcls, key='form', validate_safe=False, error_cfg={}, **kw):
    """
    Used to decorate a Pecan controller with form creation for GET | HEAD and
    form validation for anything else (e.g., POST | PUT | DELETE ).

    For an HTTP GET or HEAD request, the form is instantiated and
    injected into the request object at ``request.pecan['form']`` and in
    the template namespace at ``form`` (unless the ``key`` is otherwise
    specified).

    For an HTTP POST, PUT, or DELETE (RFC2616 unsafe methods) request, the
    form is instantiated and validated.  Errors from validation (if any) are
    accessible at ``request.pecan['form'].errors``.

    Optionally, validation errors can be made to trigger an internal HTTP
    redirect by specifying a ``handler`` in the ``error_cfg`` argument.

    :param formcls: A subclass of ``wtforms.form.Form``
    :param key: The key used to inject the form in the template namespace
    :param validate_safe: When True, validation is performed against GET data
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
                       request.params,
                       csrf_context={
                           'request': request,
                           'response': response
                       },
                       error_cfg=copy_error_cfg, **kw
                   )

            if key not in request.pecan:
                request.pecan[key] = form

            if (request.method not in ('GET', 'HEAD') or validate_safe):
                if not form.validate() and error_handler is not None:
                    redirect_to_handler(form, error_handler)

                # Remove the CSRF token (so it's not passed to the controller)
                kwargs.pop('csrf_token', None)

                # Overwrite kwargs with "validated" versions
                kwargs.update(form.data)

            ns = f(*args, **kwargs)
            if isinstance(ns, dict) and key not in ns:
                ns[key] = form
            return ns

        return wrapped

    return deco


def redirect_to_handler(form, location):
    """
    Cause a form with error to internally redirect to a URI path.

    This is generally for internal use, but can be called from within a Pecan
    controller to trigger a validation failure from *within* the controller
    itself, e.g.::

        @expose()
        @with_form(SomeForm, error_cfg={
            'auto_insert_errors': True, 'handler': '/some/handler'
        })
        def some_controller(self, **kw):
            if some_bad_condition():
                form = pecan.request.pecan['form']
                form.some_field.errors.append('Validation failure!')
                redirect_to_handler(form, '/some/handler')
    """
    setattr(form, '_validation_original_data', request.params)
    if callable(location):
        location = location()
    request.environ['REQUEST_METHOD'] = 'GET'
    request.environ['pecan.validation_redirected'] = True
    request.environ['pecan.validation_form'] = form
    redirect(location, internal=True)
