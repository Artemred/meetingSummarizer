import google.generativeai as genai
import json
import time
import os
from load_dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ.get("GEMINI_API_TOKEN")

OUTPUT_FILE = "train.jsonl"

BATCHES_TO_GENERATE = 10

genai.configure(api_key=API_KEY)

MODEL_NAME = "models/gemini-flash-lite-latest"

generation_config = {
    "temperature": 0.7,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "application/json",
}

model = genai.GenerativeModel(
    model_name=MODEL_NAME,
    generation_config=generation_config,
)

BASE_PROMPT = """
You are a synthetic data generator for Fine-Tuning Qwen 2.5.
Your task is to generate 10 unique training examples in JSONL format based on the topic: "{topic}".

Output must be a strictly valid JSON Array: [{{}}, {{}}, ...].
Do NOT wrap the list in a dictionary or use numbered keys like "1", "2".

DATA STRUCTURE:
Each item in the list must be:
{{"messages": [{{"role": "system", "content": "SYSTEM_PROMPT"}},
{{"role": "user", "content": "INPUT_TEXT"}},
{{"role": "assistant", "content": "IDEAL_RESPONSE"}}]}}

CONSTANTS:
For "role": "system", ALWAYS use this exact text:
"You are a professional meeting assistant. Your task is to analyze the raw transcript, fix recognition errors, provide a concise summary, and extract a list of action items."

REQUIREMENTS FOR "USER" (Raw Whisper Simulation):
1. Language: English.
2. Simulate "dirty" raw Speech-to-Text output: no punctuation, mostly lowercase, run-on sentences, missing apostrophes.
3. Include filler words: "um", "uh", "like", "you know", "sort of", "i mean".
4. In 3 out of 10 examples, add Whisper hallucinations at the start or end (e.g., "Subtitles by...", "Thanks for watching", "Amara.org").
5. **CRITICAL:** Ensure the dialogue implies that participants are assigning tasks, agreeing on deadlines, or planning next steps (so there are actual Action Items to extract).
6. **NO SPEAKER LABELS OR DIARIZATION:** The input must appear as a continuous stream of text. Do NOT use prefixes like "Speaker 1:", "Alice:", or new lines to separate turns. The model must rely solely on context (e.g., "hi dave can you fix this") to identify who is being addressed.

REQUIREMENTS FOR "ASSISTANT" (Ideal Response):
1. Language: English.
2. Format the output using Markdown.
3. **Structure:**
   - First, a section **"### Summary"**: A concise paragraph (2-3 sentences) summarizing the discussion in an impersonal style.
   - Second, a section **"### Action Items"**: A bulleted list of tasks derived from the conversation.
4. If a task is assigned to a specific person (inferred from context like "hey bob can you do x"), mention the role or name if clear, otherwise use generic phrasing (e.g., "The team needs to...").
5. Completely IGNORE the "dirty" artifacts and hallucinations from the User input.
"""



TOPICS = [
    "A chaotic daily standup meeting in a software team",
    "Customer calling support about a broken coffee machine",
    "Two students discussing a difficult history exam",
    "A nervous job interview for a sales position",
    "A podcast intro that goes wrong with technical issues",
    "Discussion about budget cuts in a marketing department",
    "A grandmother trying to dictate a cooking recipe over the phone",
    "Breaking news report with bad signal from the field",
    "Ordering food at a drive-through with a bad microphone",
    "A couple arguing about where to go for vacation"
]


def generate_batch(batch_index):
    topic = TOPICS[batch_index % len(TOPICS)]

    try:
        response = model.generate_content(BASE_PROMPT.format(topic=topic))
        data_list = json.loads(response.text)
        if not isinstance(data_list, list):
            return

        with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
            for item in data_list:

                if "messages" in item:
                    f.write(json.dumps(item, ensure_ascii=False) + "\n")

    except Exception as e:
        print(e)
        time.sleep(5)


if __name__ == "__main__":
    for i in range(BATCHES_TO_GENERATE):
        generate_batch(i)
        time.sleep(2)
