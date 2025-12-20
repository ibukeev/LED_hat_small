# Firmware Documentation

## Overview

This directory contains Pixelblaze pattern files (.pe format) and related firmware for the LED Hat Small project.

## Directory Structure

```
firmware/
├── README.md           # This file
├── patterns/           # Pattern files (.pe)
│   ├── aurora.pe      # Aurora/northern lights effect
│   ├── waves.pe       # Wave patterns
│   └── ...            # Additional patterns
└── presets/           # Pattern presets and configurations
    ├── default.json   # Default preset configuration
    └── ...           # Additional presets
```

## Pattern Files

### Uploading Patterns

1. Connect to Pixelblaze web interface
2. Navigate to Pattern Editor
3. Copy pattern code from `.pe` files
4. Paste into editor
5. Click "Save" to store in flash

### Pattern Naming Convention

- Use descriptive names: `aurora.pe`, `rainbow-wave.pe`
- Include version if needed: `pattern-v2.pe`
- Group related patterns: `waves-*.pe`

## Available Patterns

### Aurora (`patterns/aurora.pe`)
- Northern lights effect
- Smooth color transitions
- Configurable speed and colors

### Waves (`patterns/waves.pe`)
- Ocean wave simulation
- Multiple wave layers
- Adjustable wave parameters

### [Add more patterns as created]

## Pattern Development

### Pixelblaze Expression Language

Pixelblaze uses a custom expression language. Key features:
- Built-in variables: `time`, `pixelCount`, `x`, `y`
- Functions: `sin()`, `cos()`, `hsv()`, `rgb()`
- Pattern structure: render function called per frame

### Pattern Template

```javascript
// Pattern: [Pattern Name]
// Description: [Brief description]

export function render(index) {
  // Pattern code here
  hsv(time * 0.1 + index * 0.01, 1, 1)
}
```

### Best Practices

1. **Performance**: Keep calculations efficient
2. **Variables**: Use exported variables for user control
3. **Comments**: Document complex logic
4. **Testing**: Test at different brightness levels
5. **Optimization**: Minimize memory usage

## Presets

Presets store pattern configurations including:
- Selected pattern
- Brightness level
- Speed setting
- Color scheme
- Other pattern-specific parameters

### Creating Presets

1. Configure pattern settings in web interface
2. Export preset configuration
3. Save as JSON file in `presets/` directory
4. Share with others or restore later

## Pattern Library

### Recommended Patterns

- **Aurora**: Smooth, organic feel
- **Waves**: Dynamic, flowing motion
- **Fire**: Warm, flickering effect
- **Matrix**: Digital rain effect
- **Stars**: Twinkling starfield

### Pattern Sources

- Pixelblaze pattern library: [Link]
- Community patterns: [Link]
- Custom creations: [This repository]

## Troubleshooting

### Pattern Won't Upload
- Check file format (.pe)
- Verify syntax is correct
- Check flash memory space

### Pattern Runs Slowly
- Optimize calculations
- Reduce pixel count in calculations
- Simplify color math

### Pattern Uses Too Much Power
- Reduce brightness
- Simplify pattern logic
- Use fewer active pixels

## Resources

- [Pixelblaze Documentation](https://electromage.com/docs)
- [Pattern Expression Language Reference](https://electromage.com/docs/pattern-language)
- [Pattern Examples](https://electromage.com/patterns)

## Contributing Patterns

When adding new patterns:
1. Test thoroughly
2. Document parameters
3. Include usage notes
4. Add to this README


