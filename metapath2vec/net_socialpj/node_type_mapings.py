with open("./node_type_mapings.txt", "a") as f:
    with open("./id_author.txt") as adictfile:
        for line in adictfile:
            toks = line.strip().split("\t")
            if len(toks) == 2:
                f.write(toks[1] + "\t" + toks[0] + "\n")

    with open("./id_conf.txt") as cdictfile:
        for line in cdictfile:
            toks = line.strip().split("\t")
            if len(toks) == 2:
                f.write(toks[1] + "\t" + toks[0] + "\n")