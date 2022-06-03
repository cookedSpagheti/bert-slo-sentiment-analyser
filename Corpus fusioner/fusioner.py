import pandas as pd
from os.path import exists
import sys


def shortten_sentiment(sentiment):
    if sentiment == 'negative':
        return 'neg'
    elif sentiment == 'neutral':
        return 'neu'
    elif sentiment == 'positive':
        return 'pos'


def tsv_like_file(read_file: str, comment_name: str, sentiment_name: str, output_file: str):
    file = pd.read_csv(read_file, sep='\t')

    data = file[[comment_name, sentiment_name]]
    data[sentiment_name] = data[sentiment_name].apply(shortten_sentiment)
    # data = data.loc[data[sentiment_name] != 0]

    if exists(output_file):
        data.to_csv(output_file, mode='a', index=False, header=False, sep="\t")

    else:
        with open(output_file, 'w') as f:
            f.write('words\tsentiment\n')
        data.to_csv(output_file, index=False, mode='a', header=False, sep="\t")  # poglej kako bi naredu za custom headerje


def normal_text(file_name: str, output_file: str, delimiter: str, special_form: str = None, replace_special_form_with: str = None):
    with open(file_name) as file:
        data = []
        i = -1

        for line in file:

            # negativnih je mal prevec zato jih skipnemo
            i += 1
            if i % 2 != 0:
                continue

            # if i % 7 != 0:
            #     continue

            line_split = line.split(delimiter)

            # popravi string, ce je cudno zapisan, npr na mesto presledkov so _
            if special_form is not None and replace_special_form_with is not None:
                import re
                line_split[0] = re.sub(special_form, replace_special_form_with, line_split[0])

            # zmanjsa podatke
            if line_split[-1] == 'positive':
                line_split[-1] = 'pos'
            elif line_split[-1] == 'negative':
                line_split[-1] = 'neg'
            elif line_split[-1] == 'neutral':
                line_split[-1] = 'neu'

            data.append(line_split)

        # zapisovanje podatkov v fajl
        if exists(output_file):
            with open(output_file, 'a') as f:
                for element in data:
                    f.write(element[0] + '\t' + element[1] + '\n')

        else:
            with open(output_file, 'w') as f:
                f.write('words\tsentiment\n')

                for element in data:
                    f.write(element[0] + '\t' + element[1] + '\n')


def help_description():
    description = ""

    description += "Pomoc za program shranjeve korpusov v eno datoteko\n"
    description += " -m    --mode                nacin delovanja\n"
    description += "                               special - datoteke s headerji in vec lastnosti (ponavadi loceni s tabulatorji)\n"
    description += "                               normal - datoteke s poljubnim zapisom (struktura mora biti string delimiter string) \n"
    description += " -i    --input               datoteka za branje podatkov\n"
    description += " -o    --output              datoteka za zapis podatkov (default: complete_corpus.csv)\n"
    description += " -cn   --comment-name        naslov dela headrja s podatki o besedah (samo pri special datotekah!)\n"
    description += " -sn   --sentiment-name      naslov dela headrja s podatki o sentimentu (samo pri special datotekah!)\n"
    description += " -dl   --delimiter           znak/i uporabljeni za delitev podatkov (samo pri normal datotekah!)\n"
    description += " -sf   --spec-form           za primere ko namesto presledkov v besedilu uporabljaljo drug znak/e (samo pri normal datotekah!)\n"
    description += " -rsf  --replace-spec-form   nadomesti znak/e uporabljanje pri --spec-form (default: ' ', samo pri normal datotekah!) \n"
    description += " -h    --help                trenutni izpis\n"
    description += "\n"
    description += " EXAMPLE: python fusioner.py -m special -i \"corpuses/SentiNews_paragraph-level.txt\" -cn content -sn sentiment\n"

    return description


if __name__ == '__main__':
    mode = None
    input_file = None
    output_file: str = 'complete_corpus.csv'
    comment_name = None
    sentiment_name = None
    delimiter = None
    special_form = None
    replace_special_form_with = ' '

    # ce je prazno
    if len(sys.argv) == 1:
        print(help_description())
        exit(0)

    # gremo cez inpute
    i = 1
    while i != len(sys.argv):
        if '-m' == sys.argv[i] or '--mode' == sys.argv[i]:
            mode = sys.argv[i + 1].lower()

        elif '-i' == sys.argv[i] or '--input' == sys.argv[i]:
            input_file = sys.argv[i + 1]

        elif '-o' == sys.argv[i] or '--output' == sys.argv[i]:
            output_file = sys.argv[i + 1]

        elif '-cn' == sys.argv[i] or '--comment-name' == sys.argv[i]:
            comment_name = sys.argv[i + 1]

        elif '-sn' == sys.argv[i] or '--sentiment-name' == sys.argv[i]:
            sentiment_name = sys.argv[i + 1]

        elif '-dl' == sys.argv[i] or '--delimiter' == sys.argv[i]:
            delimiter = sys.argv[i + 1]

        elif '-sf' == sys.argv[i] or '--spec-form' == sys.argv[i]:
            special_form = sys.argv[i + 1]

        elif '-rsf' == sys.argv[i] or '--replace-spec-form' == sys.argv[i]:
            replace_special_form_with = sys.argv[i + 1]

        elif '-h' == sys.argv[i] or '--help' == sys.argv[i]:
            print(help_description())
            exit(0)

        else:
            print(help_description())
            exit(0)

        i += 2

    # preveri, da je podan vsaj ena povezava
    if '' == input_file or '' == output_file:
        print("Manjka povezava do prispevka s komentarji")
        exit(0)

    # preveri izbran nacin procesiranja
    if 'special' == mode:
        if None is comment_name or None is sentiment_name:
            print(help_description())
            print("Manjka comment-name oz. sentiment-name !!!")
            exit(0)

        tsv_like_file(input_file, comment_name, sentiment_name, output_file)

    elif 'normal' == mode:
        if None is delimiter:
            print(help_description())
            print("Manjka delimiter !!!")
            exit(0)

        if None is special_form:
            normal_text(input_file, output_file, delimiter)
        else:
            normal_text(input_file, output_file, delimiter, special_form, replace_special_form_with)
