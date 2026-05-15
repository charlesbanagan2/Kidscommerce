import time
import socket

host = "db.qkdacoawexaxejljfihh.supabase.co"
port = 6543

print(f"Testing connection to {host}:{port}...")
print("Running 5 tests...\n")

latencies = []
for i in range(5):
    try:
        start = time.time()
        sock = socket.create_connection((host, port), timeout=5)
        latency = (time.time() - start) * 1000
        sock.close()
        latencies.append(latency)
        print(f"Test {i+1}: {latency:.0f}ms")
    except Exception as e:
        print(f"Test {i+1}: Failed - {e}")

if latencies:
    avg = sum(latencies) / len(latencies)
    print(f"\n{'='*40}")
    print(f"Average latency: {avg:.0f}ms")
    print(f"{'='*40}")
    
    if avg < 50:
        print("✓ EXCELLENT - Very close to server")
    elif avg < 150:
        print("✓ GOOD - Acceptable latency")
    elif avg < 300:
        print("⚠ MODERATE - Consider closer region")
    else:
        print("✗ HIGH - Strongly recommend closer region")
