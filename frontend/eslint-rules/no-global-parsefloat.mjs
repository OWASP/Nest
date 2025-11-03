const noGlobalParseFloatRule = {
  meta: {
    type: 'suggestion',
    docs: {
      description: 'Disallow use of global parseFloat, use Number.parseFloat instead',
      recommended: false,
    },
    fixable: 'code',
    messages: {
      useNumberParseFloat: 'Use Number.parseFloat() instead of global parseFloat().',
    },
    schema: [],
  },
  create(context) {
    return {
      CallExpression(node) {
        if (node.callee.type === 'Identifier' && node.callee.name === 'parseFloat') {
          context.report({
            node: node.callee,
            messageId: 'useNumberParseFloat',
            fix(fixer) {
              return fixer.replaceText(node.callee, 'Number.parseFloat')
            },
          })
        }
      },
    }
  },
}

export default noGlobalParseFloatRule
