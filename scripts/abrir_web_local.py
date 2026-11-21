"""Comprueba la instalación local y abre la web sin detener otros servidores."""
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
from urllib.error import URLError
from urllib.request import ProxyHandler, build_opener
import webbrowser

ROOT = Path(__file__).resolve().parents[1]


def main():
    os.chdir(ROOT)
    # La instalación del estudiante usa MariaDB; no cambiar silenciosamente a SQLite.
    for command in [
        ['check', '--database', 'default'],
        ['migrate', '--noinput'],
        ['shell', '-c', "from django.urls import resolve; print('Ruta web:', resolve('/web/ingresar/').url_name)"],
    ]:
        subprocess.run([sys.executable, 'manage.py', *command], check=True)
    # Otro proyecto puede ocupar 8000. No cerrarlo: elegir un puerto libre.
    port = None
    for candidate in range(8001, 8011):
        with socket.socket() as listener:
            try:
                listener.bind(('127.0.0.1', candidate))
            except OSError:
                continue
            port = candidate
            break
    if port is None:
        raise RuntimeError('Los puertos 8001 a 8010 estan ocupados. No se detuvo ningun proceso.')
    url = f'http://127.0.0.1:{port}/web/ingresar/'
    print('Abriendo la version actualizada:', url, flush=True)
    server = subprocess.Popen([sys.executable, 'manage.py', 'runserver', f'127.0.0.1:{port}', '--insecure', '--noreload'])
    try:
        opener = build_opener(ProxyHandler({}))
        for _ in range(60):
            if server.poll() is not None:
                raise RuntimeError('Django se detuvo. Revisa el error mostrado arriba.')
            try:
                with opener.open(url, timeout=1) as response:
                    ready = response.status == 200
            except (URLError, OSError):
                ready = False
            if ready:
                webbrowser.open(url)
                print('Pagina de ingreso disponible. Deja esta ventana abierta; Ctrl+C para detener.', flush=True)
                server.wait()
                return
            time.sleep(.5)
        raise RuntimeError('La pagina no respondio correctamente. Envia una captura de esta ventana.')
    except KeyboardInterrupt:
        print('\nCerrando solo el servidor iniciado por este lanzador.')
    finally:
        if server.poll() is None:
            server.terminate()
            try:
                server.wait(timeout=10)
            except subprocess.TimeoutExpired:
                server.kill()
                server.wait()


if __name__ == '__main__':
    try:
        main()
    except (RuntimeError, subprocess.CalledProcessError, OSError) as exc:
        print(f'No se pudo abrir la web: {exc}', file=sys.stderr)
        sys.exit(1)
