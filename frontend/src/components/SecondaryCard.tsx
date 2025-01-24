const SecondaryCard = ({ title, children, className = '' }) => (
  <div className={`mb-8 rounded-lg bg-gray-100 p-6 shadow-md dark:bg-gray-800 ${className}`}>
    <h2 className="mb-4 text-2xl font-semibold">{title}</h2>
    {children}
  </div>
)

export default SecondaryCard
