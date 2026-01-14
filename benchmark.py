"""
Enhanced Benchmark Comparison Tool for Traffic Control Methods

This script compares the performance of 3 traffic light control methods:
1. Fixed Switch (default timed lights)
2. Q-Learning
3. Contextual Q-Learning

Features:
- Runs 50 simulations per method for statistical significance
- Calculates mean, std dev, min, max, 95% confidence interval
- Tests across multiple traffic scenarios including fluctuating traffic
"""

import sys
import os
import argparse
import csv
import math
import random
from typing import Dict, List, Tuple, Callable
from dataclasses import dataclass, field

# Ensure we can import modules from the current directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from traffic_sim.simulation import Simulation
from traffic_sim.constants import FPS
from ai_controller.traffic_env import TrafficEnv
from ai_controller.q_agent import QLearningAgent


# Configuration
NUM_RUNS = 50           # Number of simulations per method for statistical analysis
TEST_NUM_RUNS = 5       # Reduced runs for quick testing

SPAWN_RATE_SCENARIOS = {
    "High Traffic": 1,
    "Medium-High": 2,
    "Medium": 5,
    "Low Traffic": 10,
    "Fluctuating": None,  # Special case: varying traffic
}

DEFAULT_DURATION = 2000  # ticks
TEST_DURATION = 200  # ticks for quick testing

# Fluctuating traffic pattern configuration - REALISTIC DAILY PROPORTIONS
# Real traffic distribution (approximate):
#   - Rush hours (high traffic): ~10% of day (2x 1h = 2h/24h)
#   - Medium traffic: ~30% of day (morning/afternoon activity)
#   - Low traffic: ~60% of day (night, early morning, late evening)
# Pattern simulates: Night → Morning rush → Day → Evening rush → Night
FLUCTUATION_INTERVAL = 200  # ticks between spawn rate changes (~20 seconds at 10 FPS)
FLUCTUATION_RATES = [
    # Night/Early morning - Low traffic (6 intervals = 60%)
    10, 10, 8, 8, 10, 10,
    # Morning rush hour - High traffic (1 interval = 10%)
    1,
    # Daytime - Medium traffic (3 intervals = 30%)
    3, 5, 5,
]  # Total 10 intervals, cycling through


@dataclass
class BenchmarkResult:
    """Stores benchmark results for a single run."""
    avg_wait_time_seconds: float = 0.0
    max_wait_time_seconds: float = 0.0
    avg_queue_length: float = 0.0
    max_queue_length: int = 0
    total_cars_spawned: int = 0


@dataclass
class AggregatedResult:
    """Stores aggregated statistics across multiple runs."""
    # Wait time statistics
    mean_wait_time: float = 0.0
    std_wait_time: float = 0.0
    min_wait_time: float = 0.0
    max_wait_time: float = 0.0
    ci95_wait_time: float = 0.0  # 95% confidence interval margin
    
    # Max wait time statistics
    mean_max_wait_time: float = 0.0
    std_max_wait_time: float = 0.0
    
    # Queue length statistics
    mean_queue_length: float = 0.0
    std_queue_length: float = 0.0
    min_queue_length: float = 0.0
    max_queue_length: float = 0.0
    ci95_queue_length: float = 0.0
    
    # Max queue statistics
    mean_max_queue: float = 0.0
    std_max_queue: float = 0.0
    
    # Cars spawned
    mean_cars_spawned: float = 0.0
    
    # Raw data for analysis
    num_runs: int = 0


def calculate_statistics(values: List[float]) -> Tuple[float, float, float, float, float]:
    """
    Calculate mean, std dev, min, max, and 95% CI margin.
    Returns: (mean, std, min, max, ci95_margin)
    """
    n = len(values)
    if n == 0:
        return 0.0, 0.0, 0.0, 0.0, 0.0
    
    mean = sum(values) / n
    
    if n > 1:
        variance = sum((x - mean) ** 2 for x in values) / (n - 1)
        std = math.sqrt(variance)
        # 95% CI: mean ± 1.96 * (std / sqrt(n))
        ci95_margin = 1.96 * (std / math.sqrt(n))
    else:
        std = 0.0
        ci95_margin = 0.0
    
    return mean, std, min(values), max(values), ci95_margin


