const noGlobalNaNRule = {
  meta: {
    type: 'suggestion',
    docs: {
      description: 'Disallow use of global NaN, use Number.NaN instead',
      recommended: false,
    },
    fixable: 'code',
    messages: {
      useNumberNaN: 'Use Number.NaN instead of global NaN.',
    },
    schema: [],
  },
  create(context) {
    return {
      Identifier(node) {
        // Only report if it's 'NaN' and not already part of 'Number.NaN'
        if (node.name === 'NaN') {
          const parent = node.parent
          if (
            parent &&
            parent.type === 'MemberExpression' &&
            parent.property === node &&
            parent.object &&
            parent.object.type === 'Identifier' &&
            parent.object.name === 'Number'
          ) {
            return
          }

          context.report({
            node,
            messageId: 'useNumberNaN',
            fix(fixer) {
              return fixer.replaceText(node, 'Number.NaN')
            },
          })
        }
      },
    }
  },
}

export default noGlobalNaNRule
