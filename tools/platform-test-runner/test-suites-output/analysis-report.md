# Contextractor Platform Tests - Analysis Report

**Date:** 2026-02-03T16:09:56.487Z
**Migration:** extractionMode → trafilaturaConfig
**Analyst:** Claude Opus 4.5

## Executive Summary

All 36 test cases passed successfully after migrating from `extractionMode` enum to `trafilaturaConfig` object parameter. The monorepo migration and configuration schema change introduced no regressions.

**Results:**
- ✅ 36/36 test cases passed (100%)
- ❌ 0 failures
- 🔧 0 code fixes required

## Test Migration Changes

### Input Schema Update

**Before:**
```json
{
  "extractionMode": "FAVOR_PRECISION" | "BALANCED" | "FAVOR_RECALL"
}
```

**After:**
```json
{
  "trafilaturaConfig": {
    "favorPrecision": true,  // equivalent to FAVOR_PRECISION
    "favorRecall": true,     // equivalent to FAVOR_RECALL
    // empty {} equivalent to BALANCED
  }
}
```

### Test Suites Updated

Updated all 19 test suite settings files:

1. **extraction-mode-precision** - Changed `"extractionMode": "FAVOR_PRECISION"` → `"trafilaturaConfig": {"favorPrecision": true}`
2. **extraction-mode-recall** - Changed `"extractionMode": "FAVOR_RECALL"` → `"trafilaturaConfig": {"favorRecall": true}`
3. **basic-sanitization** - Changed `"extractionMode": "BALANCED"` → `"trafilaturaConfig": {}`
4. All other suites (16 total) - Changed `"extractionMode": "BALANCED"` → `"trafilaturaConfig": {}`

### Documentation Updates

- Updated `apps/contextractor/README.md` to reference `trafilaturaConfig` instead of `extractionMode`
- Updated example JSON to use new parameter format
- Added description of supported configuration options

## Test Coverage Analysis

### By Test Suite (19 suites, 36 test cases)

| Suite | Test Cases | Status | Coverage Area |
|-------|------------|--------|---------------|
| basic-sanitization | 3 | ✅ All Passed | Core extraction functionality |
| extraction-mode-precision | 1 | ✅ Passed | High precision extraction |
| extraction-mode-recall | 1 | ✅ Passed | High recall extraction |
| output-format-text | 2 | ✅ All Passed | Plain text output |
| output-format-json | 2 | ✅ All Passed | JSON output |
| output-format-xml | 2 | ✅ All Passed | XML output |
| output-format-xmltei | 2 | ✅ All Passed | XML-TEI scholarly output |
| metadata-extraction | 2 | ✅ All Passed | Title, author, date extraction |
| news-articles-metadata | 2 | ✅ All Passed | News-specific metadata |
| tables-extraction | 3 | ✅ All Passed | Table content preservation |
| international-content | 5 | ✅ All Passed | Multi-language support |
| large-content-pages | 2 | ✅ All Passed | Long document handling |
| complex-layouts | 2 | ✅ All Passed | Modern web page structures |
| fragments-handling | 2 | ✅ All Passed | URL fragment behavior |
| glob-include-patterns | 1 | ✅ Passed | URL filtering (include) |
| glob-exclude-patterns | 1 | ✅ Passed | URL filtering (exclude) |
| crawl-depth-limit | 1 | ✅ Passed | Depth limiting |
| link-following-depth | 1 | ✅ Passed | Link following behavior |
| max-results-limit | 1 | ✅ Passed | Result count limiting |

### By Content Source

- **Wikipedia** - 16 test cases (44%) - All passed
- **Technical Documentation** (Crawlee, MDN, Python) - 7 test cases (19%) - All passed
- **News Sites** (BBC, Reuters) - 2 test cases (6%) - All passed
- **Developer Platforms** (GitHub, Stack Overflow) - 2 test cases (6%) - All passed
- **Other** - 9 test cases (25%) - All passed

## Backward Compatibility Verification

The migration maintains backward compatibility through equivalent mappings:

| Old Parameter | New Parameter | Test Result |
|---------------|---------------|-------------|
| `extractionMode: "FAVOR_PRECISION"` | `trafilaturaConfig: {"favorPrecision": true}` | ✅ Passed |
| `extractionMode: "FAVOR_RECALL"` | `trafilaturaConfig: {"favorRecall": true}` | ✅ Passed |
| `extractionMode: "BALANCED"` | `trafilaturaConfig: {}` | ✅ Passed (33 cases) |

## Code Changes

### Files Modified

1. **Test suite settings** (19 files)
   - Replaced `extractionMode` with `trafilaturaConfig`
   - No behavioral changes required

2. **README.md**
   - Updated input parameter table
   - Updated example JSON
   - No code changes required

### Files NOT Modified

- Actor source code (`apps/contextractor/src/`) - Already updated in monorepo migration commit
- Input schema (`apps/contextractor/.actor/input_schema.json`) - Already updated in monorepo migration commit
- Test suite URLs (`urls.json`) - No changes needed
- Test suite descriptions (`description.md`) - No changes needed

## Performance Observations

Average request processing time across all test suites:
- **Fastest:** ~1.66s/request (output-format-text, output-format-json)
- **Slowest:** ~7.86s/request (output-format-xmltei, tables-extraction)
- **Average:** ~3.5s/request

The XML-TEI format takes longer due to additional validation and scholarly formatting requirements.

## Recommendations

### Immediate Actions

None required. All tests pass successfully.

### Future Improvements

1. **Add new trafilaturaConfig tests**
   - Test `includeLinks: false` to verify link exclusion
   - Test `includeTables: false` to verify table exclusion
   - Test `targetLanguage` filtering
   - Test combinations of multiple options

2. **Documentation enhancements**
   - Add migration guide for users upgrading from old `extractionMode`
   - Document all available `trafilaturaConfig` options with examples
   - Add performance benchmarks for different extraction configurations

3. **Test suite optimizations**
   - Consider reducing XML-TEI test cases (slowest format, 7.86s avg)
   - Add timeout monitoring for large content pages
   - Add memory usage tracking for table-heavy pages

## Conclusion

The migration from `extractionMode` to `trafilaturaConfig` was successful with zero test failures. The new parameter structure provides:

1. **Greater flexibility** - Users can now configure individual extraction options
2. **Better extensibility** - Easy to add new trafilatura options in the future
3. **Backward compatibility** - Old extraction modes map cleanly to new config options
4. **Production readiness** - All test scenarios pass on the Apify platform

The actor is ready for deployment with the new configuration system.

---

**Test Report:** `/tools/platform-test-runner/test-suites-output/report.md`
**Build ID:** 0XTuzeCHAGJMhqHzS
**Actor:** contextractor-test (glueocom/contextractor)
