/**
 * Jest transformer for handling ES modules and other transformations
 */

module.exports = {
  process(sourceText, sourcePath) {
    // Simple transformer that returns source as-is
    // Add any necessary transformations here
    return {
      code: sourceText,
    };
  },
};