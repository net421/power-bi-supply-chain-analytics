"""
KPI Verification Tests

Validates KPI calculations against expected ranges and logic.
"""

import pandas as pd
import numpy as np
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analytics.kpi_calculations import SupplyChainKPIs


class KPITester:
    """Class to test KPI calculations."""
    
    def __init__(self):
        self.kpi_calc = SupplyChainKPIs()
        self.test_results = {}
        
    def load_data(self):
        """Load data for testing."""
        self.kpi_calc.load_data()
        
    def test_otif_range(self):
        """Test that OTIF is within valid range."""
        print("\n" + "="*60)
        print("TEST: OTIF Range")
        print("="*60)
        
        otif = self.kpi_calc.calculate_otif()
        
        # OTIF should be between 80% and 100% given our data generation
        passed = 80 <= otif <= 100
        
        print(f"  OTIF Value: {otif:.2f}%")
        print(f"  Expected Range: 80-100%")
        print(f"  {'✓ PASS' if passed else '✗ FAIL'}")
        
        self.test_results['otif_range'] = passed
        return passed
    
    def test_fill_rate_logic(self):
        """Test that fill rate cannot exceed 100% significantly."""
        print("\n" + "="*60)
        print("TEST: Fill Rate Logic")
        print("="*60)
        
        fill_rate = self.kpi_calc.calculate_fill_rate()
        
        # Fill rate should not exceed 100% by much (no over-delivery in our data)
        passed = 90 <= fill_rate <= 100
        
        print(f"  Fill Rate Value: {fill_rate:.2f}%")
        print(f"  Expected Range: 90-100%")
        print(f"  {'✓ PASS' if passed else '✗ FAIL'}")
        
        self.test_results['fill_rate_logic'] = passed
        return passed
    
    def test_on_time_vs_otif(self):
        """Test that On-Time Delivery >= OTIF (logical relationship)."""
        print("\n" + "="*60)
        print("TEST: On-Time vs OTIF Relationship")
        print("="*60)
        
        otif = self.kpi_calc.calculate_otif()
        on_time = self.kpi_calc.calculate_on_time_delivery()
        
        # On-time should always be >= OTIF because OTIF requires both on-time AND in-full
        passed = on_time >= otif
        
        print(f"  OTIF: {otif:.2f}%")
        print(f"  On-Time Delivery: {on_time:.2f}%")
        print(f"  On-Time >= OTIF: {passed}")
        print(f"  {'✓ PASS' if passed else '✗ FAIL'}")
        
        self.test_results['on_time_vs_otif'] = passed
        return passed
    
    def test_perfect_order_subset(self):
        """Test that Perfect Order <= OTIF (perfect is stricter)."""
        print("\n" + "="*60)
        print("TEST: Perfect Order Subset")
        print("="*60)
        
        otif = self.kpi_calc.calculate_otif()
        perfect = self.kpi_calc.calculate_perfect_order()
        
        # Perfect order should be <= OTIF because it has additional quality requirement
        passed = perfect <= otif
        
        print(f"  OTIF: {otif:.2f}%")
        print(f"  Perfect Order: {perfect:.2f}%")
        print(f"  Perfect <= OTIF: {passed}")
        print(f"  {'✓ PASS' if passed else '✗ FAIL'}")
        
        self.test_results['perfect_order_subset'] = passed
        return passed
    
    def test_inventory_turns_positive(self):
        """Test that inventory turns is positive."""
        print("\n" + "="*60)
        print("TEST: Inventory Turns Positive")
        print("="*60)
        
        turns = self.kpi_calc.calculate_inventory_turns()
        
        passed = turns > 0
        
        print(f"  Inventory Turns: {turns:.2f}x")
        print(f"  Positive Value: {passed}")
        print(f"  {'✓ PASS' if passed else '✗ FAIL'}")
        
        self.test_results['inventory_turns_positive'] = passed
        return passed
    
    def test_days_of_supply_reasonable(self):
        """Test that days of supply is in reasonable range."""
        print("\n" + "="*60)
        print("TEST: Days of Supply Reasonable")
        print("="*60)
        
        dos = self.kpi_calc.calculate_days_of_supply()
        
        # Should be between 0.1 and 365 days (allowing for synthetic data variance)
        passed = 0.1 <= dos <= 365
        
        print(f"  Days of Supply: {dos:.2f} days")
        print(f"  Reasonable Range (0.1-365): {passed}")
        print(f"  {'✓ PASS' if passed else '✗ FAIL'}")
        
        self.test_results['days_of_supply_reasonable'] = passed
        return passed
    
    def test_cost_positive(self):
        """Test that costs are positive."""
        print("\n" + "="*60)
        print("TEST: Cost Values Positive")
        print("="*60)
        
        cost_per_order = self.kpi_calc.calculate_cost_to_serve_per_order()
        freight_per_kg = self.kpi_calc.calculate_freight_cost_per_kg()
        
        passed = cost_per_order > 0 and freight_per_kg > 0
        
        print(f"  Cost per Order: ${cost_per_order:,.2f}")
        print(f"  Freight per Kg: ${freight_per_kg:.2f}")
        print(f"  Both Positive: {passed}")
        print(f"  {'✓ PASS' if passed else '✗ FAIL'}")
        
        self.test_results['cost_positive'] = passed
        return passed
    
    def test_supplier_ranking(self):
        """Test supplier ranking produces valid results."""
        print("\n" + "="*60)
        print("TEST: Supplier Ranking")
        print("="*60)
        
        from analytics.rankings_scenarios import RankingsScenarios
        
        rankings = RankingsScenarios()
        rankings.load_data()
        
        supplier_ranks = rankings.calculate_supplier_reliability_rank()
        
        # Check we have rankings for all suppliers
        passed = len(supplier_ranks) == len(rankings.suppliers)
        
        # Check ranks are sequential
        rank_values = sorted(supplier_ranks['reliability_rank'].unique())
        expected_ranks = list(range(1, len(rank_values) + 1))
        ranks_sequential = rank_values == expected_ranks
        
        print(f"  Suppliers Ranked: {len(supplier_ranks)}")
        print(f"  All Suppliers Included: {passed}")
        print(f"  Ranks Sequential: {ranks_sequential}")
        print(f"  {'✓ PASS' if passed and ranks_sequential else '✗ FAIL'}")
        
        self.test_results['supplier_ranking'] = passed and ranks_sequential
        return self.test_results['supplier_ranking']
    
    def test_time_intelligence_ytd(self):
        """Test YTD calculation."""
        print("\n" + "="*60)
        print("TEST: Time Intelligence YTD")
        print("="*60)
        
        from analytics.time_intelligence import TimeIntelligence
        
        ti = TimeIntelligence()
        ti.load_data()
        
        ytd = ti.calculate_otif_ytd()
        py = ti.calculate_otif_py()
        
        # Both should be valid percentages
        passed = 0 <= ytd <= 100 and 0 <= py <= 100
        
        print(f"  OTIF YTD: {ytd:.2f}%")
        print(f"  OTIF PY: {py:.2f}%")
        print(f"  Valid Percentages: {passed}")
        print(f"  {'✓ PASS' if passed else '✗ FAIL'}")
        
        self.test_results['time_intelligence_ytd'] = passed
        return passed
    
    def run_all_tests(self):
        """Run all KPI verification tests."""
        print("\n" + "="*60)
        print("KPI VERIFICATION TEST SUITE")
        print("="*60)
        
        self.load_data()
        
        tests = [
            self.test_otif_range,
            self.test_fill_rate_logic,
            self.test_on_time_vs_otif,
            self.test_perfect_order_subset,
            self.test_inventory_turns_positive,
            self.test_days_of_supply_reasonable,
            self.test_cost_positive,
            self.test_supplier_ranking,
            self.test_time_intelligence_ytd
        ]
        
        results = [test() for test in tests]
        
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        
        passed = sum(results)
        total = len(results)
        
        print(f"\n  Tests Passed: {passed}/{total}")
        print(f"  Pass Rate: {(passed/total)*100:.1f}%")
        
        if passed == total:
            print("\n✅ ALL KPI TESTS PASSED!")
            return True
        else:
            print(f"\n⚠️ {total - passed} TEST(S) FAILED")
            return False


def main():
    """Main function to run KPI verification."""
    tester = KPITester()
    passed = tester.run_all_tests()
    
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
