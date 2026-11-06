import json
import logging
import os
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# firebase-admin se importa de forma perezosa (dentro de las funciones)
# para que en entornos distintos de prod la aplicación arranque con normalidad
# aunque la variable FIREBASE_CREDENTIALS_JSON no exista o esté mal formada,
# y aunque la librería no esté instalada.

_REQUIRED_CREDENTIAL_FIELDS = ("type", "project_id", "private_key", "client_email")

EVENTOS_TOPIC = "eventos"
REFLEXIONES_TOPIC = "reflexiones"


class FirebaseNotificationError(Exception):
    """No se pudo enviar la notificación a Firebase."""


class FirebaseNotificationService:
    """Soporte de notificaciones FCM inicializado con la cuenta de servicio.

    La cuenta de servicio se lee desde la variable de entorno
    FIREBASE_CREDENTIALS_JSON (contenido JSON completo en texto).
    """

    def __init__(self, credentials_json: str):
        if not credentials_json or not str(credentials_json).strip():
            raise RuntimeError(
                "FIREBASE_CREDENTIALS_JSON es obligatorio cuando APP_ENV=prod "
                "pero está vacía o ausente"
            )

        try:
            parsed = json.loads(credentials_json)
        except (json.JSONDecodeError, TypeError) as exc:
            raise RuntimeError(
                "FIREBASE_CREDENTIALS_JSON está malformado: no es un JSON válido"
            ) from exc

        # Tolera doble-codificación: {"\"type\": ...}" parseado como str.
        if isinstance(parsed, str):
            try:
                parsed = json.loads(parsed)
            except (json.JSONDecodeError, TypeError) as exc:
                raise RuntimeError(
                    "FIREBASE_CREDENTIALS_JSON está malformado: no es un JSON válido"
                ) from exc

        if not isinstance(parsed, dict):
            raise RuntimeError(
                "FIREBASE_CREDENTIALS_JSON está malformado: debe ser un objeto JSON "
                "de cuenta de servicio"
            )

        missing = [field for field in _REQUIRED_CREDENTIAL_FIELDS if not parsed.get(field)]
        if missing:
            raise RuntimeError(
                "FIREBASE_CREDENTIALS_JSON está malformado: faltan campos "
                f"obligatorios ({', '.join(missing)})"
            )

        if parsed.get("type") != "service_account":
            raise RuntimeError(
                "FIREBASE_CREDENTIALS_JSON está malformado: "
                "el campo 'type' debe ser 'service_account'"
            )

        try:
            import firebase_admin
            from firebase_admin import credentials
        except ImportError as exc:
            raise RuntimeError(
                "firebase-admin no está instalado; es obligatorio en APP_ENV=prod"
            ) from exc

        try:
            cred = credentials.Certificate(parsed)
            app_name = "firebase-notifications"
            try:
                app = firebase_admin.get_app(app_name)
            except ValueError:
                app = firebase_admin.initialize_app(cred, name=app_name)
        except RuntimeError:
            raise
        except Exception as exc:
            raise RuntimeError(
                "FIREBASE_CREDENTIALS_JSON está malformado o no pudo usarse "
                f"para inicializar Firebase: {exc}"
            ) from exc

        self._app = app
        self._messaging_module = None  # se resuelve perezosamente

    def _messaging(self):
        if self._messaging_module is None:
            try:
                from firebase_admin import messaging
            except ImportError as exc:
                raise RuntimeError(
                    "firebase-admin no está instalado; es obligatorio en APP_ENV=prod"
                ) from exc
            self._messaging_module = messaging
        return self._messaging_module

    def send_notification(
        self,
        token: str,
        title: str,
        body: str,
        data: Optional[Dict[str, str]] = None,
    ) -> str:
        """Envía una notificación push a un único token FCM.

        Devuelve el ID del mensaje enviado.
        """
        if not token or not str(token).strip():
            raise ValueError("El token FCM no puede estar vacío")
        if not title or not str(title).strip():
            raise ValueError("El título no puede estar vacío")

        messaging = self._messaging()
        message = messaging.Message(
            data={k: str(v) for k, v in (data or {}).items()},
            notification=messaging.Notification(title=title, body=body),
            token=token.strip(),
        )
        try:
            return messaging.send(message, app=self._app)
        except Exception as exc:
            logger.exception("No se pudo enviar la notificación FCM")
            raise FirebaseNotificationError(
                "No se pudo enviar la notificación a Firebase"
            ) from exc

    def send_multicast(
        self,
        tokens: List[str],
        title: str,
        body: str,
        data: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Envía la misma notificación a varios tokens FCM.

        Devuelve el BatchResponse de Firebase (success_count, failure_count, responses).
        """
        cleaned = [str(t).strip() for t in (tokens or []) if t and str(t).strip()]
        if not cleaned:
            raise ValueError("Debe indicarse al menos un token FCM válido")
        if len(cleaned) > 500:
            raise ValueError("FCM permite como máximo 500 tokens por multicast")

        messaging = self._messaging()
        message = messaging.MulticastMessage(
            data={k: str(v) for k, v in (data or {}).items()},
            notification=messaging.Notification(title=title, body=body),
            tokens=cleaned,
        )
        try:
            return messaging.send_multicast(message, app=self._app)
        except Exception as exc:
            logger.exception("No se pudo enviar la notificación multicast FCM")
            raise FirebaseNotificationError(
                "No se pudo enviar la notificación a Firebase"
            ) from exc

    def send_topic(
        self,
        topic: str,
        title: str,
        body: str,
        data: Optional[Dict[str, str]] = None,
    ) -> str:
        """Envía una notificación push a un topic FCM.

        Devuelve el ID del mensaje enviado.
        """
        if not topic or not str(topic).strip():
            raise ValueError("El topic FCM no puede estar vacío")

        messaging = self._messaging()
        message = messaging.Message(
            data={k: str(v) for k, v in (data or {}).items()},
            notification=messaging.Notification(title=title, body=body),
            topic=topic.strip(),
        )
        try:
            return messaging.send(message, app=self._app)
        except Exception as exc:
            logger.exception("No se pudo enviar la notificación FCM al topic %s", topic)
            raise FirebaseNotificationError(
                "No se pudo enviar la notificación a Firebase"
            ) from exc


def _is_prod_env() -> bool:
    """True solo cuando el entorno es prod.

    Se considera la variable canónica APP_ENV (expuesta en
    config.settings.app_env). Como compatibilidad también se acepta
    APP_EN (solicitado literalmente), por si el despliegue la define
    con ese nombre.
    """
    try:
        from config import settings

        if str(settings.app_env or "").strip().lower() == "prod":
            return True
    except Exception:
        pass
    return str(os.getenv("APP_EN") or "").strip().lower() == "prod"


_service_instance: Optional[FirebaseNotificationService] = None


def get_firebase_notification_service() -> Optional[FirebaseNotificationService]:
    """Devuelve el servicio de notificaciones Firebase o None si no está en prod.

    - Si APP_ENV (o APP_EN) no es "prod": retorna None y la app levanta normal,
      sin importar firebase-admin ni validar FIREBASE_CREDENTIALS_JSON.
    - Si es "prod":
        * si FIREBASE_CREDENTIALS_JSON falta o está vacía -> RuntimeError
        * si está malformada (JSON inválido o campos de cuenta de servicio
          ausentes) -> RuntimeError
        * si es válida -> FirebaseNotificationService inicializado
    """
    global _service_instance

    if not _is_prod_env():
        return None

    if _service_instance is not None:
        return _service_instance

    # Se importa aquí para no acoplar el arranque en dev a la config.
    from config import settings

    credentials_json = settings.firebase_credentials_json
    if credentials_json is None:
        credentials_json = os.getenv("FIREBASE_CREDENTIALS_JSON")

    # FirebaseNotificationService lanza RuntimeError si falta/malformado.
    _service_instance = FirebaseNotificationService(credentials_json or "")
    logger.info("Firebase inicializado para notificaciones (APP_ENV=prod)")
    return _service_instance
