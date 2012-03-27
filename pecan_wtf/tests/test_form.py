from unittest import TestCase


class TestFormValidation(TestCase):

    def test_simple_validation(self):
        import pecan_wtf

        class SimpleForm(pecan_wtf.form.Form):
            first_name = pecan_wtf.fields.TextField(
                "First Name",
                [pecan_wtf.validators.Required()]
            )
            last_name = pecan_wtf.fields.TextField(
                "Last Name",
                [pecan_wtf.validators.Required()]
            )

        f = SimpleForm(
            first_name='Ryan',
            last_name='Petrello',
            csrf_enabled=False
        )
        f.validate()
        assert f.errors == {}

    def test_simple_validation_with_errors(self):
        import pecan_wtf

        class SimpleForm(pecan_wtf.form.Form):
            first_name = pecan_wtf.fields.TextField(
                "First Name",
                [pecan_wtf.validators.Required()]
            )
            last_name = pecan_wtf.fields.TextField(
                "Last Name",
                [pecan_wtf.validators.Required()]
            )

        f = SimpleForm(
            first_name='Ryan',
            csrf_enabled=False
        )
        f.validate()
        assert f.errors == {'last_name': ['This field is required.']}

    def test_csrf_validation_by_default(self):
        import pecan_wtf

        class SimpleForm(pecan_wtf.form.Form):
            first_name = pecan_wtf.fields.TextField(
                "First Name",
                [pecan_wtf.validators.Required()]
            )
            last_name = pecan_wtf.fields.TextField(
                "Last Name",
                [pecan_wtf.validators.Required()]
            )

        f = SimpleForm(
            first_name='Ryan',
            last_name='Petrello'
        )
        f.validate()
        assert f.errors == {'csrf_token': ['CSRF token missing']}


class TestFormWithErrorMarkup(TestCase):

    def test_no_errors(self):
        import pecan_wtf

        class SimpleForm(pecan_wtf.form.Form):
            first_name = pecan_wtf.fields.TextField(
                "First Name",
                [pecan_wtf.validators.Required()]
            )
            last_name = pecan_wtf.fields.TextField(
                "Last Name",
                [pecan_wtf.validators.Required()]
            )

        f = SimpleForm(
            first_name='Ryan',
            last_name='Petrello',
            csrf_enabled=False,
            error_config={
                'auto_insert_errors': True
            }
        )
        f.validate()
        assert f.errors == {}
        assert str(f.first_name) == ('<input id="first_name" '
                                     'name="first_name" type="text" '
                                     'value="Ryan">')
        assert str(f.last_name) == ('<input id="last_name" '
                                     'name="last_name" type="text" '
                                     'value="Petrello">')

    def test_simple_error(self):
        import pecan_wtf

        class SimpleForm(pecan_wtf.form.Form):
            first_name = pecan_wtf.fields.TextField(
                "First Name",
                [pecan_wtf.validators.Required()]
            )
            last_name = pecan_wtf.fields.TextField(
                "Last Name",
                [pecan_wtf.validators.Required()]
            )

        f = SimpleForm(
            first_name='Ryan',
            csrf_enabled=False,
            error_config={
                'auto_insert_errors': True
            }
        )
        f.validate()
        assert f.errors == {'last_name': ['This field is required.']}
        assert str(f.first_name) == ('<input id="first_name" '
                                     'name="first_name" type="text" '
                                     'value="Ryan">')
        assert '<span class="error-message">This field is required.</span>' \
                in str(f.last_name)

    def test_multiple_error_fields(self):
        import pecan_wtf

        class SimpleForm(pecan_wtf.form.Form):
            first_name = pecan_wtf.fields.TextField(
                "First Name",
                [pecan_wtf.validators.Required()]
            )
            last_name = pecan_wtf.fields.TextField(
                "Last Name",
                [pecan_wtf.validators.Required()]
            )

        f = SimpleForm(
            csrf_enabled=False,
            error_config={
                'auto_insert_errors': True
            }
        )
        f.validate()
        assert f.errors == {
            'first_name': ['This field is required.'],
            'last_name': ['This field is required.']
        }
        assert '<span class="error-message">This field is required.</span>' \
                in str(f.first_name)
        assert '<span class="error-message">This field is required.</span>' \
                in str(f.last_name)
