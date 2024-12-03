import argparse


class Worker:
    """Processes log chunks and reports results"""
    
    def __init__(self, port: int, worker_id: str, coordinator_url: str):
        self.worker_id = worker_id
        self.coordinator_url = coordinator_url
        self.port = port
    
    def start(self) -> None:
        """Start worker server"""
        print(f"Starting worker {self.worker_id} on port {self.port}...")
        pass

    async def process_chunk(self, filepath: str, start: int, size: int) -> dict:
        """Process a chunk of log file and return metrics"""
        with open(filepath, "r") as file:
            file.seek(start)
            chunk = file.read(size)
            lines = chunk.strip().split("\n")

            metrics = {"error_count": 0, "response_times": [], "request_count": 0}
            for line in lines:
                if "ERROR" in line:
                    metrics["error_count"] += 1
                if "Request processed in" in line:
                    time_taken = int(line.split("in")[-1].strip("ms"))
                    metrics["response_times"].append(time_taken)
                    metrics["request_count"] += 1

            avg_response_time = sum(metrics["response_times"]) / len(metrics["response_times"]) if metrics["response_times"] else 0
            return {
                "error_rate": metrics["error_count"] / len(lines),
                "avg_response_time": avg_response_time,
                "request_count": metrics["request_count"]
            }

    async def report_health(self) -> None:
        """Send heartbeat to coordinator"""
        while True:
            async with aiohttp.ClientSession() as session:
                try:
                    await session.post(f"{self.coordinator_url}/heartbeat", json={"worker_id": self.worker_id})
                except Exception as e:
                    print(f"Error reporting health: {e}")
            await asyncio.sleep(5)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Log Analyzer Coordinator")
    parser.add_argument("--port", type=int, default=8000, help="Coordinator port")
    parser.add_argument("--id", type=str, default="worker1", help="Worker ID")
    parser.add_argument("--coordinator", type=str, default="http://localhost:8000", help="Coordinator URL")
    args = parser.parse_args()

    worker = Worker(port=args.port, worker_id=args.id, coordinator_url=args.coordinator)
    worker.start()
