import json
import sys
from collections import deque

def find_path_to_win(filename="transitions_game.json"):
    try:
        with open(filename, "r") as f:
            transitions = json.load(f)
    except FileNotFoundError:
        print(f"❌ File {filename} not found. Run the agent first to generate data.")
        return None

    if not transitions:
        print("❌ No transitions data found.")
        return None

    start_state = list(transitions.keys())[0]
    queue = deque([(start_state, [])])
    visited = set()

    print(f"🔍 Searching {len(transitions)} mapped states for optimal path...")

    while queue:
        current_state, path = queue.popleft()
        if current_state in visited:
            continue
        visited.add(current_state)

        for action, data in transitions.get(current_state, {}).items():
            next_state_key = data["next_state_key"]
            next_game_state = data["next_game_state"]
            
            new_path = path + [action]
            
            if next_game_state == "GameState.WIN":
                print(f"\n🏆 WIN STATE REACHED!")
                print(f"Shortest Optimal Path: {len(new_path)} actions.")
                print(f"Sequence: {new_path}")
                return new_path
            
            if next_state_key not in visited:
                queue.append((next_state_key, new_path))
    
    print("❌ No win state found. Keep exploring!")
    return None

if __name__ == "__main__":
    filename = sys.argv[1] if len(sys.argv) > 1 else "transitions_game.json"
    find_path_to_win(filename)