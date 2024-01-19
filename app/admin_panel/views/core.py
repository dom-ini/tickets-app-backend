from typing import Any, Iterable

from fastapi.requests import Request
from sqladmin import ModelView


class FileModelView(ModelView):
    FILE_FIELDS: Iterable[str] = ()

    async def update_model(self, request: Request, pk: str, data: dict) -> Any:
        for key in self.FILE_FIELDS:
            if key in data and data[key].file is None:
                del data[key]
        return await super().update_model(request=request, pk=pk, data=data)
