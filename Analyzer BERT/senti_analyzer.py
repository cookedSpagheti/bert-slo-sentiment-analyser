# imports and global settings
from transformers import AutoTokenizer, AutoModel, BertModel, BertTokenizer
from torch import nn
import torch

import numpy as np
import pandas as pd


# Python implementation: CPython
# Python version       : 3.7.12
# IPython version      : 7.33.0
#
# numpy       : 1.21.6
# pandas      : 1.3.5
# torch       : 1.11.0
# transformers: 4.18.0


# what sentiments program detects or is BERT learned with
SENTI_NAMES = ['negative', 'neutral', 'positive']
SENTI_NAMES_SLO = ['negativnih', 'nevtralnih', 'pozitivnih']


# selecting seed and device
RANDOM_SEED = 23052022
np.random.seed(RANDOM_SEED)
torch.manual_seed(RANDOM_SEED)
DEVICE = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")


# config for tokenizer
PRE_TRAINED_MODEL_NAME = 'EMBEDDIA/sloberta'

TOKENIZER = AutoTokenizer.from_pretrained(PRE_TRAINED_MODEL_NAME) # BertTokenizer
BERT_MODEL = AutoModel.from_pretrained(PRE_TRAINED_MODEL_NAME, return_dict=False) # BertModel    # return_dict=False for transformer >= 4.x


# maximum length, probably doesn't matter
# MAX_LEN = 190     # bert_normal_model_final.bin
# MAX_LEN = 512     # bert_bigger_model_final.bin


# functions
def get_encoded_sentiment(text):
    return TOKENIZER.encode_plus(
        text,
        max_length=max_len,
        add_special_tokens=True,
        return_token_type_ids=False,
        pad_to_max_length=True,
        return_attention_mask=True,
        return_tensors='pt',
    )


def get_sentiment_evalution(text):
    encoded_text = get_encoded_sentiment(text)

    input_ids = encoded_text['input_ids'].to(DEVICE)
    attention_mask = encoded_text['attention_mask'].to(DEVICE)

    output = model(input_ids, attention_mask)
    _, prediction = torch.max(output, dim=1)

    return prediction.item()    # with out .item() it returns something like: tensor([1], device='cuda:0')


# BERT base
class SentimentClassifier(nn.Module):
    def __init__(self, n_classes):
        super(SentimentClassifier, self).__init__()
        self.bert = BERT_MODEL
        self.drop = nn.Dropout(p=0.3)
        self.out = nn.Linear(self.bert.config.hidden_size, n_classes)

    def forward(self, input_ids, attention_mask):
        _, pooled_output = self.bert(
            input_ids=input_ids,
            attention_mask=attention_mask
        )

        output = self.drop(pooled_output)
        return self.out(output)



def help_description():
    description = ""

    description += "Pomoc za program detekcije sentimenta z uporabo naucenega BERT modela\n"
    description += " -m    --mode                nacin delovanja\n"
    description += "                               statistics - oceni sestavo posredovanih podatkov in izpise analizo sentimentov\n"
    description += "                               sentiment-adding - oblikuje novo vhodno datoteko s posredovanimi podatki in oceno sentimenta\n"
    description += " -mn   --model-name          bert model za detekcijo sentimentov (zahtevana oblika: negative, neutral in positive)\n"
    description += " -ml   --max-length          najvecja dolzina text-a (default: 512, vrednost ne sme presegati 512)\n"
    description += " -i    --input               datoteka za branje podatkov\n"
    description += " -o    --output              datoteka za zapis podatkov (default: added-sentiment/input_file_name - sentiments.csv)\n"
    description += " -d    --delimiter           znak/i za ločitev podatkov v vhodni datoteki (default: \\t, samo pri nacinu sentiment-adding!)\n"
    description += " -h    --help                trenutni izpis\n"
    description += "\n"
    description += " EXAMPLE: python senti_analyzer.py -m statistics -mn models/bert_normal_model_final.bin -ml 190 -i \"some-file-with-news.txt\"\n"

    return description


