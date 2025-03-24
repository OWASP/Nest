import { defineConfig } from "@chakra-ui/react"

const customTheme = defineConfig({
  globalCss: {
    "html, body": {
      margin: 0,
      padding: 0,
    },
  },
})

export default customTheme