const React = require('react')

const passthrough = (name) => {
  const C = ({ children, className, ...props }) =>
    React.createElement('div', { 'data-testid': name, className, ...props }, children)
  C.displayName = name
  return C
}

module.exports = {
  Breadcrumbs: ({ children, className, separator, 'aria-label': ariaLabel, ...props }) => {
    const items = React.Children.toArray(children)
    return React.createElement('nav', { 'aria-label': ariaLabel, className },
      React.createElement('ol', { 'data-slot': 'list' },
        items.map((item, i) =>
          React.createElement(React.Fragment, { key: i },
            item,
            i < items.length - 1
              ? React.createElement('li', { 'data-slot': 'separator' }, separator)
              : null
          )
        )
      )
    )
  },
  BreadcrumbsItem: ({ children, className, isDisabled, ...props }) => React.createElement('li', { className, 'aria-disabled': isDisabled || undefined, ...props }, children),
  BreadcrumbsRoot: passthrough('BreadcrumbsRoot'),
  Button: ({ children, variant, className, ...props }) => React.createElement('button', { 'data-testid': 'dropdown-button', 'data-variant': variant, className, ...props }, children),
  ButtonRoot: passthrough('ButtonRoot'),
  Dropdown: ({ children, ...props }) => React.createElement('div', { 'data-testid': 'dropdown' }, children),
  DropdownTrigger: ({ children }) => React.createElement('div', { 'data-testid': 'dropdown-trigger' }, children),
  DropdownMenu: ({ children, onAction, selectedKeys, selectionMode, ...props }) => React.createElement('div', { 'data-testid': 'dropdown-menu', 'data-selected-keys': selectedKeys, 'data-selection-mode': selectionMode, ...props }, children),
  DropdownItem: ({ children, onPress, ...props }) => React.createElement('div', { 'data-testid': 'dropdown-item', onClick: onPress, ...props }, children),
  DropdownSection: ({ children, 'data-title': title, ...props }) => React.createElement('div', { 'data-testid': 'dropdown-section', 'data-title': title, ...props }, title ? React.createElement('span', { 'data-testid': 'dropdown-section-title' }, title) : null, children),
  DropdownRoot: passthrough('DropdownRoot'),
  DropdownPopover: passthrough('DropdownPopover'),
  Input: ({ className, id, type, value, onChange, placeholder, ...props }) => React.createElement('input', { id, type: type || 'text', value, onChange, placeholder, className }),
  InputRoot: passthrough('InputRoot'),
  Autocomplete: passthrough('Autocomplete'),
  AutocompleteRoot: passthrough('AutocompleteRoot'),
  ListBoxItem: ({ children, ...props }) => React.createElement('div', props, children),
  PaginationRoot: passthrough('PaginationRoot'),
  PaginationContent: passthrough('PaginationContent'),
  PaginationItem: passthrough('PaginationItem'),
  PaginationLink: passthrough('PaginationLink'),
  PaginationPrevious: passthrough('PaginationPrevious'),
  PaginationNext: passthrough('PaginationNext'),
  PaginationEllipsis: passthrough('PaginationEllipsis'),
  ToastProvider: () => null,
  Tooltip: passthrough('Tooltip'),
  Modal: passthrough('Modal'),
  ModalRoot: passthrough('ModalRoot'),
  ModalBody: passthrough('ModalBody'),
  ModalHeader: passthrough('ModalHeader'),
  ModalFooter: passthrough('ModalFooter'),
  ModalContent: passthrough('ModalContent'),
  ModalTrigger: passthrough('ModalTrigger'),
  Skeleton: passthrough('Skeleton'),
  Select: passthrough('Select'),
  SelectItem: passthrough('SelectItem'),
  addToast: jest.fn(),
}
