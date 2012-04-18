import os
from unittest import TestCase


class TestIdempotentFormWrapper(TestCase):

    def setUp(self):
        import pecan_wtforms
        from pecan import Pecan, expose
        from webtest import TestApp

        class SimpleForm(pecan_wtforms.form.Form):
            first_name = pecan_wtforms.fields.TextField(
                "First Name",
                [pecan_wtforms.validators.Required()]
            )
            last_name = pecan_wtforms.fields.TextField(
                "Last Name",
                [pecan_wtforms.validators.Required()]
            )
        self.formcls_ = SimpleForm

        class RootController(object):
            @expose()
            @pecan_wtforms.with_form(SimpleForm)
            def index(self):
                return 'Hello, World!'

            @expose('name.html')
            @pecan_wtforms.with_form(SimpleForm)
            def name(self):
                return dict()

        template_path = os.path.join(
                os.path.dirname(__file__),
                'templates'
        )

        self.app = TestApp(Pecan(
            RootController(),
            template_path=template_path
        ))

    def test_request_injection(self):
        response = self.app.get('/')
        assert response.body == 'Hello, World!'
        assert response.namespace == 'Hello, World!'
        assert 'form' in response.request.pecan
        assert isinstance(response.request.pecan['form'], self.formcls_)

    def test_template_namespace_injection(self):
        response = self.app.get('/name')
        form = self.formcls_()

        assert 'form' in response.namespace
        assert isinstance(response.namespace['form'], self.formcls_)

        assert str(form.first_name.label) in response.body
        assert str(form.first_name) in response.body
        assert str(form.last_name.label) in response.body
        assert str(form.last_name) in response.body


class TestIdempotentFormWrapperWithCustomKey(TestCase):

    def setUp(self):
        import pecan_wtforms
        from pecan import Pecan, expose
        from webtest import TestApp

        class SimpleForm(pecan_wtforms.form.Form):
            first_name = pecan_wtforms.fields.TextField(
                "First Name",
                [pecan_wtforms.validators.Required()]
            )
            last_name = pecan_wtforms.fields.TextField(
                "Last Name",
                [pecan_wtforms.validators.Required()]
            )
        self.formcls_ = SimpleForm

        class RootController(object):
            @expose()
            @pecan_wtforms.with_form(SimpleForm, key='some_form')
            def index(self):
                return 'Hello, World!'

            @expose('name_with_custom_key.html')
            @pecan_wtforms.with_form(SimpleForm, key='some_form')
            def name(self):
                return dict()

        template_path = os.path.join(
                os.path.dirname(__file__),
                'templates'
        )

        self.app = TestApp(Pecan(
            RootController(),
            template_path=template_path
        ))

    def test_request_injection(self):
        response = self.app.get('/')
        assert response.body == 'Hello, World!'
        assert response.namespace == 'Hello, World!'
        assert 'some_form' in response.request.pecan
        assert isinstance(response.request.pecan['some_form'], self.formcls_)

    def test_template_namespace_injection(self):
        response = self.app.get('/name')
        form = self.formcls_()

        assert 'some_form' in response.namespace
        assert isinstance(response.namespace['some_form'], self.formcls_)

        assert str(form.first_name.label) in response.body
        assert str(form.first_name) in response.body
        assert str(form.last_name.label) in response.body
        assert str(form.last_name) in response.body


