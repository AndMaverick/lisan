# lisan

Arabic is spoken by some 400 million people and is thin on the web, so most AI infrastructure treats it as an afterthought. The first thing that goes wrong is mundane: the same word written three ways does not match itself. lisan fixes the mundane layer so search, retrieval, and model input behave. Standard library only.

## Use

```python
from lisan import arabic_ratio, normalize, search_key, tokens

normalize(text)                    # strips diacritics and tatweel, unifies alef and yeh forms, Eastern digits to ASCII
normalize(text, ta_marbuta=True)   # also folds teh marbuta to heh, for loose matching
search_key(text)                   # a canonical key for lookups and deduplication
tokens(text)                       # normalized word tokens
arabic_ratio(text)                 # share of Arabic letters, useful for routing mixed-language input
```

## Why these choices

- **Diacritics and tatweel are stripped** because users rarely type them and sources add them inconsistently, so the same name fragments across spellings.
- **Alef variants and the final yeh are unified** so a query matches its document regardless of how each was written.
- **Teh marbuta folding is opt-in.** It improves recall and costs precision, so you decide.
- **Eastern Arabic and Persian digits become ASCII**, so numbers can be compared and parsed.

The test suite writes every Arabic string as Unicode escapes, so it reads the same in any editor and terminal.

## Tests

```
python -m unittest discover -s tests -t . -v
```

MIT licensed. Built by [AndMaverick LLC](https://www.andmaverick.com).

---

**Related reading:** [The Language They Did Not Build For](https://blog.andmaverick.com/the-language-they-did-not-build-for?utm_source=github&utm_medium=repo&utm_campaign=lisan)

**If this is your problem.** If your data, language, or jurisdiction sits outside the assumptions of American AI infrastructure, that is work I do. Let us talk. [Begin a conversation](https://calendly.com/andmaverick?utm_source=github&utm_medium=repo&utm_campaign=lisan).
