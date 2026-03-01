import { useRouter } from 'next/navigation'
import React from 'react'
import { FaPersonWalkingArrowRight, FaRightToBracket } from 'react-icons/fa6'
import { IconWrapper } from 'wrappers/IconWrapper'
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
    <SecondaryCard icon={FaPersonWalkingArrowRight} title={<AnchorTitle title="Leaders" />}>
      <div className="flex w-full flex-wrap items-stretch justify-center gap-4 p-2">
        {users.map((user) => (
          <UserCard
            key={user.member?.login || user.memberName}
            avatar={user.member?.avatarUrl || ''}
            button={{
              icon: <IconWrapper icon={FaRightToBracket} />,
              label: 'View Profile',
              onclick: () => handleButtonClick(user),
            }}
            className="h-auto w-full max-w-[280px] bg-inherit"
            description={user.description}
            name={user.member?.name || user.memberName}
          />
        ))}
      </div>
    </SecondaryCard>
  )
}

export default Leaders