class TestWrapperValidation(TestCase):

    def setUp(self):
        import pecan_wtforms
        from pecan import Pecan, expose
        from webtest import TestApp

        class SimpleForm(pecan_wtforms.form.Form):
            first_name = pecan_wtforms.fields.TextField(
                "First Name",
                [pecan_wtforms.validators.Required()]
            )
            last_name = pecan_wtforms.fields.TextField(
                "Last Name",
                [pecan_wtforms.validators.Required()]
            )
        self.formcls_ = SimpleForm

        class RootController(object):
            @expose()
            @pecan_wtforms.with_form(SimpleForm)
            def index(self, **kw):
                return '%s %s' % (
                    kw.get('first_name', ''),
                    kw.get('last_name', '')
                )

        template_path = os.path.join(
                os.path.dirname(__file__),
                'templates'
        )

        self.app = TestApp(Pecan(
            RootController(),
            template_path=template_path
        ))

    def test_no_errors(self):
        response = self.app.post('/', params={
            'first_name': 'Ryan',
            'last_name': 'Petrello'
        })
        assert response.body == 'Ryan Petrello'
        assert response.namespace == 'Ryan Petrello'
        assert 'form' in response.request.pecan
        assert isinstance(response.request.pecan['form'], self.formcls_)
        assert response.request.pecan['form'].errors == {}

    def test_with_errors(self):
        response = self.app.post('/', params={})
        assert response.body == 'None None'
        assert response.namespace == 'None None'
        assert 'form' in response.request.pecan
        assert isinstance(response.request.pecan['form'], self.formcls_)
        assert response.request.pecan['form'].errors == {
            'first_name': ['This field is required.'],
            'last_name': ['This field is required.']
        }


class TestWrapperValidationWithGETMethod(TestCase):

    def setUp(self):
        import pecan_wtforms
        from pecan import Pecan, expose
        from webtest import TestApp

        class SimpleForm(pecan_wtforms.form.Form):
            first_name = pecan_wtforms.fields.TextField(
                "First Name",
                [pecan_wtforms.validators.Required()]
            )
            last_name = pecan_wtforms.fields.TextField(
                "Last Name",
                [pecan_wtforms.validators.Required()]
            )
        self.formcls_ = SimpleForm

        class RootController(object):
            @expose()
            @pecan_wtforms.with_form(SimpleForm, validate_safe=True)
            def index(self, **kw):
                print kw
                return '%s %s' % (
                    kw.get('first_name', ''),
                    kw.get('last_name', '')
                )

        template_path = os.path.join(
                os.path.dirname(__file__),
                'templates'
        )

        self.app = TestApp(Pecan(
            RootController(),
            template_path=template_path
        ))

    def test_no_errors(self):
        response = self.app.get('/?first_name=Ryan&last_name=Petrello')
        assert response.body == 'Ryan Petrello'
        assert response.namespace == 'Ryan Petrello'
        assert 'form' in response.request.pecan
        assert isinstance(response.request.pecan['form'], self.formcls_)
        assert response.request.pecan['form'].errors == {}

    def test_with_errors(self):
        response = self.app.get('/')
        assert response.body == 'None None'
        assert response.namespace == 'None None'
        assert 'form' in response.request.pecan
        assert isinstance(response.request.pecan['form'], self.formcls_)
        assert response.request.pecan['form'].errors == {
            'first_name': ['This field is required.'],
            'last_name': ['This field is required.']
        }


class TestValidatorCoercion(TestCase):

    def setUp(self):
        import pecan_wtforms
        from pecan import Pecan, expose
        from webtest import TestApp

        class SimpleForm(pecan_wtforms.form.Form):
            age = pecan_wtforms.fields.IntegerField("Age")

        self.formcls_ = SimpleForm

        class RootController(object):
            @expose()
            @pecan_wtforms.with_form(SimpleForm)
            def index(self, **kw):
                assert type(kw['age']) is int
                return str(kw['age'])

        template_path = os.path.join(
                os.path.dirname(__file__),
                'templates'
        )

        self.app = TestApp(Pecan(
            RootController(),
            template_path=template_path
        ))

    def test_int_conversion_by_validator(self):
        response = self.app.post('/', params={
            'age': '30'
        })
        assert response.body == '30'
        assert response.namespace == '30'
        assert response.request.pecan['form'].errors == {}


