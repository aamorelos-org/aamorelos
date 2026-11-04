def validate_slogan(value: str) -> str:
    """Valida y normaliza un slug (slogan) para URLs y claves de archivo."""
    slogan = value.strip()
    lowered = slogan.lower()

    if not slogan:
        raise ValueError("El slug no puede estar vacío")

    if "." in slogan:
        raise ValueError('El slug no puede contener "."')

    if ".web" in lowered or "webp" in lowered:
        raise ValueError('El slug no puede contener ".web" ni "webp"')

    if any(char not in "abcdefghijklmnopqrstuvwxyz0123456789_-" for char in lowered):
        raise ValueError("El slug solo puede contener minúsculas, números, guiones y guiones bajos")

    if slogan != lowered:
        raise ValueError("El slug debe estar en minúsculas")

    return slogan
