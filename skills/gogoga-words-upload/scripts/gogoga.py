#!/usr/bin/env python3
"""
gogoga: sign in to a gogoga server and upload what a gogoga-words skill made. Python 3.10+, standard
library only.

  gogoga.py login                     sign in from this terminal (opens the browser to confirm a code)
  gogoga.py whoami
  gogoga.py logout
  gogoga.py upload MANIFEST.json --type mindmap [--preview page.png ...] [--collection pear]
  gogoga.py list                      your uploads
  gogoga.py delete ID

The server is https://words.gogoga.top unless GOGOGA_SERVER says otherwise. The sign-in is kept in
~/.config/gogoga/credentials.json (readable only by you); GOGOGA_TOKEN overrides it.
"""
from __future__ import annotations

import argparse
import base64
import getpass
import json
import os
import platform
import socket
import sys
import time
import urllib.error
import urllib.request
import webbrowser
from pathlib import Path

DEFAULT_SERVER = "https://words.gogoga.top"
CREDENTIALS = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "gogoga" / "credentials.json"
TYPES = ["mindmap", "cards", "read-along", "practice", "games", "roleplay", "story", "phonics"]
UA = "gogoga-cli/1.0"


def fail(message: str) -> None:
    print(f"gogoga: {message}", file=sys.stderr)
    sys.exit(1)


def server() -> str:
    return os.environ.get("GOGOGA_SERVER", "").rstrip("/") or saved().get("server") or DEFAULT_SERVER


def saved() -> dict:
    try:
        return json.loads(CREDENTIALS.read_text())
    except (OSError, ValueError):
        return {}


def token() -> str:
    value = os.environ.get("GOGOGA_TOKEN", "").strip() or saved().get("token", "")
    if not value:
        fail("not signed in: run `gogoga.py login` first")
    return value


def request(method: str, path: str, body: dict | None = None, auth: bool = True, base: str | None = None) -> tuple[int, dict]:
    headers = {"User-Agent": UA, "Accept": "application/json"}
    data = None
    if body is not None:
        data = json.dumps(body).encode()
        headers["Content-Type"] = "application/json"
    if auth:
        headers["Authorization"] = f"Bearer {token()}"
    req = urllib.request.Request(f"{base or server()}{path}", data=data, method=method, headers=headers)
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=300) as response:
                return response.status, json.loads(response.read() or b"{}")
        except urllib.error.HTTPError as error:
            try:
                return error.code, json.loads(error.read() or b"{}")
            except ValueError:
                return error.code, {"error": f"HTTP {error.code}"}
        except (urllib.error.URLError, ConnectionError, TimeoutError) as error:
            if attempt == 2:
                fail(f"cannot reach {base or server()}: {error}")
            time.sleep(2 * (attempt + 1))
    return 0, {}


