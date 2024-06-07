import argparse
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass

import requests


def main_check(sentence: str, tool_original: str) -> None:
    tool = tool_original.lower()
    tool = ALIASES.get(tool, tool)
    f = TOOLS.get(tool)
    if f is not None:
        try:
            result = f(sentence)
        except GrammarZooNotInstalledException as e:
            eprint(f"{e} is not installed.")
        else:
            print("Grammatical: ", end="")
            if result.grammatical:
                print("yes")
            else:
                print("no")

            if result.comments:
                print()
                print("Comments:")
                for comment in result.comments:
                    print(f"  {comment}")
    else:
        eprint(
            f"{tool_original!r} is not a recognized tool. Re-run with -l to see available tools."
        )


def main_list() -> None:
    for tool in sorted(TOOLS):
        print(tool)


@dataclass
class Result:
    grammatical: bool
    comments: str


def run_language_tool(sentence: str) -> Result:
    if shutil.which("languagetool-server") is None:
        raise GrammarZooNotInstalledException("languagetool")

    # TODO: allow custom port
    port = 4356
    process = subprocess.Popen(
        ["languagetool-server", "--port", str(port), "--allow-origin"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    try:
        return hit_language_tool_api(sentence, port)
    finally:
        process.kill()


def hit_language_tool_api(sentence: str, port: int) -> Result:
    url = f"http://localhost:{port}/v2/check"
    data = {
        "language": "en-US",
        "text": sentence,
    }

    retries = 5
    while True:
        try:
            response = requests.post(url, data=data)

            # API documentation: https://languagetool.org/http-api/
            payload = response.json()
            matches = payload["matches"]
            if len(matches) == 0:
                return Result(grammatical=True, comments=[])
            else:
                return Result(grammatical=False, comments=[m["message"] for m in matches])
        except requests.exceptions.ConnectionError:
            retries -= 1
            if retries == 0:
                raise e

            time.sleep(0.5)
            continue


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


class GrammarZooException(Exception):
    pass


class GrammarZooNotInstalledException(Exception):
    pass


TOOLS = {
    "languagetool": run_language_tool,
}

ALIASES = {
    "language-tool": "languagetool",
}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # TODO: --random flag
    parser.add_argument("-t", "--tool")
    parser.add_argument("-l", "--list", action="store_true")
    parser.add_argument("words", nargs="*")
    args = parser.parse_args()

    if args.list:
        main_list()
    else:
        sentence = " ".join(args.words)
        main_check(sentence, args.tool)
