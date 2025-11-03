const noGlobalIsFiniteRule = {
  meta: {
    type: 'suggestion',
    docs: {
      description: 'Disallow use of global isFinite, use Number.isFinite instead',
      recommended: false,
    },
    fixable: 'code',
    messages: {
      useNumberIsFinite: 'Use Number.isFinite() instead of global isFinite().',
    },
    schema: [],
  },
  create(context) {
    return {
      CallExpression(node) {
        if (node.callee.type === 'Identifier' && node.callee.name === 'isFinite') {
          context.report({
            node: node.callee,
            messageId: 'useNumberIsFinite',
            fix(fixer) {
              return fixer.replaceText(node.callee, 'Number.isFinite')
            },
          })
        }
      },
    }
  },
}

export default noGlobalIsFiniteRule
