import json

def main():
    with open("results/data/test_case_evaluations.json", "r", encoding="utf-8") as f:
        tc = json.load(f)
    print("=== TEST CASE EVALUATION SUMMARY ===")
    for d in tc:
        print(f"{d['case_id']:25s} | 16Q: {d['16q_is_exact_match']} ({d['16q_observed_coords']}/16) | 12Q: {d['12q_is_exact_match']} ({d['12q_observed_coords']}/16)")

    with open("results/data/coupon_collector_experiment.json", "r", encoding="utf-8") as f:
        cc = json.load(f)
    print("\n=== COUPON COLLECTOR SAMPLING DATA ===")
    print("Shots | Mean Obs | Emp P | Exact P | Poisson P | Missing")
    for d in cc:
        print(f"{d['shots']:5d} | {d['mean_observed_coordinates']:8.3f} | {d['empirical_prob_full_coverage']:5.3f} | {d['exact_prob_full_coverage']:7.5f} | {d['poisson_prob_full_coverage']:9.5f} | {d['expected_missing_pixels']:6.3f}")

if __name__ == "__main__":
    main()

