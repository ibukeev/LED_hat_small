# Assembly Instructions

## Pre-Assembly Checklist

- [ ] All components received and verified
- [ ] Tools prepared and ready
- [ ] Workspace cleared and organized
- [ ] Safety equipment ready (safety glasses, etc.)

## Step 1: Prepare LED Matrix

1. **Measure and Cut** (if using strip)
   - Measure required length for hat
   - Cut at designated cut points (every 3 LEDs typically)
   - Note: Cutting between pixels, not through them

2. **Test LED Matrix**
   - Connect to Pixelblaze temporarily
   - Upload test pattern
   - Verify all pixels work correctly
   - Check for any dead pixels

3. **Prepare Connections**
   - Strip wire ends for data and power
   - Tin wire ends with solder
   - Attach connectors if using

## Step 2: Prepare Power System

1. **Battery Pack Setup**
   - Verify battery voltage with multimeter
   - Attach JST connector to battery leads
   - Test battery capacity if possible

2. **Power Distribution**
   - Plan power routing to LED matrix
   - Ensure adequate wire gauge for current
   - Add inline power switch on the positive battery lead
   - Insulate each splice with heat shrink or equivalent

3. **On/Off Button Installation**
   - Use a latching 2-pin inline switch so the hat can be powered down without unplugging the battery
   - Current installed switch: JIA Teng KAN-28 self-lock micro push button, 1.5A 250V, 18 x 12 mm
   - Wire the switch in series with the positive power lead, not the ground lead
   - Mount or secure the switch so fabric movement does not pull directly on the solder joints
   - See `hardware/schematics/on-off-button-installed.jpg` for the current installed example

3. **Charging Circuit**
   - Install charging module
   - Route charging port to accessible location
   - Test charging functionality

## Step 3: Install Pixelblaze Controller


## Step 4: Integrate with Hat


## Step 5: Final Assembly


## Step 6: Testing


## Step 7: Final Adjustments


## Safety Notes

- Always disconnect power before making connections
- Verify polarity before connecting power
- Use appropriate wire gauge for current
- Protect battery from short circuits
- Test in safe environment first

## Troubleshooting

See `build/troubleshooting.md` for common issues and solutions.


