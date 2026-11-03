"""Crea un usuario nuevo en la base de datos de la API.

Uso:
    python scripts/create_user.py --username demo --email demo@ejemplo.com
    python scripts/create_user.py --username demo --email demo@ejemplo.com --nombre "Demo"
    python scripts/create_user.py --username demo --email demo@ejemplo.com --inactivo
"""

import argparse
import getpass
import sys
from pathlib import Path

# Permite ejecutar el script con `python scripts/create_user.py` desde cualquier
# directorio sin depender de PYTHONPATH.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from database.database import SessionLocal  # noqa: E402
from repositories.usuario_repository import UsuarioRepository  # noqa: E402
from services.usuario_service import (  # noqa: E402
    InvalidUserDataError,
    NewUser,
    UserAlreadyExistsError,
    UsuarioService,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Crea un usuario para iniciar sesión en la API.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--username", required=True, help="Nombre de usuario único")
    parser.add_argument("--email", required=True, help="Correo electrónico único")
    parser.add_argument("--nombre", default=None, help="Nombre completo del usuario")
    parser.add_argument(
        "--password",
        default=None,
        help=(
            "Contraseña. Si se omite, se solicita de forma segura. "
            "Evita usarla en entornos compartidos porque queda en el historial."
        ),
    )
    parser.add_argument(
        "--inactivo",
        action="store_true",
        help="Crea el usuario con activo = FALSE",
    )
    return parser


def read_password() -> str:
    password = getpass.getpass("Contraseña: ")
    confirmation = getpass.getpass("Confirmar contraseña: ")
    if password != confirmation:
        raise ValueError("Las contraseñas no coinciden")
    return password


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        password = args.password or read_password()
        db = SessionLocal()
        try:
            service = UsuarioService(UsuarioRepository(db))
            usuario = service.create_user(
                NewUser(
                    username=args.username,
                    email=args.email,
                    password=password,
                    nombre_completo=args.nombre,
                    activo=not args.inactivo,
                )
            )
            created = {
                "id": usuario.id,
                "username": usuario.username,
                "email": usuario.email,
                "activo": usuario.activo,
            }
        finally:
            db.close()

        print("Usuario creado correctamente:")
        print(f"  id:       {created['id']}")
        print(f"  username: {created['username']}")
        print(f"  email:    {created['email']}")
        print(f"  activo:   {created['activo']}")
        return 0

    except (InvalidUserDataError, UserAlreadyExistsError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