def aggregate_results(results: List[BenchmarkResult]) -> AggregatedResult:
    """Aggregate multiple benchmark results into statistics."""
    agg = AggregatedResult()
    agg.num_runs = len(results)
    
    if not results:
        return agg
    
    # Extract values
    wait_times = [r.avg_wait_time_seconds for r in results]
    max_wait_times = [r.max_wait_time_seconds for r in results]
    queue_lengths = [r.avg_queue_length for r in results]
    max_queues = [float(r.max_queue_length) for r in results]
    cars_spawned = [float(r.total_cars_spawned) for r in results]
    
    # Calculate statistics
    agg.mean_wait_time, agg.std_wait_time, agg.min_wait_time, agg.max_wait_time, agg.ci95_wait_time = \
        calculate_statistics(wait_times)
    
    agg.mean_max_wait_time, agg.std_max_wait_time, _, _, _ = calculate_statistics(max_wait_times)
    
    agg.mean_queue_length, agg.std_queue_length, agg.min_queue_length, agg.max_queue_length, agg.ci95_queue_length = \
        calculate_statistics(queue_lengths)
    
    agg.mean_max_queue, agg.std_max_queue, _, _, _ = calculate_statistics(max_queues)
    
    agg.mean_cars_spawned = sum(cars_spawned) / len(cars_spawned)
    
    return agg


