import { tooltipAnatomy } from '@ark-ui/react'
import { createSystem, defaultConfig, defineConfig, defineSlotRecipe } from '@chakra-ui/react'

export const TooltipRecipe = defineSlotRecipe({
  slots: tooltipAnatomy.keys(),
  base: {
    content: {
      '--tooltip-bg': 'colors.bg.inverted',
      bg: 'var(--tooltip-bg)',
      color: 'fg.inverted',
      borderRadius: 'sm',
      fontWeight: 'normal',
      textStyle: 'sm',
      px: '2.5 !important',
      py: '1 !important',
      width: 'max-content',
      zIndex: '100',
      _open: {
        animationStyle: 'scale-fade-in',
        animationDuration: 'fast',
      },
      _closed: {
        animationStyle: 'scale-fade-out',
        animationDuration: 'fast',
      },
    },
    arrow: {
      '--arrow-size': 'sizes.2',
      '--arrow-background': 'var(--tooltip-bg)',
    },
    arrowTip: {
      borderTopWidth: '1px',
      borderInlineStartWidth: '1px',
      borderColor: 'var(--tooltip-bg)',
    },
  },
  className: 'chakra-tooltip',
})

export const customConfig = defineConfig({
  theme: {
    slotRecipes: {
      tooltip: TooltipRecipe,
    },
  },
})

export const system = createSystem(defaultConfig, customConfig)
