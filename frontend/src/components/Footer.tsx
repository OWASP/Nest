import { Box, Button, Heading, Link, List, Text } from '@chakra-ui/react'
import { faChevronDown, faChevronUp } from '@fortawesome/free-solid-svg-icons'
import { faGithub, faSlack, faBluesky } from '@fortawesome/free-brands-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { useState, useCallback } from 'react'
import { Section } from 'types/section'
import { footerSections } from 'utils/constants'

export default function Footer() {
  // State to keep track of the open section in the footer
  const [openSection, setOpenSection] = useState<string | null>(null)

  // Function to toggle the section open/closed
  const toggleSection = useCallback((title: string) => {
    // If the section is already open, close it, otherwise open it
    setOpenSection((prev) => (prev === title ? null : title))
  }, [])

  // Social media links configuration
  const socialLinks = [
    {
      icon: faBluesky,
      href: 'https://bsky.app/profile/nest.owasp.org',
      label: 'Bluesky'
    },
    {
      icon: faGithub,
      href: 'https://github.com/owasp/nest',
      label: 'GitHub'
    },
    {
      icon: faSlack,
      href: 'https://owasp.slack.com/archives/project-nest',
      label: 'Slack'
    }
  ]

  return (
    <Box
      as="footer"
      className="mt-auto w-full border-t bg-slate-200 dark:bg-slate-800 xl:max-w-full"
    >
      <Box className="grid w-full place-content-center gap-12 px-4 py-4 text-slate-800 dark:text-slate-200 md:py-8">
        <Box className="grid w-full sm:grid-cols-2 sm:gap-20 md:grid-cols-4">
          {/* Existing footer sections */}
          {footerSections.map((section: Section) => (
            <Box key={section.title} className="space-y-4">
              <Button
                onClick={() => toggleSection(section.title)}
                className="flex w-full items-center justify-between text-left text-lg font-semibold focus:outline-none focus:ring-slate-400 lg:cursor-default"
                aria-expanded={openSection === section.title}
                aria-controls={`footer-section-${section.title}`}
              >
                <Heading as="h3">{section.title}</Heading>
                {/* Icon to indicate open/close state */}
                <Box className="transition-transform duration-200 lg:hidden">
                  {openSection === section.title ? (
                    <FontAwesomeIcon icon={faChevronUp} className="h-4 w-4" />
                  ) : (
                    <FontAwesomeIcon icon={faChevronDown} className="h-4 w-4" />
                  )}
                </Box>
              </Button>
              <List.Root
                id={`footer-section-${section.title}`}
                className={`space-y-2 overflow-hidden text-sm transition-all duration-300 ease-in-out lg:max-h-full ${
                  openSection === section.title ? 'max-h-96' : 'max-h-0 lg:max-h-full'
                }`}
              >
                {/* Existing section links */}
                {section.links.map((link, index) => (
                  <List.Item key={index} className="py-1">
                    {link.isSpan ? (
                      <Box as="span" className="text-slate-600 dark:text-slate-400">
                        {link.text}
                      </Box>
                    ) : (
                      <Link
                        target="_blank"
                        className="text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-slate-100"
                        href={link.href}
                      >
                        {link.text}
                      </Link>
                    )}
                  </List.Item>
                ))}
              </List.Root>
            </Box>
          ))}
        </Box>
        
        {/* Social Media Icons Section */}
        <Box className="flex justify-center space-x-6 mb-0">
          {socialLinks.map((social) => (
            <Link
              key={social.label}
              href={social.href}
              target="_blank"
              rel="noopener noreferrer"
              aria-label={`OWASP Nest ${social.label}`}
              className="text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-slate-100 transition-colors duration-200"
            >
              <FontAwesomeIcon icon={social.icon} className="h-6 w-6" />
            </Link>
          ))}
        </Box>

        {/* Footer bottom section with copyright and links */}
        <Box className="grid w-full place-content-center">
          <Box className="flex w-full flex-col items-center gap-4 sm:flex-row sm:text-left">
            <Text className="text-sm text-slate-600 dark:text-slate-400">
              ©{' '}
              <Box as="span" id="year">
                {new Date().getFullYear()}
              </Box>{' '}
              OWASP Nest. All rights reserved.
            </Text>
          </Box>
        </Box>
      </Box>
    </Box>
  )
}