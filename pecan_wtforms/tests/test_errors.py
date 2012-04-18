from unittest import TestCase


class TestErrorWidget(TestCase):

    def make_form(self, values={}, config={}):
        import pecan_wtforms

        class SmartField(pecan_wtforms.fields.TextField):
            widget = pecan_wtforms.errors.ErrorMarkupWidget(
                pecan_wtforms.fields.TextField.widget,
                **config
            )

        class SimpleForm(pecan_wtforms.Form):
            name = SmartField(
                "Name",
                [pecan_wtforms.validators.Required()]
            )

        f = SimpleForm(**values)
        f.validate()
        return f

    def test_errorless_field(self):
        f = self.make_form({'name': 'Ryan'})
        assert f.errors == {}
        assert str(f.name) == ('<input id="name" name="name" type="text" '
                               'value="Ryan">')

    def test_error_prepend(self):
        f = self.make_form()
        assert f.errors == {'name': ['This field is required.']}
        assert str(f.name).startswith(
            '<span class="error-message">This field is required.</span>'
        )

    def test_error_append(self):
        f = self.make_form(config={'prepend_errors': False})
        assert f.errors == {'name': ['This field is required.']}
        assert str(f.name).strip().endswith(
            '<span class="error-message">This field is required.</span>'
        )

    def test_custom_formatter(self):
        f = self.make_form(config={
            'formatter': lambda msg: 'OMG! %s' % msg
        })
        assert f.errors == {'name': ['This field is required.']}
        assert str(f.name).startswith(
            'OMG! This field is required.'
        )

    def test_format_multiple_errors(self):
        from pecan_wtforms.errors import ErrorMarkupWidget
        markup = ErrorMarkupWidget(None).format_errors(['Error 1', 'Error 2'])
        assert markup == ''.join([
            '<span class="error-message">Error 1</span>\n',
            '<span class="error-message">Error 2</span>\n'
        ])

    def test_default_error_class(self):
        f = self.make_form()
        assert f.errors == {'name': ['This field is required.']}
        assert '<input class="error"' in str(f.name)

    def test_custom_error_class(self):
        f = self.make_form(config={'class_': 'failure'})
        assert f.errors == {'name': ['This field is required.']}
        assert '<input class="failure"' in str(f.name)
