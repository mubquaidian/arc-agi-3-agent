import arc_agi
from arcengine import GameAction

# Initialize the local environment
arc = arc_agi.Arcade()
env = arc.make("ls20", render_mode="terminal")

if env is None:
    print("❌ Failed to create environment.")
    exit(1)

print("🚀 Playing 10 random actions to test environment...")
for _ in range(10):
    env.step(GameAction.ACTION1)

print("✅ Environment test complete.")
print(arc.get_scorecard())