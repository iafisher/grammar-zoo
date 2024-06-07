import argparse
import json
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from typing import List

import requests


# TODO: can I pull this from pkg config?
REPO = "https://github.com/iafisher/grammar-zoo"


def main() -> None:
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


def main_check(sentence: str, tool_original: str) -> None:
    tool = tool_original.lower()
    tool = ALIASES.get(tool, tool)
    f = TOOLS.get(tool)
    if f is not None:
        try:
            result = f(sentence)
        except GrammarZooException as e:
            eprint(f"Error: {e}")
        except GrammarZooNotInstalledException as e:
            eprint(f"Error: {e} is not installed.")
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
    comments: List[str]


VALE_CONFIG = """\
MinAlertLevel = error

[*]
BasedOnStyles = Vale
"""


def run_vale(sentence: str) -> Result:
    if shutil.which("vale") is None:
        raise GrammarZooNotInstalledException("languagetool")

    with tempfile.NamedTemporaryFile() as tmp:
        # TODO: distribute vale config file with pkg instead of creating it on the fly
        tmp.write(VALE_CONFIG.encode("ascii"))
        tmp.flush()

        proc = subprocess.run(
            ["vale", "--output=JSON", "--config", tmp.name, sentence],
            check=False,
            capture_output=True,
            text=True,
        )
        payload = json.loads(proc.stdout)
        if not payload:
            return Result(grammatical=True, comments=[])
        else:
            # TODO: handle error
            try:
                comments = payload["stdin.txt"]
            except KeyError:
                raise GrammarZooException(
                    "Vale's output is missing the expected 'stdin.txt' key.\n\n"
                    + f"Please file a bug at {REPO}."
                )

            return Result(
                grammatical=False, comments=[comment["Message"] for comment in comments]
            )


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
                return Result(
                    grammatical=False, comments=[m["message"] for m in matches]
                )
        except requests.exceptions.ConnectionError as e:
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
    "vale": run_vale,
}

ALIASES = {
    "language-tool": "languagetool",
}
