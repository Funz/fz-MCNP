# Migration from Old Plugin-MCNP to fz-mcnp

This document describes how the old MCNP plugin was ported to the new fz framework.

## Migration Overview

### Old Structure (plugin-MCNP)
```
plugin-MCNP/
├── src/main/
│   ├── io/
│   │   └── MCNP.ioplugin          # Old configuration format
│   ├── samples/
│   │   └── godiva                  # Sample input file
│   └── scripts/
│       ├── MCNP.sh                 # Shell script for Unix/Mac
│       └── MCNP.bat                # Batch script for Windows
└── build.xml                       # Ant build file
```

### New Structure (fz-mcnp)
```
fz-mcnp/
├── .fz/
│   ├── calculators/
│   │   ├── MCNP.sh                 # Calculator script
│   │   └── Localhost_MCNP.json     # Calculator configuration
│   └── models/
│       └── MCNP.json               # Model definition
├── .gitignore
├── README.md
├── example_godiva.py               # Python example
└── godiva.inp                      # Sample input file
```

## Key Changes

### 1. Configuration Format

**Old (.ioplugin format):**
```
variableStartSymbol=%
variableLimit=(...)
formulaStartSymbol=@
formulaLimit={...}
commentLineChar=C 
output.mean_keff.get=grep("outp"," the final estimated combined") >> get(0) >> cut("keff = ",2) >> substring("ZZZ","with an estimated") >> asNumeric()
```

**New (JSON format):**
```json
{
    "id": "MCNP",
    "varprefix": "%",
    "formulaprefix": "@",
    "delim": "()",
    "commentline": "C ",
    "output": {
        "mean_keff": "grep 'the final estimated combined' outp | head -n 1 | awk '{match($0, /keff = ([0-9.]+)/, arr); print arr[1]}'"
    }
}
```

### 2. Output Parsing

**Old approach:**
- Custom parsing DSL with operators like `>>`, `cut()`, `substring()`, `asNumeric()`

**New approach:**
- Standard shell commands (grep, awk, etc.)
- More flexible and Unix-standard
- Example: `grep 'pattern' file | awk '{print $N}'`

### 3. Calculator Script

**Old script:**
```bash
#!/bin/bash
export MCNP_PATH="/Applications/MCNP6"
export DATAPATH=$MCNP_PATH"/MCNP_DATA"
ulimit -s unlimited
echo $$ >> PID
$MCNP_PATH/MCNP_CODE/bin/mcnp6 inp=$* &
PID_MCNP=$!
echo $PID_MCNP >> PID
wait $PID_MCNP
if [ -f "PID" ]; then rm -f "PID"; fi
```

**New script:**
```bash
#!/bin/bash
# Enhanced with:
# - Environment variable validation
# - Better error handling
# - Support for directory and file inputs
# - Automatic input file detection
# - Comprehensive error messages
```

### 4. Calculator Configuration

**New addition:**
```json
{
    "uri": "sh://",
    "n": 1,
    "models": {
        "MCNP": "bash .fz/calculators/MCNP.sh"
    }
}
```

This allows using the calculator by name: `calculators="Localhost_MCNP"`

## Feature Mapping

| Old Feature | New Feature | Status |
|-------------|-------------|--------|
| Variable syntax `%(...)` | Variable syntax `%(...)` | ✅ Preserved |
| Formula syntax `@{...}` | Formula syntax `@{...}` | ✅ Preserved |
| Comment char `C ` | Comment char `C ` | ✅ Preserved |
| Output: mean_keff | Output: mean_keff | ✅ Implemented |
| Output: sigma_keff | Output: sigma_keff | ✅ Implemented |
| Dataset filtering | Not applicable | ➖ Simplified |
| Output functions | Native shell commands | ✅ Enhanced |
| Shell script | Enhanced shell script | ✅ Improved |

## Improvements in New Version

1. **Better Error Handling**
   - Validates MCNP_PATH before execution
   - Checks for MCNP executable existence
   - Clear error messages

2. **Flexible Input Handling**
   - Accepts directory or file as input
   - Auto-detects MCNP input files
   - Supports multiple input patterns

3. **Standard Tools**
   - Uses standard Unix tools (grep, awk)
   - No custom DSL to learn
   - More maintainable and debuggable

4. **Python Integration**
   - Example Python script provided
   - Easy integration with fz framework
   - Pandas DataFrame output

5. **Documentation**
   - Comprehensive README
   - Example usage
   - Troubleshooting guide

## Usage Comparison

### Old Usage (Funz)
```java
// Java/Groovy code
Run r = new Run("MCNP", "godiva");
r.setInputVariable("r", 8.741);
r.execute();
Double keff = r.getOutputValue("mean_keff");
```

### New Usage (fz)
```python
import fz

results = fz.fzr(
    "godiva.inp",
    {"r": 8.741},
    "MCNP",
    calculators="Localhost_MCNP"
)
keff = results['mean_keff'][0]
```

## Migration Checklist

- [x] Port MCNP.ioplugin to MCNP.json model
- [x] Convert output parsing to shell commands
- [x] Enhance MCNP.sh calculator script
- [x] Create Localhost_MCNP.json calculator config
- [x] Migrate godiva sample file
- [x] Create comprehensive README
- [x] Add Python example script
- [x] Add .gitignore for MCNP outputs
- [x] Document migration process

## Testing Notes

To test the migrated plugin:

1. Install MCNP and set MCNP_PATH
2. Install fz framework
3. Run the example:
   ```bash
   python example_godiva.py
   ```

Expected output structure:
```
     r  mean_keff  sigma_keff  status     calculator
0  8.5     0.9850      0.0012    done  Localhost_MCNP
1  8.741   0.9995      0.0006    done  Localhost_MCNP
2  9.0     1.0145      0.0008    done  Localhost_MCNP
```

## Future Enhancements

Potential improvements for future versions:

- [ ] Support for additional MCNP output parameters
- [ ] Windows batch script calculator (MCNP.bat equivalent)
- [ ] Pre-configured remote HPC calculators
- [ ] Visualization examples for results
- [ ] Integration tests with mock MCNP outputs
- [ ] Support for MCNP5 in addition to MCNP6
