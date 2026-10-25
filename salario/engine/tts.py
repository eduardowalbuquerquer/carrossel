"""Narração: Gemini TTS (padrão, grátis com chave do Google AI Studio, sem faturamento), Google Cloud Text-to-Speech
ou ElevenLabs. Sem chave, devolve None e o vídeo sai sem voz.

Variáveis: SO_TTS (gemini|google|elevenlabs|off), SO_GEMINI_KEY, SO_GEMINI_VOICE (ex.: Charon), SO_GEMINI_MODEL,
SO_GOOGLE_TTS_KEY, SO_GOOGLE_VOICE (ex.: pt-BR-Chirp3-HD-Charon),
ELEVENLABS_API_KEY, SO_ELEVEN_VOICE (voice_id). Cache por texto em salario/.cache_tts para não pagar duas vezes.
Docs: https://ai.google.dev/gemini-api/docs/speech-generation
      https://cloud.google.com/text-to-speech/docs/reference/rest/v1/text/synthesize
      https://elevenlabs.io/docs/api-reference/text-to-speech/convert
"""
import base64, hashlib, json, os, subprocess, urllib.error, urllib.request
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


STYLE = ("Português do Brasil, sotaque neutro. Narrador de vídeo curto de finanças: confiante, próximo e animado, "
         "ritmo ágil, ênfase nos números.")


def _gemini(text, out):
    key = _clean(os.environ.get("SO_GEMINI_KEY"))
    if not key:
        return False
    item = {"type": "text", "text": text, "speech_metadata": {"style": os.environ.get("SO_GEMINI_STYLE", STYLE)}}
    body = {"model": os.environ.get("SO_GEMINI_MODEL", "gemini-3.8-flash-tts"),
            "input": [{"type": "user_input", "content": [item]}],
            "response_format": {"type": "audio"},
            "generation_config": {"speech_config": [{"voice": os.environ.get("SO_GEMINI_VOICE", "Charon")}]}}

    def call():
        req = urllib.request.Request("https://generativelanguage.googleapis.com/v1beta/interactions", data=json.dumps(body).encode(),
                                     headers={"Content-Type": "application/json", "x-goog-api-key": key})
        with urllib.request.urlopen(req, timeout=180) as r:
            return json.loads(r.read())
    try:
        r = call()
    except urllib.error.HTTPError as e:
        if e.code != 400:
            raise
        item.pop("speech_metadata")  # se o campo de estilo for recusado, narra sem ele
        r = call()
    audio = [c for st in r.get("steps", []) if st.get("type") == "model_output" for c in st.get("content", []) if c.get("type") == "audio"]
    raw = out.with_suffix(".src.wav")
    raw.write_bytes(base64.b64decode(audio[-1]["data"]))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(raw), "-ar", "44100", "-ac", "1", str(out)], check=True)
    raw.unlink()
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
    mode = os.environ.get("SO_TTS", "gemini").lower()
    if mode == "off" or not text.strip():
        return None
    CACHE.mkdir(exist_ok=True)
    out = CACHE / (hashlib.sha1(f"{mode}|{os.environ.get('SO_GEMINI_VOICE','')}|{os.environ.get('SO_GOOGLE_VOICE','')}|{os.environ.get('SO_ELEVEN_VOICE','')}|{text}".encode()).hexdigest() + ".wav")
    if out.exists():
        return out
    ok = {"elevenlabs": _eleven, "google": _google}.get(mode, _gemini)(text, out)
    return out if ok else None


def duration(wav):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(wav)],
                       capture_output=True, text=True, check=True)
    return float(r.stdout.strip())
