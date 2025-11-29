'use client';

import React from 'react'
import ModuleList from 'components/ModuleList'

export default function DevModuleListPage() {
  const lessThan5 = ['Module 1', 'Module 2', 'Module 3']
  const exactly5 = ['Module 1', 'Module 2', 'Module 3', 'Module 4', 'Module 5']
  const manyModules = Array.from({ length: 8 }, (_, i) => `Module ${i + 1}`)
  const sixModules = Array.from({ length: 6 }, (_, i) => `Module ${i + 1}`)
  const longModule = [
    'This is a very long module name that exceeds fifty characters and should be truncated',
  ]
  const emptyStrings = ['', 'Valid Module', '']

  // show empty / undefined / null cases (cast to any to allow rendering in dev)
  const undefinedModules = undefined as any
  const nullModules = null as any
  const emptyArray: string[] = []

  return (
    <main className="min-h-screen p-8 bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100">
      <h1 className="mb-4 text-2xl font-bold">Dev: ModuleList</h1>
      <p className="mb-6 text-sm text-gray-600 dark:text-gray-400">
        Use Tab + Enter/Space to test keyboard activation and focus rings. This page renders the
        same scenarios covered by the unit tests.
      </p>

      <section className="mb-8">
        <h2 className="mb-2 font-semibold">Less than 5 modules</h2>
        <ModuleList modules={lessThan5} />
      </section>

      <section className="mb-8">
        <h2 className="mb-2 font-semibold">Exactly 5 modules</h2>
        <ModuleList modules={exactly5} />
      </section>

      <section className="mb-8">
        <h2 className="mb-2 font-semibold">More than 5 modules (8 items)</h2>
        <ModuleList modules={manyModules} />
      </section>

      <section className="mb-8">
        <h2 className="mb-2 font-semibold">Edge case: exactly 6 modules</h2>
        <ModuleList modules={sixModules} />
      </section>

      <section className="mb-8">
        <h2 className="mb-2 font-semibold">Long module name (truncation)</h2>
        <ModuleList modules={longModule} />
      </section>

      <section className="mb-8">
        <h2 className="mb-2 font-semibold">Modules with empty strings</h2>
        <ModuleList modules={emptyStrings} />
      </section>

      <section className="mb-8">
        <h2 className="mb-2 font-semibold">Empty / undefined / null (should render nothing)</h2>
        <div className="space-y-4">
          <div>
            <div className="mb-1 text-sm text-gray-500">Empty array</div>
            <ModuleList modules={emptyArray} />
          </div>
          <div>
            <div className="mb-1 text-sm text-gray-500">Undefined (dev cast)</div>
            <ModuleList modules={undefinedModules} />
          </div>
          <div>
            <div className="mb-1 text-sm text-gray-500">Null (dev cast)</div>
            <ModuleList modules={nullModules} />
          </div>
        </div>
      </section>
    </main>
  )
}