# 8-Phase Signal Controller - WSDOT DM 1330 Layout

Reference: [1330.pdf](1330.pdf). **Through + left phase numbers sum to 7 (major) or 11 (minor) per approach.**

## Major street (sum = 7)

| Approach | Through | Left | Sum |
|----------|---------|------|-----|
| Northbound | 2 | 5 | 7 |
| Southbound | 6 | 1 | 7 |

## Minor street (sum = 11)

| Approach | Through | Left | Sum |
|----------|---------|------|-----|
| Westbound | 4 | 7 | 11 |
| Eastbound | 8 | 3 | 11 |

## ASCII layout (left, then through on each leg)

```
               [5: NB Left]  [2: NB Thru]
[7: WB Left]  [4: WB Thru]    [3: EB Left]  [8: EB Thru]
               [1: SB Left]  [6: SB Thru]
```

## Approach pairs (concurrent / preemption)

- **NB:** phases 2 + 5 (Channel A)
- **SB:** phases 1 + 6 (Channel C)
- **WB:** phases 4 + 7 (Channel B)
- **EB:** phases 3 + 8 (Channel D)

## Demo timing sequence

1. Major lefts: 1 + 5
2. Major through: 2 + 6
3. Minor through: 4 + 8
4. Minor lefts: 3 + 7

Run: `python src/cli/main.py run`
