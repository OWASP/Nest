import { faPersonWalkingArrowRight } from '@fortawesome/free-solid-svg-icons'
import { useRouter } from 'next/navigation'
import React from 'react'
import FontAwesomeIconWrapper from 'wrappers/FontAwesomeIconWrapper'
import type { Leader } from 'types/leader'
import AnchorTitle from 'components/AnchorTitle'
import SecondaryCard from 'components/SecondaryCard'
import UserCard from 'components/UserCard'

interface LeadersProps {
  users: Leader[]
}

const Leaders: React.FC<LeadersProps> = ({ users }) => {
  const router = useRouter()

  const handleButtonClick = (user: Leader) => {
    if (user.member) {
      router.push(`/members/${user.member.login}`)
    } else {
      router.push(`/members?q=${encodeURIComponent(user.memberName)}`)
    }
  }

  return (
    <SecondaryCard icon={faPersonWalkingArrowRight} title={<AnchorTitle title="Leaders" />}>
      <div className="flex w-full flex-col items-center justify-around overflow-hidden md:flex-row">
        {users.map((user) => (
          <UserCard
            key={user.member?.login || user.memberName}
            avatar={user.member?.avatarUrl}
            button={{
              icon: <FontAwesomeIconWrapper icon="fa-solid fa-right-to-bracket" />,
              label: 'View Profile',
              onclick: () => handleButtonClick(user),
            }}
            className="h-64 w-42 bg-inherit"
            description={user.description}
            name={user.member?.name || user.memberName}
          />
        ))}
      </div>
    </SecondaryCard>
  )
}

export default Leaders
