# lisan

Arabic is spoken by some 400 million people and is thin on the web, so most AI infrastructure treats it as an afterthought. The first thing that goes wrong is mundane. The same word written three ways does not match itself. The same person is written six ways in Latin letters, and a search for one finds none of the others.

lisan is the layer that fixes this before the model sees the text: normalization with named profiles, light stemming, BM25 search, name matching across Arabic and Latin, transliteration, Eastern Arabic numerals, and routing signals for dialect and Arabizi. Standard library only, Python 3.10 to 3.13, typed, 88 tests.

## Use

```python
from lisan import Index, light_stem, match_names, normalize

normalize(text)                      # 0.1 behaviour: diacritics, tatweel, alef and yeh forms, Eastern digits to ASCII
normalize(text, profile="search")    # + NFKC, invisible controls, Quranic marks, Persian letters, hamza, teh marbuta, punctuation
light_stem("والمعلمون")              # "معلم"

match_names("عبد الرحمن بن راشد", "Abdulrahman bin Rashid").is_match   # True
match_names("Hassan", "Hamza").is_match                                # False

index = Index("stemmed")             # BM25 with Arabic-aware analysis
index.add("doc1", "افتتحت الجامعة مكتبة جديدة")
index.search("مكتبه جديده")[0].id    # "doc1"
```

The 0.1 API (`normalize`, `tokens`, `search_key`, `arabic_ratio`, `is_arabic_letter`) is unchanged and returns the same results.

## What is in it

| | |
|---|---|
| **Normalization** | Profiles `legacy` (exactly 0.1), `clean` (Unicode hygiene only: NFKC turns presentation forms and ligatures such as the Allah ligature and lam alef into plain letters, invisible bidirectional and zero width characters go, Quranic marks go) and `search` (also Persian and Urdu letters, hamza, teh marbuta, punctuation). Every option can be overridden by keyword. Digits convert to ASCII, Eastern Arabic or Persian. |
| **Light stemming** | Removes the definite article, clitic prefixes and plural and feminine suffixes, never a root. Affix lists follow the Larkey, Ballesteros and Connell (2002) family; the guards on minimum stem length are this library's own and are parameters. Character n grams for retrieval. |
| **Search** | `Index`: BM25 over analyzers `raw`, `normalized`, `stemmed`, `trigram`, or your own function. Deterministic ties. |
| **Name matching** | Consonant skeletons put Arabic and Latin spellings in one alphabet: digraphs (kh, sh, th, dh, gh), arabizi digits (7, 3, 5, 9 and the rest), doubled letters, bin and ibn, al and el, titles, compounds that begin with abd. Token by token alignment where the worst token sets the score, so one wrong token in a long name is not averaged away. Reports coverage for partial names and a confidence flag for very short skeletons. |
| **Transliteration** | Buckwalter, in both directions, one character for one character, and a round trip keeps the vowel marks. |
| **Numbers** | Find and read numbers written with any digit set and Arabic separators, with positions. |
| **Routing signals** | Arabic share, RTL, script runs, dialect marker words (Egyptian, Levantine, Gulf, Maghrebi), Arabizi score. |
| **CLI** | `lisan normalize`, `clean`, `tokens`, `translit`, `numbers`, `detect`, `match`. `match` exits 1 below its threshold and `detect --min-arabic` exits 1 below its share, so a pipeline can gate on them. Exit 2 is an error. |

## Command line

```
$ echo 'ﷲ أكبر، مُدَرِّسَةٌ ١٢٣٫٥' | lisan normalize --profile search
الله اكبر, مدرسه 123.5

$ echo 'والمعلمون في المدارس' | lisan tokens --stem
معلم
في
مدارس

$ echo 'مُحَمَّد' | lisan translit
muHama~d

$ lisan match 'عبد الرحمن بن راشد' 'Abdulrahman bin Rashid'
{"score": 1.0, "match": true, "coverage": 0.667, "method": "joined", "confidence": "high", "left": "bdl rhmn ršd", "right": "bdlrhmn ršd"}
exit 0

$ lisan match Hassan Hamza
{"score": 0.333, "match": false, "coverage": 1.0, "method": "aligned", "confidence": "high", "left": "hsn", "right": "hmz"}
exit 1

$ echo 'ana 7abibi w gdan وصلت دلوقتي' | lisan detect
{"arabic_ratio": 0.435, "rtl": false, "arabizi": 0.25, "dialect_hints": {"egyptian": ["دلوقتي"]}, "runs": [{"script": "latin", "text": "ana 7abibi w gdan"}, {"script": "arabic", "text": "وصلت دلوقتي"}]}
```

