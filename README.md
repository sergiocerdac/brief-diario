# Brief Diario

Podcast personal automatizado: resumen diario (~6-10 min) de noticias en tecnología, IA, startups y negocios, en español chileno.

- **Feed RSS:** https://sergiocerdac.github.io/brief-diario/feed.xml (pegar en Apple Podcasts → Seguir un programa por URL)
- `episodes/` — audios mp3 (voz `es-CL-LorenzoNeural` vía edge-tts)
- `scripts/` — transcripciones de cada episodio
- `feed.xml` — feed RSS del podcast

Cada episodio nuevo = agregar mp3 a `episodes/`, transcripción a `scripts/`, y un `<item>` nuevo al tope de `feed.xml` (actualizar `length` con el tamaño en bytes del mp3).

Generado por una rutina programada de Claude Code.
