from jamdict import Jamdict
jam = Jamdict()

# use wildcard matching to find anything starts with 食べ and ends with る
text = '予想外'
result = jam.lookup(text)
for entry in result.entries:
    print(entry)
for char in result.chars:
    if str(char) in text:
        print([r.value for r in char.rm_groups[0].readings if r.r_type == 'ja_on' or r.r_type == 'ja_kun'])
    

# print all word entries
"""for entry in result.entries:
     print(entry.senses)

print("-" * 20)"""

# print(["; ".join(str(g) for g in sense.gloss) for entry in result.entries for sense in entry.senses ])


    # [gloss for sense.gloss in entry.senses for gloss in sense.gloss]