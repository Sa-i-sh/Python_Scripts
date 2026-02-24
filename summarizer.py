import os
import re
import json
import nltk
import spacy
from datetime import datetime

nltk.download('punkt', quiet = True)

nlp = spacy.load("en_core_web_sm")

class MeetingSummarizer:
    def __init__(self, input_path, output_path):
        self.input_path = input_path
        self.output_path = output_path

    def read_transcript(self):
        if not os.path.exists(self.input_path):
            raise FileNotFoundError(f"Transcript not found: {self.input_path}")
        
        with open(self.input_path, "r", encoding = "utf-8") as file:
            return file.read()
        
    def clean_transcript(self, text):
        text = re.sub(r"\d{1,2}:\d{2}:\d{2}", "", text)

        text = re.sub(r"\b[A-Z][a-z]+:", "", text)

        text = re.sub(r"\s+", "", text).strip()

        return text

    def summarize(self, text, max_sentences = 5):
        sentences = nltk.sent_tokenize(text)

        if len(sentences) <= max_sentences:
            return sentences
        
        return sentences[:max_sentences]
    
    def extract_action_items(self, text):
        doc = nlp(text)
        action_items = []

        action_keywords = [
            "will","should","need to","must","assign","follow up","deadline","complete","review","going to","plan to","intend to","promise","commit to","schedule","arrange",
            "organize","prepare","set up","have to","required to","expected to","responsible for","accountable for","mandated","obligated","due by","pending","asap","implement",
            "execute","submit","deliver","update","fix","resolve","create","build","deploy","check with","get back to","reach out","coordinate","discuss","confirm","notify",
            "inform","clarify","sync","by tomorrow","by next week","end of day","eod","by friday","before","after","within","no later than","let's","can you","could you","please",
            "remind","ensure","make sure","double check"
        ]

        for sent in doc.sents:
            sentence_text = sent.text.lower()
            if any(keyword in sentence_text for keyword in action_keywords):
                action_items.append(sent.text.strip())

        return action_items
    
    def save_output(self, summary, actions):
        output_data = {
            "generated_at" : datetime.now().isoformat(),
            "summary_points" : summary,
            "actions_list" : actions
        }

        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)

        with open(self.output_path, "w", encoding="utf-8") as file:
            json.dump(output_data, file, indent=4)

    def process(self):
        raw_text = self.read_transcript()
        cleaned_text = self.clean_transcript(raw_text)
        summary = self.summarize(cleaned_text)
        actions = self.extract_action_items(cleaned_text)
        self.save_output(summary, actions)

        print("Meeting summary generated SUCCESSFULLY!!!")

if __name__ == "__main__":
    input_file = "input/meeting1.txt"
    output_file = "output/meeting1_summary.json"

    summarizer = MeetingSummarizer(input_file, output_file)
    summarizer.process()

