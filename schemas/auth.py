from pydantic import BaseModel, Field


class LoginRequestSchema(BaseModel):
    username_or_email: str = Field(
        ...,
        min_length=1,
        description="Nombre de usuario o correo electrónico",
    )
    password: str = Field(..., min_length=1, description="Contraseña en texto plano")


class TokenResponseSchema(BaseModel):
    access_token: str
    token_type: str = "bearer"
    nombre_completo: str | None = None


class LoginResponseSchema(BaseModel):
    ok: bool
    mensaje: str
    data: TokenResponseSchema
