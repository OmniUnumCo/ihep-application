# Fragmented Code

This folder contains code that has been moved here for one of the following reasons:

1. **Superseded**: Newer implementations exist elsewhere in the codebase
2. **Utility Scripts**: Standalone scripts not part of the main application
3. **Experimental**: Prototype or experimental code not ready for production
4. **Reference**: Code kept for reference but not actively used

## Contents

### JavaScript Files

- `ai_studio_code.js` - Simple React Three Fiber viewer (superseded by DigitalTwinCanvas.tsx)
- `dt-rendering-optimization.js` - Standalone optimization patterns demo

### Utility Folders

- `proposal-mailer/` - Investor outreach email scripts (utility, not part of main app)

## Usage

Code in this folder should NOT be imported by the main application. If you need functionality from these files:

1. Review the code to understand its purpose
2. Extract and integrate the relevant parts into the appropriate location
3. Ensure proper TypeScript typing and testing
4. Remove the file from fragmented once integrated

## Cleanup Policy

Files in this folder may be deleted if:
- They have been fully integrated elsewhere
- They are no longer relevant to the project
- They have been superseded by better implementations
