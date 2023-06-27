from app.auth.crud.password_reset import CRUDPasswordResetToken
from app.auth.crud.user import CRUDUser
from app.auth.models import PasswordResetToken, User

user = CRUDUser(User)
password_reset_token = CRUDPasswordResetToken(PasswordResetToken)
