import argparse
import itertools
import threading
import time
from typing import Optional

from dotenv import load_dotenv
from src.graph import app

load_dotenv()


def _fmt_elapsed(seconds: float) -> str:
    return f"{seconds:.1f}s"


class StatusTicker:
    def __init__(self, started: float) -> None:
        self._started = started
        self._status = "Queued"
        self._stop_event = threading.Event()
        self._lock = threading.Lock()
        self._thread: Optional[threading.Thread] = None

    def start(self) -> None:
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def update(self, status: str) -> None:
        with self._lock:
            self._status = status

    def emit(self, line: str) -> None:
        with self._lock:
            print("\r" + (" " * 120) + "\r", end="", flush=True)
            print(line)

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=1.0)
        print("\r" + (" " * 120) + "\r", end="", flush=True)

    def _run(self) -> None:
        spinner = itertools.cycle("|/-\\")
        while not self._stop_event.is_set():
            with self._lock:
                status = self._status
            elapsed = _fmt_elapsed(time.perf_counter() - self._started)
            frame = next(spinner)
            print(
                f"\r{frame} Status: {status} | Elapsed: {elapsed}",
                end="",
                flush=True,
            )
            time.sleep(0.12)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Ask-the-Internetz agent.")
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show node-level internals and raw tool call payloads.",
    )
    parser.add_argument(
        "--no-ticker",
        action="store_true",
        help="Disable the live spinner/timer status line.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    print("--- 🌐 Ask-the-Internetz Agent (local llama3.2:3b) ---")
    print("Type 'exit' or 'quit' to end.")
    
    question_index = 0
    while True:
        user_input = input("\nUser: ")
        if user_input.lower() in ["exit", "quit"]:
            break

        question_index += 1
        started = time.perf_counter()
        tool_call_count = 0
        retries = 0
        used_tool = False
        final_answer = ""
        active_tool_name: Optional[str] = None
        active_tool_started: Optional[float] = None
        ticker: Optional[StatusTicker] = None

        print(f"\nQuestion {question_index}: {user_input}")
        if not args.no_ticker:
            ticker = StatusTicker(started)
            ticker.start()
            ticker.update("Queued")
        else:
            print("Status: Queued | Elapsed: 0.0s")

        inputs = {"messages": [("user", user_input)]}
        if ticker:
            ticker.update("Thinking")
        else:
            print(f"Status: Thinking | Elapsed: {_fmt_elapsed(time.perf_counter() - started)}")

        try:
            for output in app.stream(inputs, stream_mode="updates"):
                for node, data in output.items():
                    if args.verbose:
                        if ticker:
                            ticker.emit(f"[Node: {str(node).upper()}]")
                        else:
                            print(f"\n[Node: {str(node).upper()}]")

                    if not isinstance(data, dict) or "messages" not in data or not data["messages"]:
                        continue

                    last_msg = data["messages"][-1]
                    raw_tool_calls = getattr(last_msg, "tool_calls", None)
                    has_tool_call = bool(raw_tool_calls)

                    if args.verbose:
                        if ticker:
                            ticker.emit(f"tool_calls: {raw_tool_calls}")
                            ticker.emit(f"content: {getattr(last_msg, 'content', '')}")
                        else:
                            print("tool_calls:", raw_tool_calls)
                            print("content:", getattr(last_msg, "content", ""))

                    if has_tool_call:
                        used_tool = True
                        for tool_call in raw_tool_calls:
                            name = tool_call.get("name", "unknown") if isinstance(tool_call, dict) else getattr(tool_call, "name", "unknown")
                            args_payload = tool_call.get("args", {}) if isinstance(tool_call, dict) else getattr(tool_call, "args", {})
                            tool_call_count += 1
                            active_tool_name = str(name)
                            active_tool_started = time.perf_counter()
                            if ticker:
                                ticker.update(f"Calling {name}")
                            else:
                                print(
                                    f"Status: Calling {name} | Elapsed: {_fmt_elapsed(time.perf_counter() - started)}"
                                )
                            if args.verbose:
                                if ticker:
                                    ticker.emit(f"Tool Start: {name}(args={args_payload})")
                                else:
                                    print(f"Tool Start: {name}(args={args_payload})")
                        continue

                    if str(node) == "tools" and active_tool_name and active_tool_started is not None:
                        tool_duration = _fmt_elapsed(time.perf_counter() - active_tool_started)
                        if ticker:
                            ticker.emit(
                                f"Tool Done: {active_tool_name} | Duration: {tool_duration} | Success: yes"
                            )
                            ticker.update("Synthesizing")
                        else:
                            print(f"Tool Done: {active_tool_name} | Duration: {tool_duration} | Success: yes")
                        active_tool_name = None
                        active_tool_started = None

                    content = getattr(last_msg, "content", "")
                    if isinstance(content, str) and content.strip():
                        final_answer = content.strip()
                        if used_tool:
                            if ticker:
                                ticker.update("Synthesizing")
                            else:
                                print(
                                    f"Status: Synthesizing | Elapsed: {_fmt_elapsed(time.perf_counter() - started)}"
                                )

            total = _fmt_elapsed(time.perf_counter() - started)
            if ticker:
                ticker.stop()
            print(
                f"Status: Completed | Total: {total} | Tool Calls: {tool_call_count} | Retries: {retries}"
            )
            print("Final Answer:")
            print(final_answer or "(No answer text returned)")

            if used_tool:
                print("Freshness: Live web data")
                print("Confidence: Medium")
        except KeyboardInterrupt:
            total = _fmt_elapsed(time.perf_counter() - started)
            if ticker:
                ticker.stop()
            print(f"\nStatus: Cancelled | Total: {total}")
            print("Cancelled current request. Ready for next question.")
            continue
        except Exception as exc:  # noqa: BLE001
            total = _fmt_elapsed(time.perf_counter() - started)
            if ticker:
                ticker.stop()
            print(f"Status: Failed | Total: {total} | Tool Calls: {tool_call_count}")
            print(f"Reason: {exc}")

if __name__ == "__main__":
    main()
