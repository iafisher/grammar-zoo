GrammarZoo is a wrapper around different *automated grammar-checking* programs.

It lets you conveniently compare their accuracy on grammatical/ungrammatical sentences.

Install it with pip or [pipx](https://pipx.pypa.io/stable/):

```shell
$ pip install grammar-zoo
```

Usage:

```shell
# list available tools
$ grammar-zoo -l

# check a sentence
$ grammar-zoo -t languagetool 'This sentence ungrammatical.'
```

## Tools
GrammarZoo currently supports the following tools:

- [LanguageTool](https://github.com/languagetool-org/languagetool): an open-source grammar-checker
  also offered as a commercial product.
- [Vale](https://vale.sh/): "a syntax-aware linter for prose"

## Further reading
- The [Corpus of Linguistic Acceptability](https://nyu-mll.github.io/CoLA/) (CoLA) is a corpus of
  sentences marked as grammatical or ungrammatical, drawn from published linguistics papers. It is
  used to pick random sentences for the `--random` flag.
