import os
print("MAYAN_APPS:", os.environ.get("MAYAN_APPS"))
print("COMMON_EXTRA_APPS:", os.environ.get("COMMON_EXTRA_APPS"))
print("All env vars with MAYAN:")
for key, value in os.environ.items():
    if 'MAYAN' in key:
        print(f"  {key}: {value}")
