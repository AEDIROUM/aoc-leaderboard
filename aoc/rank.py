from math import inf


def entry_key(entry):
    return (-entry["score"], entry["name"])


def rank_entries(entries):
    entries.sort(key=entry_key)
    cur_rank = 0
    last_score = inf

    for index, entry in enumerate(entries):
        if entry["score"] != last_score:
            cur_rank = index + 1
            last_score = entry["score"]

        entry["rank"] = cur_rank
