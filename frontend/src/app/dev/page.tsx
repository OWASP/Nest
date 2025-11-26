'use client'
import React, { useState } from 'react'
import ProgramActions from 'components/ProgramActions'
import { ProgramStatusEnum } from 'types/__generated__/graphql'

export default function DevProgramActionsPage() {
  const [status, setStatus] = useState<ProgramStatusEnum>(ProgramStatusEnum.Draft)

  return (
    <div className="min-h-screen p-8 bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100">
      <h1 className="mb-4 text-2xl font-bold">Dev: ProgramActions</h1>

      <p className="mb-4">
        Current status: <strong data-testid="current-status">{status}</strong>
      </p>

      <div className="mb-6">
        <ProgramActions status={status} setStatus={(s) => setStatus(s)} />
      </div>

      <p className="text-sm text-gray-600 dark:text-gray-400">
        Tip: Use Tab to focus the actions button, then Enter or Space to open the menu. Use Enter/Space
        to activate menu items.
      </p>
    </div>
  )
}