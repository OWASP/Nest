import { Box, Button, Collapse, Container, Flex, Grid, Link, Stack, Text } from '@chakra-ui/react'
import { faChevronDown, faChevronUp } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { useCallback, useState } from 'react'
import { Section } from 'types/section'
import { footerSections } from 'utils/constants'

export default function Footer() {
  const [openSection, setOpenSection] = useState<string | null>(null)

  const toggleSection = useCallback((title: string) => {
    setOpenSection((prev) => (prev === title ? null : title))
  }, [])

  return (
    <Box as="footer" mt="auto" w="full" borderTop="1px" borderColor="gray.300" bg="gray.100" _dark={{ bg: 'gray.800', borderColor: 'gray.700' }}>
      <Container maxW="container.xl" py={8}>
        <Grid templateColumns={{ base: '1fr', sm: 'repeat(2, 1fr)', md: 'repeat(4, 1fr)' }} gap={10}>
          {footerSections.map((section: Section) => (
            <Box key={section.title}>
              <Button
                variant="ghost"
                onClick={() => toggleSection(section.title)}
                w="full"
                justifyContent="space-between"
                fontSize="lg"
                fontWeight="semibold"
                textAlign="left"
                aria-expanded={openSection === section.title}
                rightIcon={<FontAwesomeIcon icon={openSection === section.title ? faChevronUp : faChevronDown} />}
                _focus={{ boxShadow: 'outline' }}
                _hover={{ bg: 'gray.200' }}
              >
                {section.title}
              </Button>
              <Collapse in={openSection === section.title} animateOpacity>
                <Stack as="ul" spacing={2} mt={2} pl={4}>
                  {section.links.map((link, index) => (
                    <Box as="li" key={index}>
                      {link.isSpan ? (
                        <Text fontSize="sm" color="gray.600" _dark={{ color: 'gray.400' }}>
                          {link.text}
                        </Text>
                      ) : (
                        <Link href={link.href} isExternal fontSize="sm" color="blue.600" _dark={{ color: 'blue.300' }} _hover={{ textDecoration: 'underline' }}>
                          {link.text}
                        </Link>
                      )}
                    </Box>
                  ))}
                </Stack>
              </Collapse>
            </Box>
          ))}
        </Grid>

        <Flex justify="center" mt={6} textAlign="center">
          <Text fontSize="sm" color="gray.600" _dark={{ color: 'gray.400' }}>
            © {new Date().getFullYear()} OWASP Nest. All rights reserved.
          </Text>
        </Flex>
      </Container>
    </Box>
  )
}
