"""Narração: Google Cloud Text-to-Speech (padrão) ou ElevenLabs. Sem chave, devolve None e o vídeo sai sem voz.

Variáveis: SO_TTS (google|elevenlabs|off), SO_GOOGLE_TTS_KEY, SO_GOOGLE_VOICE (ex.: pt-BR-Chirp3-HD-Charon),
ELEVENLABS_API_KEY, SO_ELEVEN_VOICE (voice_id). Cache por texto em salario/.cache_tts para não pagar duas vezes.
Docs: https://cloud.google.com/text-to-speech/docs/reference/rest/v1/text/synthesize
      https://elevenlabs.io/docs/api-reference/text-to-speech/convert
"""
import base64, hashlib, json, os, subprocess, urllib.request
from pathlib import Path

CACHE = Path(__file__).resolve().parents[1] / ".cache_tts"


def _clean(v):
    return (v or "").strip().strip("<>\"'").strip()


def _google(text, out):
    key = _clean(os.environ.get("SO_GOOGLE_TTS_KEY"))
    if not key:
        return False
    voice = os.environ.get("SO_GOOGLE_VOICE", "pt-BR-Chirp3-HD-Charon")
    body = {"input": {"text": text}, "voice": {"languageCode": "pt-BR", "name": voice},
            "audioConfig": {"audioEncoding": "LINEAR16", "sampleRateHertz": 44100}}
    req = urllib.request.Request(f"https://texttospeech.googleapis.com/v1/text:synthesize?key={key}",
                                 data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        out.write_bytes(base64.b64decode(json.loads(r.read())["audioContent"]))
    return True


def _eleven(text, out):
    key = _clean(os.environ.get("ELEVENLABS_API_KEY"))
    voice = os.environ.get("SO_ELEVEN_VOICE", "")
    if not key or not voice:
        return False
    body = {"text": text, "model_id": os.environ.get("SO_ELEVEN_MODEL", "eleven_multilingual_v2"),
            "voice_settings": {"stability": 0.45, "similarity_boost": 0.8, "style": 0.25}}
    req = urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{voice}?output_format=mp3_44100_128",
                                 data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json", "xi-api-key": key})
    mp3 = out.with_suffix(".mp3")
    with urllib.request.urlopen(req, timeout=120) as r:
        mp3.write_bytes(r.read())
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(mp3), "-ar", "44100", "-ac", "1", str(out)], check=True)
    return True


def speak(text):
    """Gera WAV mono 44,1 kHz para o texto e devolve o caminho (ou None se não houver voz configurada)."""
    mode = os.environ.get("SO_TTS", "google").lower()
    if mode == "off" or not text.strip():
        return None
    CACHE.mkdir(exist_ok=True)
    out = CACHE / (hashlib.sha1(f"{mode}|{os.environ.get('SO_GOOGLE_VOICE','')}|{os.environ.get('SO_ELEVEN_VOICE','')}|{text}".encode()).hexdigest() + ".wav")
    if out.exists():
        return out
    ok = _eleven(text, out) if mode == "elevenlabs" else _google(text, out)
    return out if ok else None


def duration(wav):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(wav)],
                       capture_output=True, text=True, check=True)
    return float(r.stdout.strip())
