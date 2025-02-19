import { Avatar, Box, Button, Divider, Flex, Grid, GridItem, HStack, Link, Text, VStack } from "@chakra-ui/react";
import { FaGithub, FaLinkedin, FaTwitter } from "react-icons/fa";

const UserDetailsPage = ({ user }) => {
  return (
    <Box maxW="4xl" mx="auto" p={6}>
      <Flex alignItems="center" justifyContent="center" direction="column">
        <Avatar size="2xl" name={user.name} src={user.avatarUrl} mb={4} />
        <Text fontSize="2xl" fontWeight="bold">{user.name}</Text>
        <Text fontSize="md" color="gray.500">{user.email}</Text>
      </Flex>

      <Divider my={6} />

      <VStack spacing={4} align="start">
        <Text fontSize="lg" fontWeight="semibold">Bio</Text>
        <Text color="gray.600">{user.bio}</Text>
      </VStack>

      <Divider my={6} />

      <VStack spacing={4} align="start">
        <Text fontSize="lg" fontWeight="semibold">Social Links</Text>
        <HStack spacing={4}>
          {user.github && (
            <Link href={user.github} isExternal>
              <Button leftIcon={<FaGithub />} colorScheme="gray" variant="outline">GitHub</Button>
            </Link>
          )}
          {user.linkedin && (
            <Link href={user.linkedin} isExternal>
              <Button leftIcon={<FaLinkedin />} colorScheme="blue" variant="outline">LinkedIn</Button>
            </Link>
          )}
          {user.twitter && (
            <Link href={user.twitter} isExternal>
              <Button leftIcon={<FaTwitter />} colorScheme="twitter" variant="outline">Twitter</Button>
            </Link>
          )}
        </HStack>
      </VStack>

      <Divider my={6} />

      <Grid templateColumns={{ base: "1fr", md: "repeat(2, 1fr)" }} gap={6}>
        <GridItem>
          <Text fontSize="lg" fontWeight="semibold">Location</Text>
          <Text color="gray.600">{user.location || "Not specified"}</Text>
        </GridItem>
        <GridItem>
          <Text fontSize="lg" fontWeight="semibold">Company</Text>
          <Text color="gray.600">{user.company || "Not specified"}</Text>
        </GridItem>
      </Grid>
    </Box>
  );
};

export default UserDetailsPage;
