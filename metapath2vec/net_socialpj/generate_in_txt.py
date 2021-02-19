import os
from tqdm import tqdm
from config import WOS_Articles, ID_Author, ID_Journal
import time


def generate_input_func(results):
    global author_id
    global journal_id
    global journal_dict
    global author_dict
    for result in results:
        paper_id = result['num_id']
        title = result['title']
        journal = result['journal']
        authors = result['authors']
        with open("paper.txt", "a") as pid:
            pid.write(str(paper_id) + '\t' + title + '\n')

        if journal not in journal_dict:
            journal_id += 1
            journal_dict[journal] = journal_id
            with open("id_conf.txt", "a") as pid:
                pid.write(str(journal_id) + '\t' + 'v' + journal + '\n')

            with open("paper_conf.txt", "a") as pid:
                pid.write(str(paper_id) + '\t' + str(journal_id) + '\n')
        else:
            with open("paper_conf.txt", "a") as pid:
                pid.write(str(paper_id) + '\t' + str(journal_dict.get(journal)) + '\n')

        if authors != '':
            for ath in authors.split(';'):
                if ath not in author_dict:
                    author_id += 1
                    author_dict[ath] = author_id
                    with open("id_author.txt", "a") as pid:
                        pid.write(str(author_id) + '\t' + 'a' + ath + '\n')

                    with open("paper_author.txt", "a") as pid:
                        pid.write(str(paper_id) + '\t' + str(author_id) + '\n')
                else:
                    with open("paper_author.txt", "a") as pid:
                        pid.write(str(paper_id) + '\t' + str(author_dict.get(ath)) + '\n')


if __name__ == '__main__':
    author_dict = dict()
    journal_dict = dict()
    author_id = 0
    journal_id = 0

    limit = 1
    start = 0
    end = 263698
    for skip in tqdm(range(start, end)):
        print(skip)
        results = WOS_Articles.find({}, no_cursor_timeout=True).skip(skip).limit(limit)
#         print(results)
#         break
        generate_input_func(results)
    
    ID_Author.insert_one(author_dict)
    ID_Journal.insert_one(journal_dict)