import time
import statistics
import concurrent.futures
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def send_health_request(i: int) -> float:
    start = time.time()
    resp = client.get("/health")
    elapsed = (time.time() - start) * 1000  # ms
    assert resp.status_code == 200
    return elapsed

def run_load_test(concurrency: int = 20, total_requests: int = 100):
    print(f"--- Starting Load Test: {total_requests} requests across {concurrency} threads ---")
    start_total = time.time()

    latencies = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = [executor.submit(send_health_request, i) for i in range(total_requests)]
        for f in concurrent.futures.as_completed(futures):
            try:
                lat = f.result()
                latencies.append(lat)
            except Exception as exc:
                print(f"Request error: {exc}")

    total_time = time.time() - start_total
    throughput = total_requests / total_time if total_time > 0 else 0

    latencies.sort()
    p50 = statistics.median(latencies)
    p95 = latencies[int(len(latencies) * 0.95)]
    p99 = latencies[int(len(latencies) * 0.99)]

    print(f"Total Requests: {len(latencies)} / {total_requests}")
    print(f"Total Duration: {total_time:.2f}s")
    print(f"Throughput: {throughput:.2f} req/sec")
    print(f"p50 Latency: {p50:.2f} ms")
    print(f"p95 Latency: {p95:.2f} ms")
    print(f"p99 Latency: {p99:.2f} ms")

if __name__ == "__main__":
    run_load_test()
