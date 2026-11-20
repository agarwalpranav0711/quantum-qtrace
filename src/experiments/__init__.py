"""
Experiments package initialization for Q-TRACE.
"""
from src.experiments.runner import (
    run_test_case_evaluations,
    run_coupon_collector_experiment,
    export_experiment_data,
)
from src.experiments.plotter import (
    plot_coupon_collector_curves,
    plot_observed_coordinates,
    plot_memory_scaling,
    plot_gate_count_comparison,
    export_circuit_text_diagrams,
    generate_all_figures,
)

