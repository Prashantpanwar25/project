from transformers import pipeline
import logging
log = logging.getLogger("hotwordDetection")


class Model():
    def __init__(self):
        log.info("model loading...")
        self.classifier = pipeline("zero-shot-classification")
        log.info("model loaded")
    
    def predict(self, sentence, hotwords):
        try:
            self.output = self.classifier(sentence, hotwords, multi_label=True)
        except:
            log.info("some error at the time of prediction")
        log.info(self.output)
        predicted_hotwords = []
        for i in range(len(self.output["labels"])):
            #Set Threshold value
            if self.output["scores"][i] > 0.9:
                predicted_hotwords.append(self.output["labels"][i])
        return predicted_hotwords
