from __future__ import annotations

import os
import time
import webbrowser
from dataclasses import dataclass

import httpx

# LUHM_PYSIMPLEGUI_MINIMAL_OPERATOR_V1
# Optional desktop operator surface only. No shell execution, signing, install,
# release, provider-secret, or Android-runtime authority is granted here.

HARNESS_ORIGIN = os.environ.get("LUHM_HARNESS_ORIGIN", "http://127.0.0.1:8791").rstrip("/")
PAIR_SCHEMA = "luhm_os.local_harness_pair.v1"


@dataclass
class OperatorSession:
    token: str = ""
    expires_at: float = 0.0

    @property
    def active(self) -> bool:
        return bool(self.token) and time.time() < self.expires_at

    def clear(self) -> None:
        self.token = ""
        self.expires_at = 0.0


def _client() -> httpx.Client:
    return httpx.Client(timeout=1.5, headers={"Cache-Control": "no-store"})


def health() -> dict[str, object]:
    with _client() as client:
        response = client.get(f"{HARNESS_ORIGIN}/health")
        response.raise_for_status()
        data = response.json()
        return data if isinstance(data, dict) else {}


def pair(code: str) -> OperatorSession:
    if len(code) != 6 or not code.isdigit():
        raise ValueError("Pair code must be six digits.")
    with _client() as client:
        response = client.post(
            f"{HARNESS_ORIGIN}/auth/pair",
            headers={"X-LuHm-Request": "pair"},
            json={"code": code},
        )
        response.raise_for_status()
        data = response.json()
    if data.get("schema") != PAIR_SCHEMA or not data.get("token"):
        raise RuntimeError("Local harness returned an invalid pairing response.")
    return OperatorSession(token=str(data["token"]), expires_at=float(data["expires_at"]))


def cockpit_ticket(session: OperatorSession) -> str:
    if not session.active:
        raise RuntimeError("Operator session is not active.")
    with _client() as client:
        response = client.post(
            f"{HARNESS_ORIGIN}/auth/ticket",
            headers={
                "Authorization": f"Bearer {session.token}",
                "X-LuHm-Request": "operator",
            },
        )
        response.raise_for_status()
        data = response.json()
    ticket = str(data.get("ticket", ""))
    if not ticket:
        raise RuntimeError("Local harness did not issue a cockpit ticket.")
    return ticket


def logout(session: OperatorSession) -> None:
    if session.active:
        try:
            with _client() as client:
                client.post(
                    f"{HARNESS_ORIGIN}/auth/logout",
                    headers={
                        "Authorization": f"Bearer {session.token}",
                        "X-LuHm-Request": "operator",
                    },
                )
        finally:
            session.clear()
    else:
        session.clear()


def main() -> int:
    try:
        import PySimpleGUI as sg
    except ImportError as exc:
        raise SystemExit(
            "PySimpleGUI is optional. Install the LuHm GUI extra with: pip install '.[gui]'"
        ) from exc

    sg.theme("DarkPurple4")
    layout = [
        [sg.Text("LuHm OS // Minimal Operator", font=("Any", 16, "bold"))],
        [sg.Text("Thin local control surface. Crown authority stays outside this GUI.")],
        [sg.Text("Harness"), sg.Text("UNKNOWN", key="-HARNESS-", size=(28, 1))],
        [sg.Text("Operator"), sg.Text("GUEST", key="-OPERATOR-", size=(28, 1))],
        [sg.Text("Pair code"), sg.Input(key="-PAIR-", size=(12, 1), password_char="•")],
        [
            sg.Button("CHECK HARNESS"),
            sg.Button("PAIR"),
            sg.Button("OPEN COCKPIT"),
        ],
        [sg.Button("LOGOUT"), sg.Button("EXIT")],
        [
            sg.Multiline(
                "No shell execution. No silent install. No signing or release authority.\n",
                key="-LOG-",
                size=(72, 8),
                disabled=True,
                autoscroll=True,
            )
        ],
    ]
    window = sg.Window("LuHm OS Minimal Operator", layout, finalize=True)
    session = OperatorSession()

    def log(message: str) -> None:
        window["-LOG-"].update(message + "\n", append=True)

    def refresh_status() -> None:
        try:
            data = health()
            ok = bool(data.get("ok"))
            pairing = bool(data.get("pairing_available"))
            window["-HARNESS-"].update("ONLINE" if ok else "DEGRADED")
            log(f"Harness check: {'GREEN' if ok else 'YELLOW'}; pairing={'ready' if pairing else 'unavailable'}")
        except Exception as exc:
            window["-HARNESS-"].update("OFFLINE")
            log(f"Harness check: RED ({type(exc).__name__})")
        window["-OPERATOR-"].update("PAIRED" if session.active else "GUEST")

    refresh_status()
    try:
        while True:
            event, values = window.read(timeout=1000)
            if event in (sg.WINDOW_CLOSED, "EXIT"):
                break
            if event == "CHECK HARNESS":
                refresh_status()
            elif event == "PAIR":
                try:
                    session = pair(str(values.get("-PAIR-", "")).strip())
                    window["-PAIR-"].update("")
                    window["-OPERATOR-"].update("PAIRED")
                    log("Operator pairing: GREEN. Token remains memory-only.")
                except Exception as exc:
                    session.clear()
                    window["-OPERATOR-"].update("GUEST")
                    log(f"Operator pairing: RED ({type(exc).__name__})")
            elif event == "OPEN COCKPIT":
                try:
                    ticket = cockpit_ticket(session)
                    webbrowser.open(f"{HARNESS_ORIGIN}/cockpit?ticket={ticket}", new=1)
                    log("Cockpit ticket issued and handed to the local browser.")
                except Exception as exc:
                    log(f"Cockpit open: RED ({type(exc).__name__})")
            elif event == "LOGOUT":
                logout(session)
                window["-OPERATOR-"].update("GUEST")
                log("Operator session closed.")
            elif not session.active and session.token:
                session.clear()
                window["-OPERATOR-"].update("GUEST")
                log("Operator session expired.")
    finally:
        logout(session)
        window.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
