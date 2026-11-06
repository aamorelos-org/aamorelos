import argparse
import os
import re
from pathlib import Path

from dotenv import load_dotenv
import psycopg2

# Cargar las variables del archivo .env
load_dotenv()

# Diccionario para convertir el mes en texto a número
MESES = {
    'ENERO': '01',
    'FEBRERO': '02',
    'MARZO': '03',
    'ABRIL': '04',
    'MAYO': '05',
    'JUNIO': '06',
    'JULIO': '07',
    'AGOSTO': '08',
    'SEPTIEMBRE': '09',
    'OCTUBRE': '10',
    'NOVIEMBRE': '11',
    'DICIEMBRE': '12',
}

# Split anclado a inicio y fin de linea: solo corta ante una linea completa
# del tipo "1 de ENERO". Sin el ancla, "10 de ENERO" se partia en "1" + "0 de ENERO".
PATRON_FECHA = r'(?m)(?=^\d{1,2}\s+de\s+[A-ZÁÉÍÓÚÑ]+\s*$)'

PATRON_FECHA_LINEA = re.compile(r'^(\d{1,2})\s+de\s+([A-ZÁÉÍÓÚÑ]+)$')
PATRON_FECHA_MMDD = re.compile(r'^\d{2}-\d{2}$')

PATRON_CITA = re.compile(
    r'^\*?\s*(A\.A\. |ALCOHÓLICOS|ALCOHOLICOS|COMO LO VE BILL|DOCE PASOS|EL DR\. BOB|DR\. BOB|LO MEJOR DE BILL|EL LENGUAJE DEL CORAZÓN|LENGUAJE DEL CORAZÓN|LA TRADICIÓN DE A\.A\.|LA TRADICIÓN DE AA|LAS DOCE TRADICIONES ILUSTRADAS|LO MEJOR DEL GRAPEVINE|VIVIENDO SOBRIO|COMPRENDIENDO EL ANONIMATO).*p[.,]?\s*\d+',
    re.IGNORECASE,
)


def convertir_fecha(fecha_str):
  """Convierte '1 de ENERO' a '01-01'. Lanza ValueError si no es valida."""
  fecha_str = fecha_str.strip()
  m = PATRON_FECHA_LINEA.match(fecha_str)
  if not m:
    raise ValueError(f'Fecha con formato invalido: {fecha_str!r} (se esperaba "1 de ENERO")')
  dia = int(m.group(1))
  mes_nombre = m.group(2).upper()
  if not 1 <= dia <= 31:
    raise ValueError(f'Dia invalido en {fecha_str!r}')
  mes = MESES.get(mes_nombre)
  if mes is None:
    raise ValueError(f'Mes desconocido en {fecha_str!r}')
  return f'{mes}-{dia:02d}'  # Formato MM-DD


def es_cita(linea):
  """Indica si la linea es la cita de una reflexion.

  Solo cuenta si empieza con la fuente y trae "p. N" (acepta "p, 59" y "p 97").
  Evita falsos positivos cuando el texto menciona "alcoholicos" sin ser la cita.
  """
  return bool(PATRON_CITA.search(linea.strip()))


def parse_reflexiones(contenido_total):
  """Parsea el texto en registros listos para insertar.

  Devuelve (registros, omitidas, descartadas):
    - registros: lista de dicts {fecha, titulo, texto, cita, contenido}
    - omitidas: bloques con fecha valida pero sin linea de cita detectada
    - descartadas: bloques incompletos o con fecha invalida
  """
  registros = []
  omitidas = []
  descartadas = []

  bloques = re.split(PATRON_FECHA, contenido_total)

  for bloque in bloques:
    if not bloque.strip():
      continue

    lineas = [l.strip() for l in bloque.strip().split('\n') if l.strip()]

    if len(lineas) < 4:
      descartadas.append(lineas)
      continue

    # 1. Fecha (Linea 1)
    try:
      fecha = convertir_fecha(lineas[0])
    except ValueError as error:
      print(f'Descartada: {error}')
      descartadas.append(lineas)
      continue

    # 2. Titulo (Linea 2)
    titulo = lineas[1].strip('"«» ')

    # Ultima coincidencia: el contenido puede citar la fuente entre parentesis.
    candidatos = [idx for idx, linea in enumerate(lineas) if es_cita(linea)]
    indice_cita = candidatos[-1] if candidatos else -1

    if indice_cita == -1:
      print(f'Omitida (sin cita): {fecha} | {titulo}')
      omitidas.append((fecha, titulo))
      continue

    cita = lineas[indice_cita].strip()

    # 3. Texto (desde la linea 3 hasta justo antes de la cita)
    texto = ' '.join(lineas[2:indice_cita]).strip()

    # 4. Contenido (todo lo que esta despues de la cita)
    contenido = ' '.join(lineas[indice_cita + 1 :]).strip()

    if not fecha or not PATRON_FECHA_MMDD.match(fecha) or not titulo or not texto or not cita or not contenido:
      print(f'Descartada (campos vacios): {fecha} | {titulo}')
      descartadas.append(lineas)
      continue

    registros.append({
        'fecha': fecha,
        'titulo': titulo,
        'texto': texto,
        'cita': cita,
        'contenido': contenido,
    })

  return registros, omitidas, descartadas


