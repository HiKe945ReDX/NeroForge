import numpy as np
from typing import Dict, List, Any
from ..models.simulation_models import CareerRole, SimulationResult
import asyncio

class CareerPathSimulator:
    def __init__(self):
        self.inflation_rate = 0.03
        self.savings_rate = 0.20
        self.investment_return = 0.08
    
    async def simulate_career_path(
        self, 
        current_role: CareerRole,
        target_role: CareerRole, 
        timeline_years: int,
        parameters: Dict[str, Any] = None
    ) -> List[SimulationResult]:
        
        if parameters:
            self.savings_rate = parameters.get("savings_rate", self.savings_rate)
            self.investment_return = parameters.get("investment_return", self.investment_return)
        
        results = []
        current_salary = current_role.salary
        total_savings = 0
        
        # Calculate transition point (when role changes)
        transition_year = timeline_years // 2  # Midpoint transition
        
        for year in range(1, timeline_years + 1):
            # Determine current role and salary
            if year <= transition_year:
                role_name = current_role.title
                growth_rate = current_role.growth_rate
            else:
                role_name = target_role.title
                # Salary jump at transition + growth
                if year == transition_year + 1:
                    current_salary = target_role.salary
                growth_rate = target_role.growth_rate
            
            # Apply salary growth
            if year > 1:
                current_salary *= (1 + growth_rate)
            
            # Calculate savings and investments
            annual_savings = current_salary * self.savings_rate
            total_savings = (total_savings * (1 + self.investment_return)) + annual_savings
            
            result = SimulationResult(
                year=year,
                role=role_name,
                salary=round(current_salary, 2),
                savings=round(annual_savings, 2),
                net_worth=round(total_savings, 2)
            )
            results.append(result)
        
        return results
    
    def calculate_summary(self, results: List[SimulationResult]) -> Dict[str, Any]:
        if not results:
            return {}
        
        final_result = results[-1]
        initial_salary = results[0].salary
        
        return {
            "total_years": len(results),
            "starting_salary": results[0].salary,
            "ending_salary": final_result.salary,
            "salary_growth_percentage": round(
                ((final_result.salary - initial_salary) / initial_salary) * 100, 2
            ),
            "final_net_worth": final_result.net_worth,
            "total_career_earnings": sum(r.salary for r in results),
            "career_progression": [r.role for r in results]
        }

    async def run_monte_carlo(
        self,
        current_role: CareerRole,
        target_role: CareerRole,
        timeline_years: int,
        iterations: int = 1000
    ) -> Dict[str, Any]:
        """Run Monte Carlo simulation with uncertainty"""
        
        final_salaries = []
        final_net_worths = []
        
        for _ in range(iterations):
            # Add randomness to growth rates
            modified_current = CareerRole(
                title=current_role.title,
                industry=current_role.industry,
                level=current_role.level,
                salary=current_role.salary,
                growth_rate=max(0, np.random.normal(current_role.growth_rate, 0.02))
            )
            
            modified_target = CareerRole(
                title=target_role.title,
                industry=target_role.industry, 
                level=target_role.level,
                salary=target_role.salary * np.random.uniform(0.8, 1.2),
                growth_rate=max(0, np.random.normal(target_role.growth_rate, 0.02))
            )
            
            results = await self.simulate_career_path(
                modified_current, modified_target, timeline_years
            )
            
            final_salaries.append(results[-1].salary)
            final_net_worths.append(results[-1].net_worth)
        
        return {
            "iterations": iterations,
            "salary_statistics": {
                "mean": round(np.mean(final_salaries), 2),
                "median": round(np.median(final_salaries), 2),
                "std_deviation": round(np.std(final_salaries), 2),
                "percentile_25": round(np.percentile(final_salaries, 25), 2),
                "percentile_75": round(np.percentile(final_salaries, 75), 2)
            },
            "net_worth_statistics": {
                "mean": round(np.mean(final_net_worths), 2),
                "median": round(np.median(final_net_worths), 2),
                "std_deviation": round(np.std(final_net_worths), 2),
                "percentile_25": round(np.percentile(final_net_worths, 25), 2),
                "percentile_75": round(np.percentile(final_net_worths, 75), 2)
            }
        }

career_simulator = CareerPathSimulator()