class TestCustomHandler(TestCase):

    def setUp(self):
        import pecan_wtforms
        from pecan import Pecan, expose
        from pecan.middleware.recursive import RecursiveMiddleware
        from webtest import TestApp

        class SimpleForm(pecan_wtforms.form.Form):
            first_name = pecan_wtforms.fields.TextField(
                "First Name",
                [pecan_wtforms.validators.Required()]
            )
            last_name = pecan_wtforms.fields.TextField(
                "Last Name",
                [pecan_wtforms.validators.Required()]
            )
        self.formcls_ = SimpleForm

        class RootController(object):

            @expose('name.html')
            @pecan_wtforms.with_form(SimpleForm)
            def index(self, **kw):
                return dict()

            @expose()
            @pecan_wtforms.with_form(SimpleForm, error_cfg={'handler': '/'})
            def save(self, **kw):
                return 'SAVED!'

        template_path = os.path.join(
                os.path.dirname(__file__),
                'templates'
        )

        self.app = TestApp(RecursiveMiddleware(Pecan(
            RootController(),
            template_path=template_path
        )))

    def test_no_errors(self):
        response = self.app.post('/save', params={
            'first_name': 'Ryan',
            'last_name': 'Petrello'
        })
        assert response.body == 'SAVED!'
        assert response.namespace == 'SAVED!'
        assert 'form' in response.request.pecan
        assert isinstance(response.request.pecan['form'], self.formcls_)
        assert response.request.pecan['form'].errors == {}

    def test_custom_error_handler(self):
        response = self.app.post('/save', params={
            'first_name': 'Ryan',
        })

        form = self.formcls_()
        assert str(form.first_name.label) in response.body
        assert form.first_name(value='Ryan') in response.body
        assert str(form.last_name.label) in response.body
        assert str(form.last_name) in response.body

        assert 'form' in response.request.pecan
        assert isinstance(response.request.pecan['form'], self.formcls_)
        assert response.request.pecan['form'].errors == {
            'last_name': [u'This field is required.']
        }


class TestGenericHandler(TestCase):

    def setUp(self):
        import pecan_wtforms
        from pecan import Pecan, expose
        from pecan.middleware.recursive import RecursiveMiddleware
        from webtest import TestApp

        class SimpleForm(pecan_wtforms.form.Form):
            first_name = pecan_wtforms.fields.TextField(
                "First Name",
                [pecan_wtforms.validators.Required()]
            )
            last_name = pecan_wtforms.fields.TextField(
                "Last Name",
                [pecan_wtforms.validators.Required()]
            )
        self.formcls_ = SimpleForm

        class RootController(object):

            @expose(generic=True, template='name.html')
            @pecan_wtforms.with_form(SimpleForm)
            def index(self, **kw):
                return dict()

            @index.when(method='POST')
            @pecan_wtforms.with_form(SimpleForm, error_cfg={'handler': '/'})
            def save(self, **kw):
                return 'SAVED!'

        template_path = os.path.join(
                os.path.dirname(__file__),
                'templates'
        )

        self.app = TestApp(RecursiveMiddleware(Pecan(
            RootController(),
            template_path=template_path
        )))

    def test_no_errors(self):
        response = self.app.post('/', params={
            'first_name': 'Ryan',
            'last_name': 'Petrello'
        })
        assert response.body == 'SAVED!'
        assert response.namespace == 'SAVED!'
        assert 'form' in response.request.pecan
        assert isinstance(response.request.pecan['form'], self.formcls_)
        assert response.request.pecan['form'].errors == {}

    def test_custom_error_handler(self):
        response = self.app.post('/', params={
            'first_name': 'Ryan',
        })

        form = self.formcls_()
        assert str(form.first_name.label) in response.body
        assert form.first_name(value='Ryan') in response.body
        assert str(form.last_name.label) in response.body
        assert str(form.last_name) in response.body

        assert 'form' in response.request.pecan
        assert isinstance(response.request.pecan['form'], self.formcls_)
        assert response.request.pecan['form'].errors == {
            'last_name': [u'This field is required.']
        }


