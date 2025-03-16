import React from 'react'

interface SnapshotCardProps {
  title: string
  startAt: string
  endAt: string
  button: {
    label: string
    icon: React.ReactNode
    onclick: () => void
  }
}

const SnapshotCard: React.FC<SnapshotCardProps> = ({ title, startAt, endAt, button }) => {
  return (
    <div className="card">
      <h3>{title}</h3>
      <p>{startAt} - {endAt}</p>
      <button onClick={button.onclick}>
        {button.icon} {button.label}
      </button>
    </div>
  )
}

export default SnapshotCard