def cmd_login(args) -> None:
    base = (args.server or os.environ.get("GOGOGA_SERVER") or DEFAULT_SERVER).rstrip("/")
    name = f"{getpass.getuser()}@{socket.gethostname()} ({platform.system()})"
    status, start = request("POST", "/api/auth/device", {"name": name}, auth=False, base=base)
    if status != 200:
        fail(start.get("error", f"could not start sign-in (HTTP {status})"))
    print(f"Open {start['verification_uri']} and confirm the code:\n\n    {start['user_code']}\n")
    if not args.no_browser:
        webbrowser.open(start["verification_uri_complete"])
    interval = int(start.get("interval", 5))
    deadline = time.time() + int(start.get("expires_in", 600))
    print("Waiting for confirmation in the browser…", flush=True)
    while time.time() < deadline:
        time.sleep(interval)
        status, result = request("POST", "/api/auth/device/token", {"device_code": start["device_code"]}, auth=False, base=base)
        if status == 200:
            CREDENTIALS.parent.mkdir(parents=True, exist_ok=True)
            # Create it private before writing the token into it.
            fd = os.open(CREDENTIALS, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
            with os.fdopen(fd, "w") as file:
                json.dump({"server": base, "token": result["access_token"], "email": result["user"]["email"]}, file)
            os.chmod(CREDENTIALS, 0o600)
            print(f"Signed in to {base} as {result['user']['email']}.")
            return
        error = result.get("error")
        if error == "slow_down":
            interval += 5
        elif error != "authorization_pending":
            fail("the code expired; run login again" if error == "expired_token" else str(error))
    fail("the code expired; run login again")


def cmd_logout(_args) -> None:
    if CREDENTIALS.exists():
        CREDENTIALS.unlink()
    print("Signed out on this computer. (Sign-ins can be revoked on the website.)")


def cmd_whoami(_args) -> None:
    status, me = request("GET", "/api/me")
    if status != 200 or not me.get("user"):
        fail("not signed in (or the sign-in was revoked): run `gogoga.py login`")
    print(f"{me['user']['email']} on {server()}")


def referenced_files(manifest_path: Path) -> list[Path]:
    """The manifest plus every image it points at, the same way the platform imports it."""
    manifest = json.loads(manifest_path.read_text())
    files = [manifest_path]

    def add(base: Path, entry: object) -> None:
        if isinstance(entry, dict) and isinstance(entry.get("file"), str):
            files.append((base / entry["file"]).resolve())
            add(base, entry.get("line_art"))

    if isinstance(manifest.get("assets_from"), str):
        parent_path = (manifest_path.parent / manifest["assets_from"]).resolve()
        files.append(parent_path)
        parent = json.loads(parent_path.read_text())
        for entry in (parent.get("assets") or {}).values():
            add(parent_path.parent, entry)
    for entry in (manifest.get("assets") or {}).values():
        add(manifest_path.parent, entry)
    for group in (manifest.get("style_assets") or {}).values():
        for entry in (group or {}).values():
            add(manifest_path.parent, entry)
    return files


def cmd_upload(args) -> None:
    manifest_path = Path(args.manifest).resolve()
    if not manifest_path.is_file():
        fail(f"no such manifest: {args.manifest}")
    try:
        manifest = json.loads(manifest_path.read_text())
    except ValueError as error:
        fail(f"{args.manifest} is not JSON: {error}")
    if not isinstance(manifest.get("title"), str):
        fail("the manifest has no title")
    previews = [Path(p).resolve() for p in args.preview or []]
    files = referenced_files(manifest_path) + previews
    missing = [str(f) for f in files if not f.is_file()]
    if missing:
        fail("missing files:\n  " + "\n  ".join(missing))

    # Send paths relative to the folder that holds them all, so "../shared/atlas.png" still resolves.
    root = Path(os.path.commonpath([str(f.parent) for f in files]))
    rel = lambda f: f.relative_to(root).as_posix()
    unique = {rel(f): f for f in files}
    size = sum(f.stat().st_size for f in unique.values())
    if size > 40 * 1024 * 1024:
        fail(f"upload is {size / 1e6:.1f} MB; the limit is 40 MB")
    body = {
        "type": args.type,
        "manifest": rel(manifest_path),
        "previews": [rel(p) for p in previews],
        "files": {name: base64.b64encode(f.read_bytes()).decode() for name, f in unique.items()},
    }
    if args.collection:
        body["collection"] = args.collection
    print(f"Uploading {manifest['title']} ({len(unique)} files, {size / 1e6:.1f} MB) to {server()}…", flush=True)
    status, result = request("POST", "/api/me/materials", body)
    if status == 401:
        fail("not signed in (or the sign-in was revoked): run `gogoga.py login`")
    if status != 201:
        fail(result.get("error", f"upload failed (HTTP {status})"))
    print(f"Uploaded: {result['title']} ({result['type']})\n{result['url']}")


def cmd_list(_args) -> None:
    status, index = request("GET", "/api/me/library/index.json")
    if status != 200:
        fail(index.get("error", f"HTTP {status}"))
    materials = index.get("materials", [])
    if not materials:
        print("No uploads yet.")
    for m in materials:
        print(f"{m['id']:40} {m['type']:11} {m['title']}")


def cmd_delete(args) -> None:
    status, result = request("DELETE", f"/api/me/materials/{args.id}")
    if status != 200:
        fail(result.get("error", f"HTTP {status}"))
    print(f"Deleted {args.id}.")


def main() -> None:
    parser = argparse.ArgumentParser(prog="gogoga.py", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("login", help="sign in from this terminal")
    p.add_argument("--server", help=f"default {DEFAULT_SERVER} (or GOGOGA_SERVER)")
    p.add_argument("--no-browser", action="store_true", help="only print the link")
    p.set_defaults(fn=cmd_login)
    sub.add_parser("logout").set_defaults(fn=cmd_logout)
    sub.add_parser("whoami").set_defaults(fn=cmd_whoami)
    p = sub.add_parser("upload", help="upload a skill's manifest, its images and rendered pages")
    p.add_argument("manifest")
    p.add_argument("--type", required=True, choices=TYPES)
    p.add_argument("--preview", action="append", metavar="PNG", help="a rendered page; repeat for several")
    p.add_argument("--collection", help="theme slug grouping related materials, e.g. pear")
    p.set_defaults(fn=cmd_upload)
    sub.add_parser("list").set_defaults(fn=cmd_list)
    p = sub.add_parser("delete")
    p.add_argument("id")
    p.set_defaults(fn=cmd_delete)
    args = parser.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