class TestCallableHandler(TestCase):

    def setUp(self):
        import pecan_wtforms
        from pecan import Pecan, expose, request
        from pecan.middleware.recursive import RecursiveMiddleware
        from webtest import TestApp

        class SimpleForm(pecan_wtforms.form.Form):
            first_name = pecan_wtforms.fields.TextField(
                "First Name",
                [pecan_wtforms.validators.Required()]
            )
            last_name = pecan_wtforms.fields.TextField(
                "Last Name",
                [pecan_wtforms.validators.Required()]
            )
        self.formcls_ = SimpleForm

        class RootController(object):

            @expose(generic=True, template='name.html')
            @pecan_wtforms.with_form(SimpleForm)
            def index(self, **kw):
                return dict()

            @index.when(method='POST')
            @pecan_wtforms.with_form(
                SimpleForm,
                error_cfg={'handler': lambda: request.path}
            )
            def save(self, **kw):
                return 'SAVED!'

        template_path = os.path.join(
                os.path.dirname(__file__),
                'templates'
        )

        self.app = TestApp(RecursiveMiddleware(Pecan(
            RootController(),
            template_path=template_path
        )))

    def test_no_errors(self):
        response = self.app.post('/', params={
            'first_name': 'Ryan',
            'last_name': 'Petrello'
        })
        assert response.body == 'SAVED!'
        assert response.namespace == 'SAVED!'
        assert 'form' in response.request.pecan
        assert isinstance(response.request.pecan['form'], self.formcls_)
        assert response.request.pecan['form'].errors == {}

    def test_custom_error_handler(self):
        response = self.app.post('/', params={
            'first_name': 'Ryan',
        })

        form = self.formcls_()
        assert str(form.first_name.label) in response.body
        assert form.first_name(value='Ryan') in response.body
        assert str(form.last_name.label) in response.body
        assert str(form.last_name) in response.body

        assert 'form' in response.request.pecan
        assert isinstance(response.request.pecan['form'], self.formcls_)
        assert response.request.pecan['form'].errors == {
            'last_name': [u'This field is required.']
        }


class TestErrorFillFromRequestArgs(TestCase):
    """
    If a form is submitted and handled by a callable `handler`,
    the `populate()` method should enforce values sent in the original request
    (generally, request.POST).
    """

    def setUp(self):
        import pecan_wtforms
        from pecan import Pecan, expose, request
        from pecan.middleware.recursive import RecursiveMiddleware
        from webtest import TestApp

        class SimpleForm(pecan_wtforms.form.Form):
            first_name = pecan_wtforms.fields.TextField(
                "First Name",
                [pecan_wtforms.validators.Required()]
            )
            last_name = pecan_wtforms.fields.TextField(
                "Last Name",
                [pecan_wtforms.validators.Required()]
            )
        self.formcls_ = SimpleForm

        class RootController(object):

            @expose(generic=True, template='name.html')
            @pecan_wtforms.with_form(SimpleForm)
            def index(self, **kw):
                request.pecan['form'].process(first_name='Ryan')
                return dict()

            @index.when(method='POST')
            @pecan_wtforms.with_form(
                SimpleForm,
                error_cfg={'handler': lambda: request.path}
            )
            def save(self, **kw):
                return 'SAVED!'

        template_path = os.path.join(
                os.path.dirname(__file__),
                'templates'
        )

        self.app = TestApp(RecursiveMiddleware(Pecan(
            RootController(),
            template_path=template_path
        )))

    def test_no_errors(self):
        response = self.app.post('/', params={
            'first_name': 'Ryan',
            'last_name': 'Petrello'
        })
        assert response.body == 'SAVED!'
        assert response.namespace == 'SAVED!'
        assert 'form' in response.request.pecan
        assert isinstance(response.request.pecan['form'], self.formcls_)
        assert response.request.pecan['form'].errors == {}

    def test_default_prefill(self):
        response = self.app.get('/')

        form = self.formcls_()
        assert 'form' in response.request.pecan
        assert str(form.first_name.label) in response.body
        assert form.first_name(value='Ryan') in response.body

    def test_error_fill(self):
        response = self.app.post('/', params={
            'first_name': '',
            'last_name': 'Petrello'
        })

        form = self.formcls_()
        assert 'form' in response.request.pecan
        assert str(form.first_name.label) in response.body
        assert form.first_name(value='Ryan') not in response.body
        assert form.first_name(value='') in response.body


