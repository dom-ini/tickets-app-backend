from pydantic import BaseModel


class VerificationTokenBase(BaseModel):
    user_id: int


class VerificationTokenCreate(VerificationTokenBase):
    pass
