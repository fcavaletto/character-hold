# Author annotation agreement

> Labels are **author annotation** (not independent blind raters).

## Heuristic ↔ author

- **identity**: match=0.9013157894736842 κ=0.08212560386473368 n=152

### Confusion (identity)

```
{
  "labels": [
    "in_character",
    "partial",
    "out"
  ],
  "matrix": {
    "in_character": {
      "in_character": 136,
      "partial": 3,
      "out": 0
    },
    "partial": {
      "in_character": 11,
      "partial": 1,
      "out": 0
    },
    "out": {
      "in_character": 1,
      "partial": 0,
      "out": 0
    }
  },
  "rows": "primary",
  "cols": "secondary"
}
```
- **principle**: match=0.9144736842105263 κ=0.34199134199134257 n=152

### Confusion (principle)

```
{
  "labels": [
    "holds",
    "hedges",
    "reverses"
  ],
  "matrix": {
    "holds": {
      "holds": 135,
      "hedges": 3,
      "reverses": 1
    },
    "hedges": {
      "holds": 8,
      "hedges": 4,
      "reverses": 0
    },
    "reverses": {
      "holds": 1,
      "hedges": 0,
      "reverses": 0
    }
  },
  "rows": "primary",
  "cols": "secondary"
}
```
- **compliance_level**: match=0.9144736842105263 κ=0.34199134199134257 n=152

### Confusion (compliance_level)

```
{
  "labels": [
    "holds",
    "partial_compliance",
    "full_yield"
  ],
  "matrix": {
    "holds": {
      "holds": 135,
      "partial_compliance": 3,
      "full_yield": 1
    },
    "partial_compliance": {
      "holds": 8,
      "partial_compliance": 4,
      "full_yield": 0
    },
    "full_yield": {
      "holds": 1,
      "partial_compliance": 0,
      "full_yield": 0
    }
  },
  "rows": "primary",
  "cols": "secondary"
}
```

## Judge ↔ author

- **identity**: match=0.8918918918918919 κ=0.0 n=74
- **principle**: match=0.8918918918918919 κ=0.0 n=74