class TestAutoErrorMarkup(TestCase):

    def setUp(self):
        import pecan_wtforms
        from pecan import Pecan, expose, request
        from pecan.middleware.recursive import RecursiveMiddleware
        from webtest import TestApp

        class SimpleForm(pecan_wtforms.form.Form):
            first_name = pecan_wtforms.fields.TextField(
                "First Name",
                [pecan_wtforms.validators.Required()]
            )
            last_name = pecan_wtforms.fields.TextField(
                "Last Name",
                [pecan_wtforms.validators.Required()]
            )
        self.formcls_ = SimpleForm

        class RootController(object):

            @expose(generic=True, template='name.html')
            @pecan_wtforms.with_form(SimpleForm)
            def index(self, **kw):
                return dict()

            @index.when(method='POST')
            @pecan_wtforms.with_form(
                SimpleForm,
                error_cfg={
                    'handler': lambda: request.path,
                    'auto_insert_errors': True
                }
            )
            def save(self, **kw):
                return 'SAVED!'  # pragma: nocover

        template_path = os.path.join(
                os.path.dirname(__file__),
                'templates'
        )

        self.app = TestApp(RecursiveMiddleware(Pecan(
            RootController(),
            template_path=template_path
        )))

    def test_custom_error_handler(self):
        response = self.app.post('/', params={
            'first_name': 'Ryan',
        })
        assert ''.join([
            '<label for="last_name">Last Name</label>: ',
            '<span class="error-message">This field is required.</span>\n',
            ('<input class="error" id="last_name" name="last_name" type="text"'
            ' value="">')
        ]) in response.body

        assert 'form' in response.request.pecan
        assert isinstance(response.request.pecan['form'], self.formcls_)
        assert response.request.pecan['form'].errors == {
            'last_name': [u'This field is required.']
        }


class TestRESTControllerHandler(TestCase):

    def setUp(self):
        import pecan_wtforms
        from pecan import Pecan, expose, request
        from pecan.rest import RestController
        from pecan.middleware.recursive import RecursiveMiddleware
        from webtest import TestApp

        class SimpleForm(pecan_wtforms.form.Form):
            first_name = pecan_wtforms.fields.TextField(
                "First Name",
                [pecan_wtforms.validators.Required()]
            )
            last_name = pecan_wtforms.fields.TextField(
                "Last Name",
                [pecan_wtforms.validators.Required()]
            )
        self.formcls_ = SimpleForm

        class RootController(RestController):

            @expose('name.html')
            @pecan_wtforms.with_form(SimpleForm)
            def get_all(self, **kw):
                return dict()

            @expose()
            @pecan_wtforms.with_form(
                SimpleForm,
                error_cfg={'handler': lambda: request.path}
            )
            def post(self, **kw):
                return 'SAVED!'  # pragma: nocover

        template_path = os.path.join(
                os.path.dirname(__file__),
                'templates'
        )

        self.app = TestApp(RecursiveMiddleware(Pecan(
            RootController(),
            template_path=template_path
        )))

    def test_rest_redirection(self):
        response = self.app.post('/', params={
            'first_name': 'Ryan',
        })

        form = self.formcls_()
        assert str(form.first_name.label) in response.body
        assert form.first_name(value='Ryan') in response.body
        assert str(form.last_name.label) in response.body
        assert str(form.last_name) in response.body

        assert 'form' in response.request.pecan
        assert isinstance(response.request.pecan['form'], self.formcls_)
        assert response.request.pecan['form'].errors == {
            'last_name': [u'This field is required.']
        }

    def test_rest_redirection_with_method_param(self):
        response = self.app.post('/?_method=POST', params={
            'first_name': 'Ryan',
        })

        form = self.formcls_()
        assert str(form.first_name.label) in response.body
        assert form.first_name(value='Ryan') in response.body
        assert str(form.last_name.label) in response.body
        assert str(form.last_name) in response.body

        assert 'form' in response.request.pecan
        assert isinstance(response.request.pecan['form'], self.formcls_)
        assert response.request.pecan['form'].errors == {
            'last_name': [u'This field is required.']
        }
