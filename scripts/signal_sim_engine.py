# signal_sim_engine.py

# 8-phase NEMA dual-ring signal controller logic
# Simulates timing sequences for protected/permissive lefts,
# pedestrian LPIs, and flashing yellows.
# 
# Intersection Layout:
#     Phase 3 (Northbound Through)     Phase 8 (Southbound Through)
#     Phase 1 (Northbound Left)        Phase 6 (Southbound Left)
#     
#     Phase 2 (Eastbound Left)         Phase 5 (Westbound Left)
#     Phase 7 (Eastbound Through)      Phase 4 (Westbound Through)

def simulate_cycle():
    print("=== 8-Phase Signal Controller - Intersection Layout ===")
    print()
    print("Intersection Leg Arrangement:")
    print("North Leg:  Phase 1 (Northbound Left) + Phase 6 (Southbound Left)")
    print("South Leg:  Phase 8 (Southbound Through) + Phase 3 (Northbound Through)")
    print("East Leg:   Phase 2 (Eastbound Left) + Phase 7 (Eastbound Through)")
    print("West Leg:   Phase 5 (Westbound Left) + Phase 4 (Westbound Through)")
    print()
    
    # Phase descriptions with intersection leg context
    phases = {
        1: "Northbound Left (Protected) - North Leg",
        2: "Eastbound Left (Protected) - East Leg", 
        3: "Northbound Through - South Leg",
        4: "Westbound Through - West Leg",
        5: "Westbound Left (Protected) - West Leg",
        6: "Southbound Left (Protected) - North Leg",
        7: "Eastbound Through - East Leg",
        8: "Southbound Through - South Leg"
    }
    
    print("Phase Sequence:")
    for phase_num, description in phases.items():
        print(f"Phase {phase_num}: {description}")
    
    print()
    print("Opposite Leg Pairs:")
    print("- Phases 1 & 6: North Leg (Northbound/Southbound Left)")
    print("- Phases 2 & 5: East/West Leg (Eastbound/Westbound Left)")
    print("- Phases 3 & 8: South Leg (Northbound/Southbound Through)")
    print("- Phases 7 & 4: East/West Leg (Eastbound/Westbound Through)")
    
    # Logic placeholder for timing sequences
    print()
    print("Timing Logic: Protected left turns run in parallel with through movements")
    print("from opposite legs to maximize intersection capacity.")

if __name__ == '__main__':
    simulate_cycle()