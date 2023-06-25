from app.auth.crud.password_reset import CRUDPasswordResetToken
from app.auth.crud.user import CRUDUser
from app.auth.models.password_reset import PasswordResetToken
from app.auth.models.user import User

user = CRUDUser(User)
password_reset_token = CRUDPasswordResetToken(PasswordResetToken)
