import os
import zipfile
import shutil
import tempfile

BASE = r'C:\Escritorio\ARCHIVOS - CUESTIONES LABORALES\rc-consorcio2025\2026'
NUEVO_LOGO = r'C:\Escritorio\ARCHIVOS - CUESTIONES LABORALES\rc-consorcio2025\LOGOS\Logo 1.jpeg'

with open(NUEVO_LOGO, 'rb') as f:
    nuevo_logo_bytes = f.read()

resultados = []

for consorcio in sorted(os.listdir(BASE)):
    abril = os.path.join(BASE, consorcio, 'Abril')
    if not os.path.isdir(abril):
        resultados.append(f'[SKIP] {consorcio}: sin carpeta Abril')
        continue

    archivos_xlsx = [f for f in os.listdir(abril) if f.endswith('.xlsx')]
    if not archivos_xlsx:
        resultados.append(f'[SKIP] {consorcio}: sin archivos xlsx en Abril')
        continue

    for nombre_xlsx in archivos_xlsx:
        ruta_xlsx = os.path.join(abril, nombre_xlsx)

        with zipfile.ZipFile(ruta_xlsx, 'r') as z:
            nombres = z.namelist()

        # Buscar imagen logo (image1.jpeg o image1.jpg)
        imagen_logo = None
        for n in nombres:
            if n in ('xl/media/image1.jpeg', 'xl/media/image1.jpg'):
                imagen_logo = n
                break

        if not imagen_logo:
            resultados.append(f'[SKIP] {consorcio}/{nombre_xlsx}: sin image1 para reemplazar')
            continue

        # Reemplazar imagen usando archivo temporal
        tmp_fd, tmp_path = tempfile.mkstemp(suffix='.xlsx')
        os.close(tmp_fd)

        try:
            with zipfile.ZipFile(ruta_xlsx, 'r') as zin, \
                 zipfile.ZipFile(tmp_path, 'w', compression=zipfile.ZIP_DEFLATED) as zout:
                for item in zin.infolist():
                    if item.filename == imagen_logo:
                        zout.writestr(item, nuevo_logo_bytes)
                    else:
                        zout.writestr(item, zin.read(item.filename))

            shutil.move(tmp_path, ruta_xlsx)
            resultados.append(f'[OK]   {consorcio}/{nombre_xlsx}: logo reemplazado ({imagen_logo})')
        except Exception as e:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            resultados.append(f'[ERR]  {consorcio}/{nombre_xlsx}: {e}')

print('\n'.join(resultados))
print(f'\nTotal procesados: {sum(1 for r in resultados if r.startswith("[OK]"))}')
print(f'Errores: {sum(1 for r in resultados if r.startswith("[ERR]"))}')
print(f'Omitidos: {sum(1 for r in resultados if r.startswith("[SKIP]"))}')
