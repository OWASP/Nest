import { UserCardProps } from "lib/constants"

const UserCard: React.FC<UserCardProps> = ({ avatar, name, company, button }) => {
  return (
    <div className="bg-white shadow-md rounded-lg overflow-hidden p-4 my-2 flex flex-col items-center justify-center w-64 h-64">
      <div className="w-16 h-16 mb-4">
        <img
          src={avatar}
          alt={`${name} Avatar`}
          className="w-16 h-16 rounded-full object-cover"
        />
      </div>
      <div className="text-center">
        <h3 className="text-xl font-semibold">{name}</h3>
        <p className="text-gray-600">{company}</p>
      </div>
      <div className="mt-auto">
        <button
          onClick={button.onclick}
          className="bg-blue-500 text-white rounded-md py-2 px-4 flex items-center"
        >
          {button.icon}
          <span className="ml-2">{button.label}</span>
        </button>
      </div>
    </div>
  )
}

export default UserCard
