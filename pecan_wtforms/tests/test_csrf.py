import os
import warnings
from unittest import TestCase


class TestCSRFValidation(TestCase):

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

    def test_referer_missing(self):
        response = self.app.post('/', params={
            'first_name': 'Ryan',
            'last_name': 'Petrello'
        })

        assert response.request.pecan['form'].errors == {
            'csrf_token': ['Referer checking failed - no Referer.']
        }

    def test_referer_mismatch(self):
        response = self.app.post('/', params={
            'first_name': 'Ryan',
            'last_name': 'Petrello'
        }, headers={'Referer': 'http://some-malicious-site'})

        assert response.request.pecan['form'].errors == {
            'csrf_token': [('Referer checking failed - '
                            'http://some-malicious-site does not match '
                            'http://localhost:80/.')]
        }

    def test_missing_csrf_token(self):
        response = self.app.post('/', params={
            'first_name': 'Ryan',
            'last_name': 'Petrello'
        }, headers={'Referer': 'http://localhost:80'})

        assert response.request.pecan['form'].errors == {
            'csrf_token': ['CSRF token missing.']
        }

    def test_invalid_csrf_token(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")

            response = self.app.post('/', params={
                'first_name': 'Ryan',
                'last_name': 'Petrello',
                'csrf_token': 'ABC123'
            }, headers={'Referer': 'http://localhost:80'})

        assert response.request.pecan['form'].errors == {
            'csrf_token': ['CSRF token incorrect.']
        }

    def test_successful_validation(self):
        import pecan_wtforms
        response = self.app.get('/')
        cookie_header = response.headers['Set-Cookie']
        parts = cookie_header.split('%s=' % pecan_wtforms.Form.SECRET_KEY)
        token = parts[1].split(';')[0]

        response = self.app.post('/', params={
            'first_name': 'Ryan',
            'last_name': 'Petrello',
            'csrf_token': token
        }, headers={'Referer': 'http://localhost:80'})

        assert response.request.pecan['form'].errors == {}
        assert response.body == 'Ryan Petrello'


class TestCSRFUtilities(TestCase):

    def test_constant_time_compare(self):
        from pecan_wtforms.form import constant_time_compare
        assert constant_time_compare('', '')
        assert constant_time_compare('A', 'A')
        assert not constant_time_compare('A', 'a')
