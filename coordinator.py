import argparse

class Coordinator:
    """Manages workers and aggregates results"""
    
    def __init__(self, port: int):
        print(f"Starting coordinator on port {port}")
        self.workers = {}
        self.results = {}
        self.port = port

    def start(self) -> None:
        """Start coordinator server"""
        print(f"Starting coordinator on port {self.port}...")
        pass

    async def distribute_work(self, filepath: str) -> None:
        """Split file and assign chunks to workers"""
        file_size = os.path.getsize(filepath)
        chunk_size = file_size // len(self.workers)
        start = 0

        for worker_id, worker_data in self.workers.items():
            end = start + chunk_size
            await self.assign_task(worker_id, filepath, start, chunk_size)
            start = end

    async def handle_worker_failure(self, worker_id: str) -> None:
        """Reassign work from failed worker"""
        failed_task = self.workers.pop(worker_id)
        # Reassign tasks
        await self.distribute_work(failed_task["filepath"])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Log Analyzer Coordinator")
    parser.add_argument("--port", type=int, default=8000, help="Coordinator port")
    args = parser.parse_args()

    coordinator = Coordinator(port=args.port)
    coordinator.start()
