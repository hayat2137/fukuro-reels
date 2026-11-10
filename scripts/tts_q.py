import json, sys, wave
from pathlib import Path
from voicevox_core.blocking import Onnxruntime, OpenJtalk, Synthesizer, VoiceModelFile
BASE = Path("/home/claude/vv")
OUT = Path(sys.argv[1]); OUT.mkdir(parents=True, exist_ok=True)
LINES = json.load(open(sys.argv[2]))
MODE = sys.argv[3] if len(sys.argv) > 3 else "gen"
ort = Onnxruntime.load_once(filename=str(BASE / "voicevox_onnxruntime-linux-x64-1.23.2/lib/libvoicevox_onnxruntime.so"))
syn = Synthesizer(ort, OpenJtalk(str(BASE / "open_jtalk_dic_utf_8-1.11")))
with VoiceModelFile.open(str(BASE / "10.vvm")) as m:
    syn.load_voice_model(m)
durs = []
for i, t in enumerate(LINES, 1):
    q = syn.create_audio_query(t, 42)
    if MODE == "kana":
        print(i, q.kana); continue
    q.speed_scale = 1.15; q.pre_phoneme_length = 0.05; q.post_phoneme_length = 0.15
    p = OUT / f"{i:02d}.wav"; p.write_bytes(syn.synthesis(q, 42))
    with wave.open(str(p)) as w: d = w.getnframes() / w.getframerate()
    durs.append(d); print(i, round(d, 2), t)
if MODE != "kana":
    print("total", round(sum(durs), 2)); json.dump(durs, open(OUT / "durs.json", "w"))
