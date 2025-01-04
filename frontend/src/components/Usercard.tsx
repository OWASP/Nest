import { UserCardProps } from 'lib/constants'

const UserCard = ({ avatar, name, company, button }: UserCardProps) => {
  return (
    <div className="my-2 flex h-64 w-64 flex-col items-center justify-center overflow-hidden rounded-lg bg-white p-4 shadow-md">
      <div className="mb-4 h-16 w-16">
        <img src={avatar} alt={`${name} Avatar`} className="h-16 w-16 rounded-full object-cover" />
      </div>
      <div className="text-center">
        <h3 className="text-xl font-semibold">{name}</h3>
        <p className="text-gray-600">{company}</p>
      </div>
      <div className="mt-auto">
        <button
          onClick={button.onclick}
          className="flex items-center rounded-md bg-blue-500 px-4 py-2 text-white"
        >
          {button.icon}
          <span className="ml-2">{button.label}</span>
        </button>
      </div>
    </div>
  )
}

export default UserCard
