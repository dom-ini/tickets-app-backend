from wtforms import Form, TextAreaField

from app.admin_panel.widgets import CKTextAreaWidget


class BasicForm(Form):
    rich_text_area = TextAreaField(widget=CKTextAreaWidget())


def test_rich_text_area_widget_has_default_class() -> None:
    form = BasicForm()
    widget_markup = form.rich_text_area.widget(field=form.rich_text_area)
    assert 'class="ckeditor"' in widget_markup


def test_rich_text_area_widget_default_class_does_not_override_user_classes() -> None:
    form = BasicForm()
    custom_class = "some-custom-class"
    kwargs = {"class": custom_class}
    widget_markup = form.rich_text_area.widget(field=form.rich_text_area, **kwargs)
    assert f'class="{custom_class} ckeditor"' in widget_markup
