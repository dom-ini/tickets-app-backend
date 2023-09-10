from app.auth.crud.crud_password_reset import CRUDPasswordResetToken
from app.auth.crud.crud_user import CRUDUser
from app.auth.crud.crud_verification_token import CRUDVerificationToken
from app.auth.models import PasswordResetToken, User, VerificationToken

user = CRUDUser(User)
password_reset_token = CRUDPasswordResetToken(PasswordResetToken)
verification_token = CRUDVerificationToken(VerificationToken)