## Measured

`python examples/evaluate.py` runs the two fixtures in `examples/`. Both were written by hand alongside the code, so they are regression sets that pin the behaviour described here. They are not an independent estimate of accuracy on real data, and a perfect score on them would mean little by itself. What they do show is where each approach stops working, including the pairs that fail on purpose.

```
Name matching (hand-written regression set, threshold 0.85)
  same-name pairs matched      76/76
  different-name pairs merged  0/42
  known collisions (merged)    5/5: Rashid~Rashad, Omar~Amir, حسن~Hussein, Nawaf~Naif, Abdulrahman~Abdulrahim
  known misses (not matched)   2/2: Mohammed~Mohd, Yusuf~Joseph

Search, success at rank 1 (the target document is the top hit)
  analyzer       spelling variants   inflections
  raw                         9/16           0/6
  normalized                 16/16           0/6
  stemmed                    16/16           5/6
  trigram                    16/16           4/6
```

- **Spelling variation** is what breaks naive matching. With plain whitespace tokens, 7 of 16 queries miss their document because the query spells a word differently (hamza forms, teh marbuta typed as heh, diacritics, Eastern digits, Persian letters). Normalization fixes all 16.
- **Inflection** is what normalization cannot fix: 0 of 6 until the stemmer is on, then 5 of 6. The sixth is a broken plural (مدينة and مدن), which needs a root or lemma and is out of reach of any light stemmer.
- **Names**: 76 pairs of the same name (Latin to Latin, Arabic to Latin, Arabic to Arabic, arabizi) all match, 42 pairs of different names are all kept apart, at threshold 0.85.
- **Known collisions and misses are pinned in the tests**, not hidden. See below.

## Honest limits

- **Name skeletons drop vowels, so differences in vowels alone collide.** Rashid and Rashad, Omar and Amir, Nawaf and Naif, and (across scripts) Hasan and Hussein have the same skeleton. Written solid, Abdulrahman and Abdulrahim differ by one letter in seven and score 0.86. Arabic against Arabic keeps Hasan and Husayn apart because it compares letters, not skeletons. Use the score and `confidence` as a screen that feeds human review, not as an identity decision.
- **Short names are weak evidence.** A skeleton of one or two letters (Ali, Aisha) is flagged `confidence="low"` because many unrelated names look alike.
- **Name matching does not know nicknames or translations** (Yusuf and Joseph) or abbreviations (Mohammed and Mohd). Those are in the pinned misses.
- **The light stemmer strips too much** by design: عربي becomes عرب, and a verb ending in ون loses it like a plural does. It does not touch broken plurals.
- **Hamza folding and teh marbuta folding are lossy.** They exist to match, not to display. The `legacy` profile does neither.
- **Dialect hints are a lookup, not a classifier.** The word list is short and conservative, and text without any marker word says nothing about its dialect. The Arabizi score is a pattern heuristic for routing.
- **Search is small.** BM25 in pure Python over an index held in memory suits thousands of documents, not millions. Use the analyzers as a front end for a real engine at scale.
- **The Buckwalter table is the standard one**; text outside it passes through, so text that mixes Latin and Arabic only converts in one direction.

## Tests

```
python -m unittest discover -s tests -t . -v
ruff check . && mypy
```

The test files write Arabic as literal UTF-8.

MIT licensed. Built by [AndMaverick LLC](https://www.andmaverick.com).

---

**Read the thinking:** [The Language They Did Not Build For](https://blog.andmaverick.com/the-language-they-did-not-build-for?utm_source=github&utm_medium=repo&utm_campaign=lisan)

**If this is your problem.** If your data, language, or jurisdiction sits outside the assumptions of American AI infrastructure, that is work I do. Let us talk. [Begin a conversation](https://calendly.com/andmaverick?utm_source=github&utm_medium=repo&utm_campaign=lisan).
