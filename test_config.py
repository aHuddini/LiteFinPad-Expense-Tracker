"""Quick test to verify config.py imports correctly"""
import config

print("[OK] Config imported successfully")
print(f"Window size: {config.Window.WIDTH} x {config.Window.HEIGHT}")
print(f"Green color: {config.Colors.GREEN_PRIMARY}")
print(f"Font family: {config.Fonts.FAMILY}")
print(f"Animation duration: {config.Animation.SLIDE_OUT_DURATION_MS}ms")
print(f"Number pad max length: {config.NumberPad.MAX_AMOUNT_LENGTH}")
print("\n[OK] All config classes accessible!")

