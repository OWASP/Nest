const noGlobalParseIntRule = {
  meta: {
    type: 'suggestion',
    docs: {
      description: 'Disallow use of global parseInt, use Number.parseInt instead',
      recommended: false,
    },
    fixable: 'code',
    messages: {
      useNumberParseInt: 'Use Number.parseInt() instead of global parseInt().',
    },
    schema: [],
  },
  create(context) {
    return {
      CallExpression(node) {
        if (node.callee.type === 'Identifier' && node.callee.name === 'parseInt') {
          context.report({
            node: node.callee,
            messageId: 'useNumberParseInt',
            fix(fixer) {
              return fixer.replaceText(node.callee, 'Number.parseInt')
            },
          })
        }
      },
    }
  },
}

export default noGlobalParseIntRule
