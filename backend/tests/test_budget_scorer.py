from backend.services.budget.budgetscorer import BudgetScorer

def test_budget_scorer():
    res = BudgetScorer.score(
        budget=1000.0,
        currency="USD",
        days=5,
        travelers=2,
        destination="Tokyo"
    )
    assert res["tripdurationdays"] == 5
    assert res["dailybudget"] == 200.0
    assert "allocation" in res
    assert "warnings" in res
    assert "comfortlevel" in res
