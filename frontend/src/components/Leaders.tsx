import { faPersonWalkingArrowRight, faRightToBracket } from '@fortawesome/free-solid-svg-icons'
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
      <div className="grid w-full grid-cols-[repeat(auto-fit,minmax(220px,1fr))] justify-items-center gap-6 p-4">
        {users.map((user) => (
          <UserCard
            key={user.member?.login || user.memberName}
            avatar={user.member?.avatarUrl}
            button={{
              icon: <FontAwesomeIconWrapper icon={faRightToBracket} />,
              label: 'View Profile',
              onclick: () => handleButtonClick(user),
            }}
            className="w-full max-w-[280px] bg-inherit"
            description={user.description}
            name={user.member?.name || user.memberName}
          />
        ))}
      </div>
    </SecondaryCard>
  )
}

export default Leaders
