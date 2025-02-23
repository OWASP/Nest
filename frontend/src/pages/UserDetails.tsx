import {
  Box,
  Button,
  Avatar as ChakraAvatar,
  Divider as ChakraDivider,
  Flex,
  Grid,
  GridItem,
  HStack,
  Link,
  Text,
  VStack,
  useColorModeValue,
} from '@chakra-ui/react'
import React from 'react' // ✅ Added React import
import { FaGithub, FaLinkedin, FaTwitter } from 'react-icons/fa'
import { UserDetailsProps } from 'types/user'

interface UserDetailsPageProps {
  user: UserDetailsProps
}

const UserDetailsPage: React.FC<UserDetailsPageProps> = ({ user }) => {
  const bgColor = useColorModeValue('white', 'gray.800')
  const textColor = useColorModeValue('gray.800', 'gray.200')

  return (
    <Box maxW="4xl" mx="auto" p={6} bg={bgColor} color={textColor}>
      <Flex alignItems="center" justifyContent="center" flexDirection="column">
        <ChakraAvatar size="2xl" name={user.name} src={user.avatarUrl} mb={4} />
        <Text fontSize="2xl" fontWeight="bold">
          {user.name}
        </Text>
        <Text fontSize="md" color="gray.500">
          {user.email}
        </Text>
      </Flex>

      <ChakraDivider my={6} />

      <VStack spacing="4" align="flex-start">
        <Text fontSize="lg" fontWeight="semibold">
          Bio
        </Text>
        <Text color="gray.600">{user.bio}</Text>
      </VStack>

      <ChakraDivider my={6} />

      <VStack spacing="4" align="flex-start">
        <Text fontSize="lg" fontWeight="semibold">
          Social Links
        </Text>
        <HStack spacing="4">
          {user.github && (
            <Link href={user.github} target="_blank" rel="noopener noreferrer">
              <Button
                display="flex"
                alignItems="center"
                gap={2}
                colorScheme="gray"
                variant="outline"
              >
                <FaGithub />
                GitHub
              </Button>
            </Link>
          )}
          {user.linkedin && (
            <Link href={user.linkedin} target="_blank" rel="noopener noreferrer">
              <Button
                display="flex"
                alignItems="center"
                gap={2}
                colorScheme="blue"
                variant="outline"
              >
                <FaLinkedin />
                LinkedIn
              </Button>
            </Link>
          )}
          {user.twitter && (
            <Link href={user.twitter} target="_blank" rel="noopener noreferrer">
              <Button
                display="flex"
                alignItems="center"
                gap={2}
                colorScheme="twitter"
                variant="outline"
              >
                <FaTwitter />
                Twitter
              </Button>
            </Link>
          )}
        </HStack>
      </VStack>

      <ChakraDivider my={6} />

      <Grid templateColumns={{ base: '1fr', md: 'repeat(2, 1fr)' }} gap={6}>
        <GridItem>
          <Text fontSize="lg" fontWeight="semibold">
            Location
          </Text>
          <Text color="gray.600">{user.location || 'Not specified'}</Text>
        </GridItem>
        <GridItem>
          <Text fontSize="lg" fontWeight="semibold">
            Company
          </Text>
          <Text color="gray.600">{user.company || 'Not specified'}</Text>
        </GridItem>
      </Grid>
    </Box>
  )
}

export default UserDetailsPage
