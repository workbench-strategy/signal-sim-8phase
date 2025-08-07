# 8-Phase Signal Controller - Intersection Layout

## Intersection Diagram

```
                    NORTH
                ┌─────────────┐
                │             │
                │   Phase 3   │
                │ Northbound  │
                │   Through   │
                │             │
    WEST ───────┼─────────────┼─────── EAST
                │             │
                │   Phase 8   │
                │ Southbound  │
                │   Through   │
                │             │
                └─────────────┘
                    SOUTH

Detailed Layout:
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│                    NORTH LEG                                │
│              ┌─────────────┐                               │
│              │ Phase 1     │                               │
│              │ Northbound  │                               │
│              │ Left        │                               │
│              └─────────────┘                               │
│              ┌─────────────┐                               │
│              │ Phase 6     │                               │
│              │ Southbound  │                               │
│              │ Left        │                               │
│              └─────────────┘                               │
│                                                             │
│  WEST LEG    ┌─────────────┐    EAST LEG                   │
│              │ Phase 5     │    ┌─────────────┐            │
│              │ Westbound   │    │ Phase 2     │            │
│              │ Left        │    │ Eastbound   │            │
│              └─────────────┘    │ Left        │            │
│              ┌─────────────┐    └─────────────┘            │
│              │ Phase 4     │    ┌─────────────┐            │
│              │ Westbound   │    │ Phase 7     │            │
│              │ Through     │    │ Eastbound   │            │
│              └─────────────┘    │ Through     │            │
│                                 └─────────────┘            │
│                    SOUTH LEG                                │
│              ┌─────────────┐                               │
│              │ Phase 3     │                               │
│              │ Northbound  │                               │
│              │ Through     │                               │
│              └─────────────┘                               │
│              ┌─────────────┐                               │
│              │ Phase 8     │                               │
│              │ Southbound  │                               │
│              │ Through     │                               │
│              └─────────────┘                               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Intersection Leg Arrangement

### North Leg (Phases 1 & 6)
- **Phase 1**: Northbound Left (Protected)
- **Phase 6**: Southbound Left (Protected)

### South Leg (Phases 3 & 8)  
- **Phase 3**: Northbound Through
- **Phase 8**: Southbound Through

### East Leg (Phases 2 & 7)
- **Phase 2**: Eastbound Left (Protected)
- **Phase 7**: Eastbound Through

### West Leg (Phases 5 & 4)
- **Phase 5**: Westbound Left (Protected)
- **Phase 4**: Westbound Through

## Opposite Leg Pairs

1. **Phases 1 & 6**: North Leg - Left turns from both directions
2. **Phases 2 & 5**: East/West Leg - Left turns from both directions  
3. **Phases 3 & 8**: South Leg - Through movements from both directions
4. **Phases 7 & 4**: East/West Leg - Through movements from both directions

## Signal Timing Logic

- Protected left turns (Phases 1, 2, 5, 6) run in parallel with through movements from opposite legs
- This arrangement maximizes intersection capacity by allowing compatible movements to run simultaneously
- The dual-ring controller allows for flexible phase sequencing while maintaining safety