# main thing
if __name__ == '__main__':
    import sys, os
    from collections import OrderedDict

    mode = None
    model_name = None
    input_file = None
    output_file = None
    custom_delimiter = "\t"
    max_len = 512


    # if no parameters are forwarded
    if len(sys.argv) == 1:
        print(help_description())
        exit(0)

    # checks all inputed arguments
    i = 1
    while i != len(sys.argv):
        if '-m' == sys.argv[i] or '--mode' == sys.argv[i]:
            mode = sys.argv[i + 1].lower()

        elif '-mn' == sys.argv[i] or '--model-name' == sys.argv[i]:
            model_name = sys.argv[i + 1]

        elif '-sn' == sys.argv[i] or '--sentiment-name' == sys.argv[i]:
            sentiment_name = sys.argv[i + 1]

        elif '-ml' == sys.argv[i] or '--max-length' == sys.argv[i]:
            max_len = int(sys.argv[i + 1])

            # current limit of BERT models
            if 512 < max_len:
                print(help_description())
                exit(0)

        elif '-i' == sys.argv[i] or '--input' == sys.argv[i]:
            input_file = sys.argv[i + 1]

        elif '-o' == sys.argv[i] or '--output' == sys.argv[i]:
            output_file = sys.argv[i + 1]

        elif '-d' == sys.argv[i] or '--delimiter' == sys.argv[i]:
            custom_delimiter = sys.argv[i + 1]

        elif '-h' == sys.argv[i] or '--help' == sys.argv[i]:
            print(help_description())
            exit(0)

        else:
            print(help_description())
            exit(0)

        i += 2


    # loads trained model (that can classify sentiment)
    model = SentimentClassifier(3)  # number of sentiment classes (negative, neutral, positive)
    model.load_state_dict(torch.load(model_name))
    model = model.to(DEVICE)


    # opens file for reading
    fd = open(input_file, 'r', encoding="utf-8")

    # only show sentiment composition of text
    if "statistics" == mode:

        # dictionary for ease of print
        senti_dictionary = {
            SENTI_NAMES_SLO[0]: 0,
            SENTI_NAMES_SLO[1]: 0,
            SENTI_NAMES_SLO[2]: 0
        }

        # reads line by line
        for current_line in fd:

            # sometimes files can have empty lines
            if current_line == "":
                continue

            # saves value sentiment
            sentiment_value = get_sentiment_evalution(current_line)

            # updates counter of received sentiment
            senti_dictionary[SENTI_NAMES_SLO[sentiment_value]] += 1

        # prints gathered values
        print("\n---------Evaluation results---------")
        for name, value in senti_dictionary.items():
            print(f" {name}: {value}")

        # gets first (biggest) number of sentiments from ordered dictionary
        sorted_value_key_pairs = sorted([(value, key) for (key, value) in senti_dictionary.items()], reverse=True)

        for v, k in sorted_value_key_pairs:
            print(f"\n Vecina novic je: {k}")
            break


    # save inputed file with sentiment evaluation
    elif "sentiment-adding" == mode:

        # checks if needs to generate "generic" name for output
        if output_file is None and mode == "sentiment-adding":
            only_file_name = input_file.split('/')[-1].split('.')[0]

            # makes directory if it doesn't exists
            if not os.path.exists("added-sentiment"):
                os.mkdir("added-sentiment")

            output_file = "added-sentiment/" + only_file_name + " - sentiments.csv"

        print(f"\n  Starting to write to \"{output_file}\"...\n")
        output_fd = open(output_file, 'w', encoding="utf-8")
        output_fd.write("content" + custom_delimiter + "sentiment")

        # reads line by line
        for current_line in fd:

            # sometimes files can have empty lines
            if current_line == "":
                continue

            # saves value sentiment
            sentiment_value = get_sentiment_evalution(current_line)

            # updates counter of received sentiment
            current_line = current_line.strip('\n')     # removes new line
            output_fd.write(current_line + custom_delimiter + SENTI_NAMES[sentiment_value] + "\n")

        output_fd.close()
        print("\n  ...done")

    fd.close()
