#!/usr/bin/env python3
"""Genera audio (edge-tts) y actualiza feed.xml para todo guion sin episodio.

Corre en GitHub Actions: por cada scripts/YYYY-MM-DD.txt sin su
episodes/YYYY-MM-DD.mp3, sintetiza el audio con la voz Lorenzo, calcula
tamano y duracion, e inserta el <item> al tope del feed.
"""
import glob
import os
import re
import subprocess
import sys
from datetime import date

BASE_URL = "https://sergiocerdac.github.io/brief-diario"
VOICE = "es-CL-LorenzoNeural"
RATE = "-5%"
DIAS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
         "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
DIAS_RFC = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
MESES_RFC = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def mp3_duration_seconds(path):
    try:
        from mutagen.mp3 import MP3
        return int(MP3(path).info.length)
    except Exception:
        return os.path.getsize(path) // 6000


def build_item(d, mp3_path, desc):
    dt = date.fromisoformat(d)
    dia = DIAS[dt.weekday()]
    titulo = f"Brief del {dia} {dt.day} de {MESES[dt.month - 1]} de {dt.year}"
    # 07:00 hora de Chile aprox; el offset exacto no afecta el orden del feed
    pub = f"{DIAS_RFC[dt.weekday()]}, {dt.day:02d} {MESES_RFC[dt.month - 1]} {dt.year} 07:00:00 -0400"
    size = os.path.getsize(mp3_path)
    dur = mp3_duration_seconds(mp3_path)
    return f"""    <item>
      <title>{titulo}</title>
      <description>{desc}</description>
      <pubDate>{pub}</pubDate>
      <guid isPermaLink="false">brief-{d}</guid>
      <enclosure url="{BASE_URL}/episodes/{d}.mp3" length="{size}" type="audio/mpeg"/>
      <itunes:duration>{dur}</itunes:duration>
    </item>
"""


def main():
    generated = []
    for script in sorted(glob.glob("scripts/????-??-??.txt")):
        d = os.path.basename(script)[:-4]
        mp3 = f"episodes/{d}.mp3"
        if os.path.exists(mp3):
            continue
        print(f"Generando {mp3} ...")
        subprocess.run([sys.executable, "-m", "edge_tts", "--voice", VOICE,
                        f"--rate={RATE}", "--file", script, "--write-media", mp3],
                       check=True)
        if os.path.getsize(mp3) < 200_000:
            raise SystemExit(f"mp3 sospechosamente chico: {mp3}")
        desc_file = f"scripts/{d}.desc.txt"
        if os.path.exists(desc_file):
            desc = open(desc_file, encoding="utf-8").read().strip()
        else:
            desc = "Brief diario de noticias de tecnología, startups y negocios."
        desc = desc.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        with open("feed.xml", encoding="utf-8") as f:
            feed = f.read()
        item = build_item(d, mp3, desc)
        if f"brief-{d}" in feed:
            continue
        m = re.search(r"^    <item>", feed, re.M)
        pos = m.start() if m else feed.index("  </channel>")
        feed = feed[:pos] + item + feed[pos:]
        with open("feed.xml", "w", encoding="utf-8") as f:
            f.write(feed)
        generated.append(d)
    print(f"Episodios generados: {generated or 'ninguno'}")


if __name__ == "__main__":
    main()
