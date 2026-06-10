from backend.services.routeoptimizer.optimizer import RouteOptimizer

def test_haversine_distance():
    dist = RouteOptimizer.haversine_distance(35.6586, 139.7454, 35.7101, 139.8107)
    assert 7.5 <= dist <= 9.0

def test_optimize_activities():
    activities = [
        {"name": "Hotel", "coordinates": {"lat": 35.6586, "lng": 139.7454}},
        {"name": "Spot 1", "coordinates": {"lat": 35.7101, "lng": 139.8107}},
        {"name": "Spot 2", "coordinates": {"lat": 35.6895, "lng": 139.6917}},
    ]
    optimized = RouteOptimizer.optimize(activities)
    assert len(optimized) == 3
    assert optimized[0]["name"] == "Hotel"
    assert "timeslot" in optimized[0]
    assert "traveltonext" in optimized[0]