def run_fixed_switch_benchmark(spawn_rate: int, duration: int, fluctuating: bool = False) -> BenchmarkResult:
    """
    Run benchmark for fixed switch (default timed lights) control.
    """
    sim = Simulation()
    sim.spawn_rate = spawn_rate if not fluctuating else FLUCTUATION_RATES[0]
    
    max_wait_time = 0
    
    for tick in range(duration):
        # Handle fluctuating traffic
        if fluctuating:
            rate_index = (tick // FLUCTUATION_INTERVAL) % len(FLUCTUATION_RATES)
            sim.spawn_rate = FLUCTUATION_RATES[rate_index]
        
        # Track max wait time
        for car in sim.cars:
            if car.total_wait_time > max_wait_time:
                max_wait_time = car.total_wait_time
        
        sim.step()
    
    # Final check
    for car in sim.cars:
        if car.total_wait_time > max_wait_time:
            max_wait_time = car.total_wait_time
    
    result = BenchmarkResult()
    result.avg_wait_time_seconds = sim.get_average_wait_time_seconds()
    result.max_wait_time_seconds = max_wait_time / FPS
    result.avg_queue_length = sim.get_average_queue_length()
    result.max_queue_length = sim.get_max_queue_length()
    result.total_cars_spawned = sim.total_cars_spawned
    
    return result


def run_qlearning_benchmark(spawn_rate: int, duration: int, contextual: bool = False, fluctuating: bool = False) -> BenchmarkResult:
    """
    Run benchmark for Q-Learning or Contextual Q-Learning control.
    """
    env = TrafficEnv(spawn_rate=spawn_rate if not fluctuating else FLUCTUATION_RATES[0], contextual=contextual)
    
    model_file = "q_agent_contextual.pkl" if contextual else "q_agent.pkl"
    agent = QLearningAgent()
    
    if os.path.exists(model_file):
        agent.load(model_file)
    
    agent.epsilon = 0.0
    
    max_wait_time = 0
    states = env.reset()
    
    for tick in range(duration):
        # Handle fluctuating traffic
        if fluctuating:
            rate_index = (tick // FLUCTUATION_INTERVAL) % len(FLUCTUATION_RATES)
            new_rate = FLUCTUATION_RATES[rate_index]
            env.set_spawn_rate(new_rate)
        
        # Track max wait time
        for car in env.sim.cars:
            if car.total_wait_time > max_wait_time:
                max_wait_time = car.total_wait_time
        
        # AI Action
        actions = {}
        for i_id, state in states.items():
            action = agent.choose_action(state)
            actions[i_id] = action
        
        next_states, reward, done = env.step(actions)
        states = next_states
        
        if done:
            break
    
    # Final check
    for car in env.sim.cars:
        if car.total_wait_time > max_wait_time:
            max_wait_time = car.total_wait_time
    
    result = BenchmarkResult()
    result.avg_wait_time_seconds = env.sim.get_average_wait_time_seconds()
    result.max_wait_time_seconds = max_wait_time / FPS
    result.avg_queue_length = env.sim.get_average_queue_length()
    result.max_queue_length = env.sim.get_max_queue_length()
    result.total_cars_spawned = env.sim.total_cars_spawned
    
    return result


def run_multiple_simulations(
    run_func: Callable[[int, int, bool], BenchmarkResult],
    spawn_rate: int,
    duration: int,
    num_runs: int,
    fluctuating: bool = False
) -> List[BenchmarkResult]:
    """Run multiple simulations and collect results."""
    results = []
    for _ in range(num_runs):
        result = run_func(spawn_rate, duration, fluctuating)
        results.append(result)
    return results


def run_all_benchmarks(
    duration: int, 
    num_runs: int,
    verbose: bool = True
) -> Dict[str, Dict[str, AggregatedResult]]:
    """
    Run all benchmarks across all scenarios and control methods.
    Returns: {scenario_name: {method_name: aggregated_result}}
    """
    results = {}
    
    methods = [
        ("Fixed Switch", lambda sr, d, fl: run_fixed_switch_benchmark(sr, d, fl)),
        ("Q-Learning", lambda sr, d, fl: run_qlearning_benchmark(sr, d, contextual=False, fluctuating=fl)),
        ("Contextual Q-Learning", lambda sr, d, fl: run_qlearning_benchmark(sr, d, contextual=True, fluctuating=fl)),
    ]
    
    total_combinations = len(SPAWN_RATE_SCENARIOS) * len(methods)
    current_combo = 0
    
    for scenario_name, spawn_rate in SPAWN_RATE_SCENARIOS.items():
        results[scenario_name] = {}
        fluctuating = (spawn_rate is None)
        effective_spawn_rate = 2 if fluctuating else spawn_rate  # Default for fluctuating
        
        for method_name, run_func in methods:
            current_combo += 1
            if verbose:
                scenario_desc = "fluctuating" if fluctuating else f"spawn_rate={spawn_rate}"
                print(f"[{current_combo}/{total_combinations}] {method_name} - {scenario_name} ({scenario_desc})")
                print(f"    Running {num_runs} simulations...", end=" ", flush=True)
            
            # Run multiple simulations
            single_results = run_multiple_simulations(
                run_func, effective_spawn_rate, duration, num_runs, fluctuating
            )
            
            # Aggregate results
            agg_result = aggregate_results(single_results)
            results[scenario_name][method_name] = agg_result
            
            if verbose:
                print(f"Done! Avg Wait: {agg_result.mean_wait_time:.2f}s ± {agg_result.std_wait_time:.2f}")
    
    return results


def print_results_table(results: Dict[str, Dict[str, AggregatedResult]], duration: int, num_runs: int):
    """Print formatted results table with statistical data."""
    print("\n" + "=" * 100)
    print("              TRAFFIC CONTROL BENCHMARK RESULTS (STATISTICAL ANALYSIS)")
    print("=" * 100)
    print(f"Duration: {duration} ticks ({duration / FPS:.1f}s) | Runs per method: {num_runs}")
    print()
    
    methods = ["Fixed Switch", "Q-Learning", "Contextual Q-Learning"]
    
    for scenario_name, scenario_results in results.items():
        spawn_rate = SPAWN_RATE_SCENARIOS[scenario_name]
        rate_desc = "fluctuating" if spawn_rate is None else f"spawn_rate={spawn_rate}"
        
        print(f"\n{'─' * 100}")
        print(f" Scenario: {scenario_name} ({rate_desc}) - {num_runs} runs")
        print(f"{'─' * 100}")
        
        # Header
        print(f"{'Method':<22} │ {'Avg Wait (s)':<24} │ {'Max Wait (s)':<16} │ {'Avg Queue':<24} │ {'Max Queue':<12}")
        print(f"{'─' * 22}─┼─{'─' * 24}─┼─{'─' * 16}─┼─{'─' * 24}─┼─{'─' * 12}")
        
        for method in methods:
            if method in scenario_results:
                r = scenario_results[method]
                wait_str = f"{r.mean_wait_time:.2f} ± {r.std_wait_time:.2f}"
                max_wait_str = f"{r.mean_max_wait_time:.2f} ± {r.std_max_wait_time:.2f}"
                queue_str = f"{r.mean_queue_length:.2f} ± {r.std_queue_length:.2f}"
                max_queue_str = f"{r.mean_max_queue:.1f} ± {r.std_max_queue:.1f}"
                
                method_display = method[:22]
                print(f"{method_display:<22} │ {wait_str:<24} │ {max_wait_str:<16} │ {queue_str:<24} │ {max_queue_str:<12}")
        
        # Min/Max row
        print(f"{'─' * 22}─┴─{'─' * 24}─┴─{'─' * 16}─┴─{'─' * 24}─┴─{'─' * 12}")
        print(f"  Range [min - max]:")
        for method in methods:
            if method in scenario_results:
                r = scenario_results[method]
                print(f"    {method}: Wait [{r.min_wait_time:.2f} - {r.max_wait_time:.2f}]s, Queue [{r.min_queue_length:.2f} - {r.max_queue_length:.2f}]")
    
    print(f"\n{'=' * 100}\n")


def print_summary_comparison(results: Dict[str, Dict[str, AggregatedResult]], num_runs: int):
    """Print a high-level summary across all scenarios."""
    print("\n" + "=" * 100)
    print("                           OVERALL SUMMARY (Mean ± Std Dev)")
    print("=" * 100)
    
    methods = ["Fixed Switch", "Q-Learning", "Contextual Q-Learning"]
    
    # Calculate overall averages
    method_totals = {m: {"wait_sum": 0, "wait_sq_sum": 0, "queue_sum": 0, "queue_sq_sum": 0, "count": 0} 
                     for m in methods}
    
    for scenario_results in results.values():
        for method, r in scenario_results.items():
            method_totals[method]["wait_sum"] += r.mean_wait_time
            method_totals[method]["queue_sum"] += r.mean_queue_length
            method_totals[method]["count"] += 1
    
    print(f"\n{'Control Method':<24} │ {'Avg Wait Time (s)':<20} │ {'Avg Queue Length':<20} │ {'Total Runs':<12}")
    print(f"{'─' * 24}─┼─{'─' * 20}─┼─{'─' * 20}─┼─{'─' * 12}")
    
    for method in methods:
        t = method_totals[method]
        if t["count"] > 0:
            avg_wait = t["wait_sum"] / t["count"]
            avg_queue = t["queue_sum"] / t["count"]
            total_runs = t["count"] * num_runs
            print(f"{method:<24} │ {avg_wait:>19.2f} │ {avg_queue:>19.2f} │ {total_runs:>11}")
    
    print()
    
    # Find best performer
    best_method = min(methods, key=lambda m: method_totals[m]["wait_sum"] / max(method_totals[m]["count"], 1))
    print(f"  🏆 Best performer (lowest avg wait): {best_method}")
    print()


def export_to_csv(results: Dict[str, Dict[str, AggregatedResult]], filename: str, num_runs: int):
    """Export results to CSV file with all statistical metrics (French version)."""
    methods = ["Fixed Switch", "Q-Learning", "Contextual Q-Learning"]
    methods_fr = {
        "Fixed Switch": "Feux Temporisés",
        "Q-Learning": "Q-Learning",
        "Contextual Q-Learning": "Q-Learning Contextuel"
    }
    scenarios_fr = {
        "High Traffic": "Trafic Élevé",
        "Medium-High": "Trafic Moyen-Élevé",
        "Medium": "Trafic Moyen",
        "Low Traffic": "Trafic Faible",
        "Fluctuating": "Trafic Fluctuant"
    }
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, delimiter=';')  # Use ; for French Excel
        
        # ===== SECTION RÉSUMÉ =====
        writer.writerow(["=== RÉSUMÉ GLOBAL ==="])
        writer.writerow([])
        
        # Calculate overall averages for ranking
        method_totals = {m: {"wait_sum": 0, "queue_sum": 0, "count": 0} for m in methods}
        for scenario_results in results.values():
            for method, r in scenario_results.items():
                method_totals[method]["wait_sum"] += r.mean_wait_time
                method_totals[method]["queue_sum"] += r.mean_queue_length
                method_totals[method]["count"] += 1
        
        # Sort by average wait time (best = lowest)
        rankings = []
        for method in methods:
            t = method_totals[method]
            if t["count"] > 0:
                avg_wait = t["wait_sum"] / t["count"]
                avg_queue = t["queue_sum"] / t["count"]
                rankings.append((method, avg_wait, avg_queue))
        
        rankings.sort(key=lambda x: x[1])  # Sort by avg wait time
        
        writer.writerow(["Rang", "Méthode de Contrôle", "Temps Attente Moyen (s)", "Longueur File Moyenne", "Meilleur?"])
        for i, (method, avg_wait, avg_queue) in enumerate(rankings):
            is_best = "*** MEILLEUR ***" if i == 0 else ""
            writer.writerow([i + 1, methods_fr[method], f"{avg_wait:.4f}", f"{avg_queue:.4f}", is_best])
        
        writer.writerow([])
        writer.writerow([f"Meilleure Méthode: {methods_fr[rankings[0][0]]}"])
        writer.writerow([f"Nombre de Simulations: {len(results) * num_runs} par méthode"])
        writer.writerow([])
        writer.writerow([])
        
        # ===== RÉSULTATS DÉTAILLÉS =====
        writer.writerow(["=== RÉSULTATS DÉTAILLÉS PAR SCÉNARIO ==="])
        writer.writerow([])
        
        # Header
        writer.writerow([
            "Scénario", "Taux de Spawn", "Méthode", "Nb Simulations",
            "Attente Moy (s)", "Écart-Type Attente", "Attente Min (s)", "Attente Max (s)", "IC95 Attente",
            "Attente Max Moy (s)", "Écart-Type Attente Max",
            "File Moy", "Écart-Type File", "File Min", "File Max", "IC95 File",
            "File Max Moy", "Écart-Type File Max",
            "Voitures Générées Moy", "Meilleur du Scénario?"
        ])
        
        # Data with best-in-scenario marker
        for scenario_name, scenario_results in results.items():
            spawn_rate = SPAWN_RATE_SCENARIOS[scenario_name]
            rate_str = "variable" if spawn_rate is None else str(spawn_rate)
            scenario_fr = scenarios_fr.get(scenario_name, scenario_name)
            
            # Find best method for this scenario
            best_in_scenario = min(scenario_results.items(), key=lambda x: x[1].mean_wait_time)[0]
            
            for method_name, r in scenario_results.items():
                is_best = "MEILLEUR" if method_name == best_in_scenario else ""
                writer.writerow([
                    scenario_fr, rate_str, methods_fr[method_name], num_runs,
                    f"{r.mean_wait_time:.4f}", f"{r.std_wait_time:.4f}", 
                    f"{r.min_wait_time:.4f}", f"{r.max_wait_time:.4f}", f"{r.ci95_wait_time:.4f}",
                    f"{r.mean_max_wait_time:.4f}", f"{r.std_max_wait_time:.4f}",
                    f"{r.mean_queue_length:.4f}", f"{r.std_queue_length:.4f}",
                    f"{r.min_queue_length:.4f}", f"{r.max_queue_length:.4f}", f"{r.ci95_queue_length:.4f}",
                    f"{r.mean_max_queue:.4f}", f"{r.std_max_queue:.4f}",
                    f"{r.mean_cars_spawned:.2f}",
                    is_best
                ])
    
    print(f"Résultats exportés vers: {filename}")


def main():
    parser = argparse.ArgumentParser(
        description="Enhanced benchmark with statistical analysis for traffic control methods",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--test", action="store_true",
        help=f"Quick test mode ({TEST_NUM_RUNS} runs, {TEST_DURATION} ticks)"
    )
    parser.add_argument(
        "--runs", type=int, default=None,
        help=f"Number of simulation runs per method (default: {NUM_RUNS})"
    )
    parser.add_argument(
        "--duration", type=int, default=None,
        help=f"Simulation duration in ticks (default: {DEFAULT_DURATION})"
    )
    parser.add_argument(
        "--csv", type=str, metavar="FILENAME",
        help="Export results to CSV file"
    )
    parser.add_argument(
        "--quiet", action="store_true",
        help="Suppress progress output"
    )
    
    args = parser.parse_args()
    
    # Determine parameters
    if args.test:
        num_runs = TEST_NUM_RUNS
        duration = TEST_DURATION
    else:
        num_runs = args.runs if args.runs else NUM_RUNS
        duration = args.duration if args.duration else DEFAULT_DURATION
    
    total_simulations = len(SPAWN_RATE_SCENARIOS) * 3 * num_runs
    estimated_time = total_simulations * duration / FPS / 60  # minutes (rough estimate)
    
    print("=" * 100)
    print("          ENHANCED TRAFFIC CONTROL BENCHMARK (STATISTICAL ANALYSIS)")
    print("=" * 100)
    print(f"\nMethods: Fixed Switch, Q-Learning, Contextual Q-Learning")
    print(f"Scenarios: {', '.join(SPAWN_RATE_SCENARIOS.keys())}")
    print(f"Runs per method: {num_runs} | Duration: {duration} ticks ({duration / FPS:.1f}s)")
    print(f"Total simulations: {total_simulations}")
    print()
    
    # Run benchmarks
    results = run_all_benchmarks(duration, num_runs, verbose=not args.quiet)
    
    # Print results
    print_results_table(results, duration, num_runs)
    print_summary_comparison(results, num_runs)
    
    # Export to CSV if requested
    if args.csv:
        export_to_csv(results, args.csv, num_runs)


if __name__ == "__main__":
    main()
