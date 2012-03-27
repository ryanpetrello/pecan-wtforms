import os
from unittest import TestCase


class TestIdempotentFormWrapper(TestCase):

    def setUp(self):
        import wtforms
        from pecan import Pecan, expose
        from pecan_wtf import with_form
        from webtest import TestApp

        class SimpleForm(wtforms.form.Form):
            first_name = wtforms.fields.TextField(
                "First Name",
                [wtforms.validators.Required()]
            )
            last_name = wtforms.fields.TextField(
                "Last Name",
                [wtforms.validators.Required()]
            )
        self.formcls_ = SimpleForm

        class RootController(object):
            @expose()
            @with_form(SimpleForm)
            def index(self):
                return 'Hello, World!'

            @expose('name.html')
            @with_form(SimpleForm)
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
        import wtforms
        from pecan import Pecan, expose
        from pecan_wtf import with_form
        from webtest import TestApp

        class SimpleForm(wtforms.form.Form):
            first_name = wtforms.fields.TextField(
                "First Name",
                [wtforms.validators.Required()]
            )
            last_name = wtforms.fields.TextField(
                "Last Name",
                [wtforms.validators.Required()]
            )
        self.formcls_ = SimpleForm

        class RootController(object):
            @expose()
            @with_form(SimpleForm, key='some_form')
            def index(self):
                return 'Hello, World!'

            @expose('name_with_custom_key.html')
            @with_form(SimpleForm, key='some_form')
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
        import wtforms
        from pecan import Pecan, expose
        from pecan_wtf import with_form
        from webtest import TestApp

        class SimpleForm(wtforms.form.Form):
            first_name = wtforms.fields.TextField(
                "First Name",
                [wtforms.validators.Required()]
            )
            last_name = wtforms.fields.TextField(
                "Last Name",
                [wtforms.validators.Required()]
            )
        self.formcls_ = SimpleForm

        class RootController(object):
            @expose()
            @with_form(SimpleForm)
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
        assert response.body == ' '
        assert response.namespace == ' '
        assert 'form' in response.request.pecan
        assert isinstance(response.request.pecan['form'], self.formcls_)
        assert response.request.pecan['form'].errors == {
            'first_name': ['This field is required.'],
            'last_name': ['This field is required.']
        }
