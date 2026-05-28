import os
import requests
import json
from logging import getLogger, basicConfig, INFO
from dotenv import load_dotenv
from shared.csv.utils import get_words

load_dotenv()
Logger = getLogger(__name__)

OUTPUT_DIR = os.getenv("TTS_OUTPUT_FOLDER", "/output")
VOICEVOX_URL = "http://127.0.0.1:50021"
SPEAKER_ID = 1


def main():
    basicConfig(level=INFO)

    if not os.path.exists(OUTPUT_DIR):
        os.mkdir(OUTPUT_DIR)

    words = get_words()

    with requests.Session() as session:
        for word in words[:10]:
            w = word[0]
            reading = word[2]

            fn = os.path.join(OUTPUT_DIR, f"{w}.wav")

            if os.path.exists(fn):
                continue

            try:
                query_params = {"text": w + " (" + reading + ")", "speaker": SPEAKER_ID}
                query_res = session.post(
                    f"{VOICEVOX_URL}/audio_query", params=query_params, timeout=10
                )
                query_res.raise_for_status()
                query_data = query_res.json()

                query_data["speedScale"] = 0.8

                synth_res = session.post(
                    f"{VOICEVOX_URL}/synthesis",
                    params={"speaker": SPEAKER_ID},
                    data=json.dumps(query_data),
                    timeout=30,
                )
                synth_res.raise_for_status()

                with open(fn, "wb") as f:
                    f.write(synth_res.content)

                Logger.info(f"Processed: {w}")

            except Exception as e:
                Logger.error(f"Error processing {w}: {e}")


if __name__ == "__main__":
    main()
