from typing import Any

from markupsafe import Markup
from wtforms import Field
from wtforms.widgets import TextArea


class CKTextAreaWidget(TextArea):
    def __call__(self, field: Field, **kwargs: Any) -> Markup:
        if kwargs.get("class"):
            kwargs["class"] += " ckeditor"
        else:
            kwargs.setdefault("class", "ckeditor")
        return super().__call__(field, **kwargs)
