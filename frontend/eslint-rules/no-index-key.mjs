const noIndexKeyRule = {
  meta: {
    type: 'problem',
    docs: {
      description: 'Disallow use of array indexes as keys in JSX list components',
      recommended: false,
    },
    messages: {
      noIndexKey:
        'JSX list components should not use array indexes as key. Use a unique identifier from the item instead.',
    },
    schema: [],
  },
  create(context) {
    const indexNamePattern = /^(index|idx|i|pos|position|n|num|counter|j|k|ind|indx)$/i

    function isIndexVariable(identifier) {
      if (identifier.type !== 'Identifier') {
        return false
      }
      return indexNamePattern.test(identifier.name)
    }

    function hasOnlyIndexInTemplate(templateLiteral) {
      if (templateLiteral.type !== 'TemplateLiteral') {
        return false
      }

      const hasIndex = templateLiteral.expressions.some((expr) => {
        if (isIndexVariable(expr)) {
          return true
        }
        if (
          expr.type === 'MemberExpression' &&
          expr.computed === true &&
          isIndexVariable(expr.property)
        ) {
          return true
        }
        return false
      })

      if (!hasIndex) {
        return false
      }

      if (
        templateLiteral.quasis.some((quasi) => quasi.value.raw && quasi.value.raw.trim().length > 0)
      ) {
        return false
      }

      const hasOtherIdentifier = templateLiteral.expressions.some((expr) => {
        if (isIndexVariable(expr)) {
          return false
        }
        if (expr.type === 'MemberExpression' && !expr.computed) {
          return true
        }
        if (expr.type === 'CallExpression') {
          return true
        }
        if (expr.type === 'Identifier' && !isIndexVariable(expr)) {
          return true
        }
        return false
      })

      return !hasOtherIdentifier
    }

    function hasIndexVariable(node) {
      if (!node) {
        return false
      }

      if (isIndexVariable(node)) {
        return true
      }

      if (node.type === 'TemplateLiteral') {
        return node.expressions.some((expr) => {
          if (isIndexVariable(expr)) {
            return true
          }
          if (
            expr.type === 'MemberExpression' &&
            expr.computed === true &&
            isIndexVariable(expr.property)
          ) {
            return true
          }
          return hasIndexVariable(expr)
        })
      }

      if (node.type === 'MemberExpression') {
        if (node.computed === true && isIndexVariable(node.property)) {
          return true
        }
        return hasIndexVariable(node.object)
      }

      if (node.type === 'BinaryExpression') {
        return hasIndexVariable(node.left) || hasIndexVariable(node.right)
      }

      if (node.type === 'UnaryExpression') {
        return hasIndexVariable(node.argument)
      }

      if (node.type === 'CallExpression') {
        return node.arguments.some((arg) => hasIndexVariable(arg))
      }

      return false
    }

    function containsIndexVariable(node) {
      if (!node) {
        return false
      }

      if (isIndexVariable(node)) {
        return true
      }

      if (node.type === 'TemplateLiteral') {
        // If it has string parts, it's a compound key - allow it
        if (node.quasis.some((quasi) => quasi.value.raw && quasi.value.raw.trim().length > 0)) {
          return false
        }

        return hasOnlyIndexInTemplate(node)
      }

      if (node.type === 'MemberExpression') {
        if (node.computed === true && isIndexVariable(node.property)) {
          return true
        }
        return false
      }

      if (node.type === 'BinaryExpression') {
        // Check if this is a compound key (string + index or index + string)
        const hasIndex = hasIndexVariable(node.left) || hasIndexVariable(node.right)
        const hasString =
          (node.left.type === 'Literal' && typeof node.left.value === 'string') ||
          (node.right.type === 'Literal' && typeof node.right.value === 'string')

        if (hasIndex && hasString) {
          return false
        }

        return hasIndex || hasString
      }

      if (node.type === 'UnaryExpression') {
        return containsIndexVariable(node.argument)
      }

      if (node.type === 'CallExpression') {
        return node.arguments.some((arg) => containsIndexVariable(arg))
      }

      return false
    }

    return {
      JSXOpeningElement(node) {
        const keyAttribute = node.attributes.find(
          (attr) => attr.type === 'JSXAttribute' && attr.name.name === 'key'
        )

        if (keyAttribute && keyAttribute.value) {
          let keyValue = null
          if (keyAttribute.value.type === 'JSXExpressionContainer') {
            keyValue = keyAttribute.value.expression
          } else if (keyAttribute.value.type === 'Literal') {
            return
          } else {
            keyValue = keyAttribute.value
          }

          if (keyValue && containsIndexVariable(keyValue)) {
            context.report({
              node: keyAttribute,
              messageId: 'noIndexKey',
            })
          }
        }
      },
    }
  },
}

export default noIndexKeyRule
