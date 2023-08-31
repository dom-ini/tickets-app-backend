from app.auth.crud.crud_password_reset import CRUDPasswordResetToken
from app.auth.crud.crud_user import CRUDUser
from app.auth.models import PasswordResetToken, User

user = CRUDUser(User)
password_reset_token = CRUDPasswordResetToken(PasswordResetToken)
