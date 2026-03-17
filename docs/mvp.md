# MVP Definition

The Astrolab MVP is complete when the system can:

1. Compute planetary positions for a given UTC datetime
2. Build a Snapshot from positions
3. Detect a single aspect (opposition) between two bodies with orb
4. Reproduce a real-world claim via simulate_claim
5. Generate reproducible outputs:
   - result.json
   - report.md
6. Execute a full case from case.yaml

Out of scope:
- chart rendering
- multiple aspect types
- houses
- UI
- performance optimization