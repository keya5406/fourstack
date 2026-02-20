import sys

if sys.platform.startswith("win"):
    import winsound

def alert(duration_ms: int = 5000):
    if sys.platform.startswith("win"):
        winsound.Beep(3000, duration_ms) # play a tone at 3000 Hz for the requested duration_ms
    else:
        print("\a", end="", flush=True)

def main():
    text = input("enter text: ").strip()
    if text == "mismatch":
        alert()
        print("***** mismatch detected *****")
