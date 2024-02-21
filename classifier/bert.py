from typing import List
import torch
import torch.nn as nn
from transformers import BertTokenizer, BertModel
from emoji import demojize

import warnings

LABEL_MAP = {
    "negative": 0,
    "positive": 1,
}

LABEL_MAP_IDX_TO_STR = {
    0: "negative",
    1: "positive"
}

def get_classifier_model(ckpt_path: str = None, device: str = None):
    if not device:
        device = "cuda" if torch.cuda.is_available() else "cpu"
    model = BertSentimentClassifier(
        num_classes=2,
        model_path="google-bert/bert-base-multilingual-cased",
        freeze_bert=True
    )
    if ckpt_path:
        model.load_state_dict(torch.load(ckpt_path, map_location=torch.device(device))["model_state_dict"])
    else:
        warnings.warn("")
    model.eval()
    return model


class BertLMHead(nn.Module):
    def __init__(self, input_dim, num_classes):
        super(BertLMHead, self).__init__()
        self.fc = nn.Linear(input_dim, num_classes)
        
        self.dropout = nn.Dropout(0.5)
        self.softmax = nn.Softmax(dim=1)
    
    def forward(self, x):
        logits = self.fc(self.dropout(x))
        return self.softmax(logits)

class BertSentimentClassifier(nn.Module):
    def __init__(self, num_classes: int, model_path: str, freeze_bert: bool = True):
        super(BertSentimentClassifier, self).__init__()
        self.tokenizer = BertTokenizer.from_pretrained(model_path)
        self.bert = BertModel.from_pretrained(model_path)
        self.decoder = BertLMHead(self.bert.config.hidden_size, num_classes)
                
        if freeze_bert:
            for param in self.bert.parameters():
                param.requires_grad = False

    def encode_texts(self, texts: List[str]):
        return self.tokenizer(texts, return_tensors="pt", add_special_tokens=True, padding="max_length", truncation=True, max_length=512)
    
    def forward(self, texts: torch.Tensor):
        bert_embedding = self.bert(**texts).pooler_output
        return self.decoder(bert_embedding)
    
    def predict(self, text: str):
        text = demojize(text.lower())
        encoded_text = self.tokenizer(text, return_tensors="pt", add_special_tokens=True, padding="max_length", truncation=True, max_length=512)
        predictions = self(encoded_text)
        predicted_class = torch.argmax(predictions, dim=1).squeeze(0).item()
        return LABEL_MAP_IDX_TO_STR[predicted_class]