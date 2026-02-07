#!/usr/bin/env python3
"""Benchmark query performance."""

import asyncio
import time
import statistics
from typing import List, Dict, Any
import logging

from mazure.services.resource_graph import ResourceGraphService
from mazure.services.graph import GraphService
from mazure.core.state import StateManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QueryBenchmark:
    """Benchmark query performance."""
    
    def __init__(self):
        self.rg_service = ResourceGraphService(StateManager())
        self.graph_service = GraphService(StateManager())
        self.results = []
    
    async def benchmark_query(self, name: str, coro, iterations: int = 10) -> Dict[str, Any]:
        """Benchmark a single query."""
        logger.info(f"\nBenchmarking: {name}")
        times = []
        
        for i in range(iterations):
            start = time.perf_counter()
            try:
                await coro()
                elapsed = time.perf_counter() - start
                times.append(elapsed * 1000)  # Convert to ms
            except Exception as e:
                logger.error(f"  Iteration {i+1} failed: {str(e)}")
        
        if times:
            result = {
                'name': name,
                'iterations': len(times),
                'min_ms': min(times),
                'max_ms': max(times),
                'mean_ms': statistics.mean(times),
                'median_ms': statistics.median(times),
                'stdev_ms': statistics.stdev(times) if len(times) > 1 else 0
            }
            self.results.append(result)
            logger.info(f"  Mean: {result['mean_ms']:.2f}ms")
            logger.info(f"  Median: {result['median_ms']:.2f}ms")
            logger.info(f"  Range: {result['min_ms']:.2f}ms - {result['max_ms']:.2f}ms")
            return result
        return None
    
    async def run_benchmarks(self):
        """Run all benchmarks."""
        logger.info("="* 60)
        logger.info("Query Performance Benchmarks")
        logger.info("="* 60)
        
        # Resource Graph benchmarks
        await self.benchmark_query(
            "RG: Simple take 10",
            lambda: self.rg_service.query(['test-sub'], 'Resources | take 10')
        )
        
        await self.benchmark_query(
            "RG: WHERE type filter",
            lambda: self.rg_service.query(
                ['test-sub'],
                "Resources | where type =~ 'Microsoft.Compute/virtualMachines'"
            )
        )
        
        await self.benchmark_query(
            "RG: PROJECT fields",
            lambda: self.rg_service.query(
                ['test-sub'],
                'Resources | project name, type, location | take 100'
            )
        )
        
        await self.benchmark_query(
            "RG: SUMMARIZE count",
            lambda: self.rg_service.query(
                ['test-sub'],
                'Resources | summarize count() by type'
            )
        )
        
        # Graph API benchmarks
        await self.benchmark_query(
            "Graph: List 10 users",
            lambda: self.graph_service.list_users(top=10)
        )
        
        await self.benchmark_query(
            "Graph: Filter users",
            lambda: self.graph_service.list_users(
                top=50,
                filter_expr="startswith(displayName,'A')"
            )
        )
        
        await self.benchmark_query(
            "Graph: List groups",
            lambda: self.graph_service.list_groups(top=10)
        )
        
        # Summary
        logger.info("\n" + "="*60)
        logger.info("Benchmark Summary")
        logger.info("="*60)
        logger.info(f"{'Query':<40} {'Mean (ms)':<15} {'Median (ms)'}")
        logger.info("-"*60)
        for result in self.results:
            logger.info(
                f"{result['name']:<40} "
                f"{result['mean_ms']:<15.2f} "
                f"{result['median_ms']:.2f}"
            )


async def main():
    """Run benchmarks."""
    benchmark = QueryBenchmark()
    await benchmark.run_benchmarks()


if __name__ == '__main__':
    asyncio.run(main())
