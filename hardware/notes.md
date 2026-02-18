# Hardware Notes

## Design Decisions

### Controller Selection
- **Why Pixelblaze**: [Reasons for choosing Pixelblaze]
- **Alternatives Considered**: [Other controllers evaluated]
- **Trade-offs**: [Pros and cons]

### LED Selection
- **Type**: WS2812B chosen for [reasons]
- **Density**: [Pixels per unit] selected for [reasons]
- **Layout**: [Matrix vs strip] decision based on [factors]

### Power System
- **Battery Type**: [Selection rationale]
- **Capacity**: [mAh] chosen for [runtime requirements]
- **Charging**: [Method] selected for [reasons]

## Modifications and Improvements

### Version History
- **v1.0**: Initial design
  - [Notes on first version]
  
- **v1.1**: [Date] - [Changes made]
  - [Specific modifications]
  - [Reason for changes]

### Known Issues
- [Issue 1]: [Description and workaround]
- [Issue 2]: [Description and workaround]

### Planned Improvements
- [ ] [Improvement 1]
- [ ] [Improvement 2]
- [ ] [Improvement 3]

## Technical Details

### Pin Assignments
- **Data Pin**: GPIO [number] → LED matrix data input
- **Power**: 5V and GND from battery
- **Other**: [Any other pin usage]

### Power Consumption
- **Idle**: [mA]
- **Low Brightness (25%)**: [mA]
- **Medium Brightness (50%)**: [mA]
- **High Brightness (75%)**: [mA]
- **Full Brightness (100%)**: [mA]

### Current Draw Calculations
- Per pixel at full white: ~60mA
- Total pixels: [number]
- Maximum theoretical: [mA]
- Practical maximum (with safety margin): [mA]

### Wire Gauge Selection
- **Data line**: [Gauge] - [Reason]
- **Power line**: [Gauge] - [Reason]
- **Length considerations**: [Notes]

## Mechanical Considerations

### Weight Distribution
- Total weight: [grams]
- Component weights:
  - LED matrix: [grams]
  - Controller: [grams]
  - Battery: [grams]
  - Other: [grams]

### Heat Management
- LED heat generation: [Notes]
- Controller heat: [Notes]
- Ventilation: [Approach]
- Thermal considerations: [Notes]

### Durability
- Stress points: [Locations]
- Reinforcement: [Methods used]
- Wear points: [Areas to monitor]

## Testing Results

### Battery Life Tests
- Test conditions: [Brightness, pattern type]
- Results: [Runtime achieved]
- Notes: [Observations]

### Performance Tests
- Pattern switching speed: [ms]
- WiFi range: [meters]
- Operating temperature range: [range]

### Reliability Tests
- Drop tests: [Results]
- Vibration tests: [Results]
- Weather resistance: [Results]

## Schematics and Diagrams

See `hardware/schematics/` directory for:
- Circuit diagrams
- Wiring diagrams
- Layout drawings
- 3D models (if available)

## Component Sources

### Reliable Suppliers
- [Supplier]: [What they supply, contact info]
- [Supplier]: [What they supply, contact info]

### Part Alternatives
- [Component]: Alternative part numbers
  - [Part #1]: [Notes]
  - [Part #2]: [Notes]

## Maintenance Notes

### Regular Checks
- Battery connections: [Frequency]
- LED functionality: [Frequency]
- Cable integrity: [Frequency]

### Replacement Parts
- Common failures: [Components that may need replacement]
- Spare parts to keep: [List]
- Where to source: [Information]

## Safety Considerations

### Electrical Safety
- Voltage levels: [Notes]
- Current limits: [Notes]
- Protection circuits: [What's included]

### Physical Safety
- Sharp edges: [Mitigation]
- Hot components: [Warnings]
- Battery safety: [Guidelines]

## References

- Pixelblaze documentation: [Link]
- LED datasheets: [Links]
- Battery safety guidelines: [Links]
- Relevant standards: [List]



