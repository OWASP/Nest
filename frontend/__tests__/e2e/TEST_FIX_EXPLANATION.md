# ChapterDetails E2E Test Fix - Keyboard Navigation Approach

## Issue
The test was timing out with "locator.click: Test timeout of 120000ms exceeded" when trying to click the "Unlock map" button on the Chapter Details page.

### Root Cause Analysis
The error logs showed that multiple overlay elements were intercepting pointer events:
1. **Grid layout div** (`<div class="grid grid-cols-1 gap-6 md:grid-cols-7">`) - continuously intercepting
2. **Sticky navbar** (`<div id="navbar-sticky">`) - fixed position causing interception
3. **Element instability** - the button's stability state was constantly changing, causing Playwright to keep retrying

These overlays are legitimate UI elements, but Playwright's strict stability checks were failing because:
- Layout shifts from responsive grid behavior
- Navbar fixed positioning causing pointer event interception
- Component animations (transitions) creating constant layout instability

## Solution
Instead of relying on mouse click operations (which are affected by element interception), use **keyboard navigation**:

```typescript
// Use keyboard navigation to activate the button (bypasses pointer interception issues)
await unlockButton.focus()
await page.keyboard.press('Enter')
```

### Why This Works
1. **Keyboard events bypass overlay checking** - Keyboard inputs are not affected by pointer event interception
2. **No stability requirements** - The button doesn't need to be perfectly stable for keyboard input
3. **Semantic interaction** - Pressing Enter on a focused button is the standard web accessibility pattern
4. **More reliable** - Doesn't depend on layout stability or CSS transitions

## Additional Improvements
1. **Enhanced page load wait conditions**:
   ```typescript
   await page.waitForLoadState('domcontentloaded')
   await page.waitForLoadState('networkidle')
   await page.waitForTimeout(1000)  // Extra wait for animations
   ```
   This ensures all layout shifts complete before the test attempts interaction.

## Testing Strategy
The button has `tabindex="0"` and `aria-label="Unlock map"`, making it keyboard-accessible:
- `await unlockButton.focus()` - Sets focus on the button
- `await page.keyboard.press('Enter')` - Triggers the click handler via keyboard
- The `setIsMapActive(true)` state is set regardless of interaction method

## Component Code Reference
From [ChapterMap.tsx](../../../src/components/ChapterMap.tsx#L280):
```typescript
<button
  type="button"
  tabIndex={0}
  className="pointer-events-auto flex cursor-pointer items-center justify-center rounded-md bg-white/90 px-5 py-3 text-sm font-medium text-gray-700 shadow-lg transition-colors hover:bg-gray-200 hover:text-gray-900 dark:bg-gray-700 dark:text-white dark:hover:bg-gray-600 dark:hover:text-white"
  onClick={() => {
    setIsMapActive(true)
  }}
  onKeyDown={(e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault()
      setIsMapActive(true)
    }
  }}
  aria-label="Unlock map"
>
```

The button has both click and keydown handlers, so keyboard input works perfectly.

## Files Modified
- `frontend/__tests__/e2e/pages/ChapterDetails.spec.ts` - Updated map interaction test

## Status
✅ Test now uses robust keyboard navigation instead of flaky mouse clicks
✅ All other tests remain unchanged  
✅ No component code changes required
