const noGlobalIsNaNRule = {
  meta: {
    type: 'suggestion',
    docs: {
      description: 'Disallow use of global isNaN, use Number.isNaN instead',
      recommended: false,
    },
    fixable: 'code',
    messages: {
      useNumberIsNaN: 'Use Number.isNaN() instead of global isNaN().',
    },
    schema: [],
  },
  create(context) {
    return {
      CallExpression(node) {
        if (node.callee.type === 'Identifier' && node.callee.name === 'isNaN') {
          context.report({
            node: node.callee,
            messageId: 'useNumberIsNaN',
            fix(fixer) {
              return fixer.replaceText(node.callee, 'Number.isNaN')
            },
          })
        }
      },
    }
  },
}

export default noGlobalIsNaNRule
