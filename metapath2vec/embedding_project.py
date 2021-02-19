import io

a = []
b = []
out_v_venus = io.open('vecs_venus.tsv', 'w', encoding='utf-8')
out_m_venus = io.open('meta_venus.tsv', 'w', encoding='utf-8')
out_v_author = io.open('vecs_author.tsv', 'w', encoding='utf-8')
out_m_author = io.open('meta_author.tsv', 'w', encoding='utf-8')

with open("./output.txt") as f:
    for line in f:
        if line.startswith("v"):
            out_m_venus.write(line[1:].split()[0] + "\n")
            out_v_venus.write('\t'.join([str(x) for x in line.split()[1:]]) + "\n")
            # a.append(line[1:])
            # print(line[1:].split()[0])
            # # b.append(line[1:].replace(" ", '\t'))
            # b.append('\t'.join([str(x) for x in line.split()[1:]]))
            # print(b)
            # break
        if line.startswith("a"):
            out_m_author.write(line[1:].split()[0] + "\n")
            out_v_author.write('\t'.join([str(x) for x in line.split()[1:]]) + "\n")

# for word_num in range(1, vocab_size):
#   word = index_word[word_num]  # index_word:{1:"OOV", 2:"the", ……}
#   embeddings = weights[word_num]
#

out_v_venus.close()
out_m_venus.close()
out_v_author.close()
out_m_author.close()