def procesar_texto_reflexiones(contenido_total, db_config, batch_size=50):
  registros, omitidas, descartadas = parse_reflexiones(contenido_total)
  print(
      f'Parseo: {len(registros)} OK, {len(omitidas)} sin cita, '
      f'{len(descartadas)} descartadas.'
  )

  if not registros:
    print('Sin registros validos; no se toca la base de datos.')
    return

  # Conexion a PostgreSQL utilizando las credenciales leidas del .env
  try:
    conn = psycopg2.connect(**db_config)
    cur = conn.cursor()
    print('¡Conexion a la base de datos exitosa!\n')
  except Exception as e:
    print(f'Error al conectar a la base de datos: {e}')
    return

  insert_query = """
        INSERT INTO public.reflexiones_diarias (fecha, titulo, texto, cita, contenido)
        VALUES (%s, %s, %s, %s, %s)
    """

  contador = 0
  try:
    for registro in registros:
      try:
        # Idempotente: si la fecha ya existe se reemplaza (no hay UNIQUE en fecha).
        cur.execute(
            'DELETE FROM public.reflexiones_diarias WHERE fecha = %s',
            (registro['fecha'],),
        )
        cur.execute(
            insert_query,
            (registro['fecha'], registro['titulo'], registro['texto'],
             registro['cita'], registro['contenido']),
        )
        contador += 1
        print(f'-> Insertado correctamente: {registro["fecha"]} | {registro["titulo"]}')
        if contador % batch_size == 0:
          conn.commit()
      except Exception as e:
        print(f'Error al insertar {registro["fecha"]}: {e}')
        conn.rollback()
    conn.commit()
  finally:
    cur.close()
    conn.close()

  print(f'\nProceso finalizado. Se insertaron {contador} reflexiones en total.')


def main():
  parser = argparse.ArgumentParser(description='Carga masiva de reflexiones_diarias desde un TXT.')
  parser.add_argument(
      '--file',
      default=str(Path(__file__).resolve().parent / 'reflexiones.txt'),
      help='Ruta del archivo TXT con las reflexiones',
  )
  parser.add_argument(
      '--batch-size',
      type=int,
      default=50,
      help='Commits intermedios cada N registros',
  )
  parser.add_argument(
      '--dry-run',
      action='store_true',
      help='Solo parsea e imprime el conteo, sin tocar la base de datos',
  )
  args = parser.parse_args()

  nombre_archivo = args.file

  if os.path.exists(nombre_archivo):
    print(f'Leyendo el archivo "{nombre_archivo}"...')
    with open(nombre_archivo, 'r', encoding='utf-8') as f:
      contenido_archivo = f.read()

    if args.dry_run:
      registros, omitidas, descartadas = parse_reflexiones(contenido_archivo)
      print(
          f'[DRY-RUN] Parseo: {len(registros)} OK, {len(omitidas)} sin cita, '
          f'{len(descartadas)} descartadas.'
      )
      for registro in registros[:5]:
        print(f'  -> {registro["fecha"]} | {registro["titulo"]}')
    else:
      db_config = {
          'dbname': os.getenv('DB_NAME'),
          'user': os.getenv('DB_USER'),
          'password': os.getenv('DB_PASSWORD'),
          'host': os.getenv('DB_HOST'),
          'port': os.getenv('DB_PORT'),
      }
      procesar_texto_reflexiones(contenido_archivo, db_config, batch_size=args.batch_size)
  else:
    print(
        f'Error: No se encontró el archivo "{nombre_archivo}" en el directorio.'
    )


if __name__ == '__main__':
  main()
