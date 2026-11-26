"""
Sonido de interfaz.
Tema: un "pop" suave y grave al presionar teclas y acciones principales; se puede silenciar.
Elaborado por: Manuel Antonio Mayorga Mendoza, Andy Daivari Canales Reyes,
               Antonio Esteban Vargas Ramírez, Luis Xavier Aburto Mantilla.
"""

import math
import os
import struct
import tempfile
import wave

from PyQt6.QtCore import QUrl

try:
    from PyQt6.QtMultimedia import QSoundEffect
except ImportError:  # Sin QtMultimedia la app funciona igual, solo sin sonido
    QSoundEffect = None

FRECUENCIA_MUESTREO = 44100
VOLUMEN = 0.35

_efecto = None
_activo = True


def _generar_pop(ruta):
    """Escribe un clic de 45 ms: tono grave que baja de 210 a 140 Hz con caída rápida.

    Se sintetiza aquí para no depender de archivos de audio con licencia.
    """
    duracion = 0.045
    total = int(FRECUENCIA_MUESTREO * duracion)
    fase = 0.0
    muestras = []
    for i in range(total):
        t = i / FRECUENCIA_MUESTREO
        frecuencia = 140 + 70 * math.exp(-t / 0.012)        # leve caída de tono
        fase += 2 * math.pi * frecuencia / FRECUENCIA_MUESTREO
        ataque = min(1.0, t / 0.002)                          # sin chasquido al inicio
        envolvente = ataque * math.exp(-t / 0.011)
        muestras.append(int(32767 * 0.6 * envolvente * math.sin(fase)))
    with wave.open(ruta, "wb") as archivo:
        archivo.setnchannels(1)
        archivo.setsampwidth(2)
        archivo.setframerate(FRECUENCIA_MUESTREO)
        archivo.writeframes(struct.pack(f"<{total}h", *muestras))


def _efecto_cargado():
    global _efecto
    if _efecto is None and QSoundEffect is not None:
        ruta = os.path.join(tempfile.gettempdir(), "calculadora_pop.wav")
        if not os.path.exists(ruta):
            _generar_pop(ruta)
        _efecto = QSoundEffect()
        _efecto.setSource(QUrl.fromLocalFile(ruta))
        _efecto.setVolume(VOLUMEN)
    return _efecto


def activar(activo):
    global _activo
    _activo = bool(activo)


def esta_activo():
    return _activo


def reproducir():
    if not _activo:
        return
    efecto = _efecto_cargado()
    if efecto is not None:
        efecto.play()
