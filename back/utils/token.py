from itsdangerous import URLSafeTimedSerializer

SECRET_KEY = "sua_chave_secreta"
SECURITY_SALT = "recuperar-senha"

def gerar_token(email: str) -> str:
    serializer = URLSafeTimedSerializer(SECRET_KEY)
    return serializer.dumps(email, salt=SECURITY_SALT)

def validar_token(token: str, max_age=1800) -> str:
    serializer = URLSafeTimedSerializer(SECRET_KEY)
    return serializer.loads(token, salt=SECURITY_SALT, max_age=max_age)