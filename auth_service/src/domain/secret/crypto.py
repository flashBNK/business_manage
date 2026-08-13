from passlib.context import CryptContext

context = CryptContext(schemes=["argon2"], deprecated="auto" )