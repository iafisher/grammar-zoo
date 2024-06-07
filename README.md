`grammar-zoo` is a wrapper around different *automated grammar-checking* programs.

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
