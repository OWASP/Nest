export default function TestCard() {
  return (
    <div className="bg-background text-foreground mx-auto mt-10 max-w-sm rounded-lg border p-6 shadow-sm">
      <h2 className="mb-3 text-xl font-bold">Tailwind Theme Test</h2>
      <p className="text-muted-foreground mb-4">
        If you can read this with correct colors, your Tailwind theme is working 🎉
      </p>
      <button className="bg-primary text-primary-foreground hover:bg-primary/80 rounded-md px-4 py-2">
        Test Button
      </button>
    </div>
  )
}
