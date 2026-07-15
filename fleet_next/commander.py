import json
import os
import subprocess
import sys


SESSION = "fleet@commander"
OPTION = "@fleet_commander_thread"
SYSTEM = """You are Fleet Commander, Will's persistent personal assistant for arranging and managing agent work.

The runner attaches a fresh `<fleet-context>` snapshot to every request. Treat it as the live source of truth. Tmux sessions are authoritative; never maintain a separate catalogue.

Be concise and conservative. Preserve spatial stability and open loops. Never fill an empty slot merely because it exists. This first implementation is read-only: propose exact changes and wait, but never execute them. Never permanently delete work.

Do not use SSH or inspect Fleet independently when answering an operational request: the attached snapshot was collected outside your sandbox. Do not edit Agent Fleet's source code or configuration unless Will explicitly changes the task from operating Fleet to developing it.

When proposing changes, identify exact source IDs and viewer slot IDs, explain any irreversible machine or agent choice, and then stop.
"""
WORKSTATIONS = ("boltzmann", "noether", "newton")


def thread():
    result = subprocess.run(
        ["tmux", "show-options", "-qv", "-t", SESSION, OPTION],
        text=True, capture_output=True)
    return result.stdout.strip()


def remember(value):
    subprocess.run(["tmux", "set-option", "-t", SESSION, OPTION, value], check=True)


def command(thread_id, prompt):
    if thread_id:
        return ["codex", "exec", "resume", "--json", "--skip-git-repo-check",
                thread_id, prompt]
    return ["codex", "exec", "--json", "--skip-git-repo-check",
            "--sandbox", "read-only",
            SYSTEM + "\nUser request:\n" + prompt]


def context():
    local = json.loads(subprocess.run(["fleet-next", "context"], text=True,
                                      capture_output=True, check=True).stdout)
    workstations = {}
    environment = {**os.environ,
                   "SSH_AUTH_SOCK": f"/run/user/{os.getuid()}/gnupg/S.gpg-agent.ssh"}
    for host in WORKSTATIONS:
        remote = json.loads(subprocess.run(
            ["ssh", "-T", "-o", "BatchMode=yes", host, "fleet-next context"],
            text=True, capture_output=True, check=True, env=environment).stdout)
        workstations[host] = {key: remote[key]
                              for key in ("profile", "unavailable", "slots")}
    return {"sessions": local["sessions"], "unavailable": local["unavailable"],
            "workstations": workstations}


def event(line):
    item = json.loads(line)
    if item["type"] == "thread.started":
        remember(item["thread_id"])
    if item["type"] != "item.completed":
        return ""
    content = item["item"]
    if content["type"] == "agent_message":
        return content["text"]
    if content["type"] == "command_execution":
        return f'[{content["command"]}]'
    return ""


def turn(prompt):
    request = prompt + "\n<fleet-context>\n" + json.dumps(context()) + "\n</fleet-context>"
    process = subprocess.Popen(command(thread(), request), cwd=os.path.expanduser("~"),
                               text=True, stdout=subprocess.PIPE)
    for line in process.stdout:
        try:
            output = event(line)
        except (KeyError, json.JSONDecodeError):
            output = line.rstrip()
        if output:
            print(output, flush=True)
    if process.wait():
        raise SystemExit(process.returncode)


def run():
    print("Fleet Commander · Codex", flush=True)
    print("commander> ", end="", flush=True)
    for line in sys.stdin:
        prompt = line.strip()
        if prompt:
            turn(prompt)
        print("commander> ", end="", flush=True)
